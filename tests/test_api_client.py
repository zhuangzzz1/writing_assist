import json

import pytest
import requests

from agents.utils import (
    APIError,
    AuthError,
    DeepSeekClient,
    InputValidationError,
    RateLimitError,
    ResponseValidationError,
    parse_json_object,
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


def make_client(session, thinking=False):
    return DeepSeekClient("test-key", session=session, thinking=thinking)


def test_non_thinking_json_request_uses_temperature_zero():
    session = FakeSession()
    result = make_client(session).chat_completion(
        [{"role": "user", "content": "test"}], json_mode=True
    )

    assert result == "ok"
    payload = session.calls[0][1]["json"]
    assert payload["model"] == "deepseek-flash"
    assert payload["temperature"] == 0.0
    assert payload["thinking"] == {"type": "disabled"}
    assert payload["response_format"] == {"type": "json_object"}


def test_thinking_request_omits_temperature():
    session = FakeSession()
    make_client(session, thinking=True).chat_completion(
        [{"role": "user", "content": "test"}], temperature=0.7
    )

    payload = session.calls[0][1]["json"]
    assert "temperature" not in payload
    assert payload["thinking"] == {"type": "enabled"}
    assert payload["reasoning_effort"] == "high"


@pytest.mark.parametrize(
    ("status_code", "exception_type"),
    [(401, AuthError), (429, RateLimitError), (500, APIError)],
)
def test_http_errors_are_categorized(status_code, exception_type):
    session = FakeSession(FakeResponse(status_code=status_code))
    with pytest.raises(exception_type):
        make_client(session).chat_completion([])


def test_timeout_is_categorized():
    session = FakeSession(error=requests.exceptions.Timeout())
    with pytest.raises(APIError, match="timed out"):
        make_client(session).chat_completion([])


def test_unexpected_response_is_categorized():
    session = FakeSession(FakeResponse(payload={"choices": []}))
    with pytest.raises(APIError, match="unexpected response"):
        make_client(session).chat_completion([])


def test_parse_json_object_and_fenced_json():
    assert parse_json_object('{"route": "support_agent"}') == {"route": "support_agent"}
    assert parse_json_object('```json\n{"route": "direct_response"}\n```') == {
        "route": "direct_response"
    }


@pytest.mark.parametrize("content", ["not json", "[]", '"text"'])
def test_parse_json_object_rejects_malformed_values(content):
    with pytest.raises(ResponseValidationError):
        parse_json_object(content)


def test_input_validation_rejects_only_empty_input_and_preserves_text():
    assert validate_writing_input("  short  ") == "  short  "
    with pytest.raises(InputValidationError):
        validate_writing_input("  \n ")
