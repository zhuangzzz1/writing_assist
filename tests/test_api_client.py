import json

import pytest
import requests

from agents.utils import (
    MAX_DRAFT_CHARS,
    APIError,
    AuthError,
    ConfigurationError,
    DeepSeekClient,
    InputValidationError,
    RateLimitError,
    ResponseValidationError,
    parse_json_object,
    validate_context_input,
    validate_writing_input,
)


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self.payload = payload or {"choices": [{"message": {"content": "ok"}}]}

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, response=None, error=None):
        self.response = response or FakeResponse()
        self.error = error
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if self.error:
            raise self.error
        return self.response


def make_client(session, thinking=True):
    return DeepSeekClient("test-key", session=session, thinking=thinking)


def test_thinking_json_request_omits_temperature_and_records_authorized_metadata():
    payload = {
        "id": "request-1",
        "created": 123,
        "model": "deepseek-flash",
        "choices": [{"message": {"content": "ok", "reasoning_content": "never capture this"}}],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
            "completion_tokens_details": {"reasoning_tokens": 8},
        },
    }
    session = FakeSession(FakeResponse(payload=payload))
    client = make_client(session, thinking=True)

    result = client.chat_completion([{"role": "user", "content": "test"}], json_mode=True)

    assert result == "ok"
    request = session.calls[0][1]["json"]
    assert request["thinking"] == {"type": "enabled"}
    assert request["reasoning_effort"] == "high"
    assert request["response_format"] == {"type": "json_object"}
    assert "temperature" not in request
    assert client.last_response_metadata["token_usage"]["reasoning_tokens"] == 8
    assert "reasoning_content" not in json.dumps(client.last_response_metadata)


def test_explicit_nonthinking_baseline_uses_temperature_zero():
    session = FakeSession()

    make_client(session, thinking=False).chat_completion(
        [{"role": "user", "content": "baseline"}], temperature=0.7
    )

    payload = session.calls[0][1]["json"]
    assert payload["thinking"] == {"type": "disabled"}
    assert payload["temperature"] == 0.7
    assert "reasoning_effort" not in payload


def test_thinking_request_can_be_explicitly_disabled_only_by_caller():
    session = FakeSession()
    client = make_client(session, thinking=True)

    client.chat_completion([], thinking=False)

    assert session.calls[0][1]["json"]["thinking"] == {"type": "disabled"}


def test_runtime_environment_uses_nonthinking_by_default(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test")
    monkeypatch.setenv("DEEPSEEK_THINKING", "false")

    client = DeepSeekClient.from_env()

    assert client.thinking is False


def test_thinking_requirement_is_explicit_not_a_runtime_fallback(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test")
    monkeypatch.setenv("DEEPSEEK_THINKING", "false")

    with pytest.raises(ConfigurationError, match="controlled evaluation"):
        DeepSeekClient.from_env(require_thinking=True)


def test_controlled_evaluation_can_opt_into_nonthinking(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test")
    monkeypatch.setenv("DEEPSEEK_THINKING", "false")

    client = DeepSeekClient.from_env(require_thinking=False)

    assert client.thinking is False


@pytest.mark.parametrize(
    ("status_code", "exception_type"),
    [(401, AuthError), (403, AuthError), (429, RateLimitError), (500, APIError)],
)
def test_http_errors_are_categorized(status_code, exception_type):
    session = FakeSession(FakeResponse(status_code=status_code))

    with pytest.raises(exception_type):
        make_client(session).chat_completion([])


def test_thinking_http_error_is_explicit():
    response = FakeResponse(
        status_code=400, payload={"error": {"message": "thinking is unavailable"}}
    )

    with pytest.raises(APIError, match="Thinking-mode request was not accepted"):
        make_client(FakeSession(response)).chat_completion([])


def test_timeout_is_categorized():
    session = FakeSession(error=requests.exceptions.Timeout())

    with pytest.raises(APIError, match="timed out"):
        make_client(session).chat_completion([])


def test_unexpected_response_is_categorized():
    session = FakeSession(FakeResponse(payload={"choices": []}))

    with pytest.raises(APIError, match="unexpected response"):
        make_client(session).chat_completion([])


def test_parse_json_object():
    assert parse_json_object('{"route": "support_agent"}') == {"route": "support_agent"}


@pytest.mark.parametrize("fence", ["json", "JSON", "Json"])
def test_parse_json_object_accepts_fenced_json(fence):
    content = f'```{fence}\n{{"route": "direct_response"}}\n```'

    assert parse_json_object(content)["route"] == "direct_response"


@pytest.mark.parametrize("content", ["not json", "[]", '"text"'])
def test_parse_json_object_rejects_malformed_values(content):
    with pytest.raises(ResponseValidationError):
        parse_json_object(content)


def test_input_validation_rejects_empty_and_preserves_text():
    assert validate_writing_input("  short  ") == "  short  "
    with pytest.raises(InputValidationError):
        validate_writing_input("  \n ")


def test_draft_length_limit_is_explicit_and_never_truncates():
    too_long = "x" * (MAX_DRAFT_CHARS + 1)

    with pytest.raises(InputValidationError, match="Nothing was truncated"):
        validate_writing_input(too_long)


def test_context_length_limit_is_explicit():
    with pytest.raises(InputValidationError, match="nothing was truncated"):
        validate_context_input("x" * 11, "Source material", 10)


@pytest.mark.parametrize("value", ["yes", "1", ""])
def test_thinking_configuration_rejects_ambiguous_values(monkeypatch, value):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test")
    monkeypatch.setenv("DEEPSEEK_THINKING", value)

    with pytest.raises(ConfigurationError, match="true or false"):
        DeepSeekClient.from_env()


@pytest.mark.parametrize("value", ["0", "-1", "abc", "nan", "inf"])
def test_timeout_configuration_must_be_positive_and_finite(monkeypatch, value):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test")
    monkeypatch.setenv("DEEPSEEK_THINKING", "false")
    monkeypatch.setenv("DEEPSEEK_TIMEOUT_SECONDS", value)

    with pytest.raises(ConfigurationError, match="positive number"):
        DeepSeekClient.from_env()


def test_response_metadata_is_isolated_between_threads():
    import threading
    from concurrent.futures import ThreadPoolExecutor

    client = DeepSeekClient("test-key")
    barrier = threading.Barrier(2)

    def write_and_read(request_id):
        client.last_response_metadata = {"provider_request_id": request_id}
        barrier.wait()
        return client.last_response_metadata["provider_request_id"]

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(write_and_read, ("first", "second")))

    assert results == ["first", "second"]
