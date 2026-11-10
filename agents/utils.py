import json
import math
import os
import re
from contextvars import ContextVar
from typing import Any

import requests
from dotenv import load_dotenv


PROMPT_VERSION = "v3.3.0"
SCHEMA_VERSION = "v3.2.1"
MAX_DRAFT_CHARS = 16_000
MAX_SOURCE_CHARS = 16_000
MAX_ASSIGNMENT_CHARS = 4_000
MAX_DIRECTIONS_CHARS = 4_000
MAX_CONCERNS_CHARS = 2_000


PROHIBITED_CLAIMS = re.compile(
    r"\b(?:ready to submit|ready for submission|good enough to turn in|"
    r"mastered|mastery of|official sbac score|predicted elpac|"
    r"reclassification recommendation)\b",
    re.IGNORECASE,
)
NUMERICAL_SCORE = re.compile(
    r"\b(?:score|rubric rating)\s*(?::|=|\bis\b|\bwas\b)?\s*"
    r"\d+(?:\s*/\s*\d+)?\b",
    re.IGNORECASE,
)
UNVERIFIABLE_SOURCE_CLAIM = re.compile(
    r"\b(?:quotation|quote|statistic|evidence|paraphrase|citation|fact)\s+"
    r"(?:is|looks|seems|appears)\s+(?:accurate|correct|reasonable|faithful)\b|"
    r"\bcorrectly represents (?:the|its) source\b",
    re.IGNORECASE,
)


def ensure_bounded_language(value: Any, source_material_available: bool) -> None:
    if isinstance(value, dict):
        for item in value.values():
            ensure_bounded_language(item, source_material_available)
        return
    if isinstance(value, list):
        for item in value:
            ensure_bounded_language(item, source_material_available)
        return
    if not isinstance(value, str):
        return
    if PROHIBITED_CLAIMS.search(value) or NUMERICAL_SCORE.search(value):
        raise ValueError(
            "Student-facing text contains a prohibited score, mastery, or readiness claim."
        )
    if not source_material_available and UNVERIFIABLE_SOURCE_CLAIM.search(value):
        raise ValueError("Source accuracy cannot be asserted without supplied source material.")


class WritingAssistantError(Exception):
    pass


class ConfigurationError(WritingAssistantError):
    pass


class StorageError(WritingAssistantError):
    pass


class APIError(WritingAssistantError):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class RateLimitError(APIError):
    pass


class AuthError(APIError):
    pass


class InputValidationError(WritingAssistantError):
    pass


class ResponseValidationError(WritingAssistantError):
    pass


class DeepSeekClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.deepseek.com",
        model: str = "deepseek-flash",
        timeout: float = 120,
        thinking: bool = True,
        reasoning_effort: str = "high",
        session: requests.Session | None = None,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.thinking = thinking
        self.reasoning_effort = reasoning_effort
        self.session = session or requests.Session()
        self._response_metadata: ContextVar[dict[str, Any]] = ContextVar(
            "deepseek_response_metadata"
        )

    @property
    def last_response_metadata(self) -> dict[str, Any]:
        return self._response_metadata.get({})

    @last_response_metadata.setter
    def last_response_metadata(self, value: dict[str, Any]) -> None:
        self._response_metadata.set(value)

    @classmethod
    def from_env(cls, require_thinking: bool = False) -> "DeepSeekClient":
        load_dotenv()
        api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        if not api_key:
            raise ConfigurationError(
                "DEEPSEEK_API_KEY is missing. Add it to .env before running a review."
            )
        thinking_value = os.getenv("DEEPSEEK_THINKING", "false").strip().lower()
        if thinking_value not in ("true", "false"):
            raise ConfigurationError("DEEPSEEK_THINKING must be true or false.")
        thinking = thinking_value == "true"
        if require_thinking and not thinking:
            raise ConfigurationError(
                "This controlled evaluation requires DEEPSEEK_THINKING=true. "
                "Enable it explicitly for that run; no automatic mode switch is allowed."
            )
        try:
            timeout = float(os.getenv("DEEPSEEK_TIMEOUT_SECONDS", "120"))
        except ValueError as exc:
            raise ConfigurationError(
                "DEEPSEEK_TIMEOUT_SECONDS must be a positive number."
            ) from exc
        if not math.isfinite(timeout) or timeout <= 0:
            raise ConfigurationError("DEEPSEEK_TIMEOUT_SECONDS must be a positive number.")
        return cls(
            api_key=api_key,
            base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com"),
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-flash"),
            timeout=timeout,
            thinking=thinking,
            reasoning_effort=os.getenv("DEEPSEEK_REASONING_EFFORT", "high").strip(),
        )

    def model_config(self) -> dict[str, Any]:
        return {
            "model_name": self.model,
            "thinking_enabled": self.thinking,
            "reasoning_effort": self.reasoning_effort if self.thinking else "",
            "prompt_version": PROMPT_VERSION,
            "schema_version": SCHEMA_VERSION,
        }

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 8000,
        json_mode: bool = False,
        thinking: bool | None = None,
    ) -> str:
        use_thinking = self.thinking if thinking is None else thinking
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "thinking": {"type": "enabled" if use_thinking else "disabled"},
        }
        if use_thinking:
            payload["reasoning_effort"] = self.reasoning_effort
        else:
            payload["temperature"] = temperature
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        self.last_response_metadata = {}
        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout as exc:
            raise APIError("The DeepSeek request timed out.") from exc
        except requests.exceptions.ConnectionError as exc:
            raise APIError("Could not connect to DeepSeek.") from exc
        except requests.exceptions.RequestException as exc:
            raise APIError("The DeepSeek request failed.") from exc

        if response.status_code in (401, 403):
            raise AuthError(
                "DeepSeek authentication failed.", status_code=response.status_code
            )
        if response.status_code == 429:
            raise RateLimitError("DeepSeek rate limit reached.", status_code=429)
        if response.status_code >= 400:
            detail = ""
            try:
                error_body = response.json()
                detail = str(error_body.get("error", {}).get("message", ""))[:500]
            except (ValueError, AttributeError):
                detail = ""
            message = f"DeepSeek returned HTTP {response.status_code}."
            if use_thinking and detail:
                message += f" Thinking-mode request was not accepted: {detail}"
            raise APIError(message, status_code=response.status_code)

        try:
            body = response.json()
            message = body["choices"][0]["message"]
            content = message["content"]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise APIError("DeepSeek returned an unexpected response format.") from exc
        if not isinstance(content, str) or not content.strip():
            raise APIError("DeepSeek returned an empty response.")
        usage = body.get("usage") if isinstance(body.get("usage"), dict) else {}
        completion_details = (
            usage.get("completion_tokens_details")
            if isinstance(usage.get("completion_tokens_details"), dict)
            else {}
        )
        self.last_response_metadata = {
            "provider_request_id": str(body.get("id", "")),
            "provider_created": body.get("created"),
            "model_name": str(body.get("model", self.model)),
            "thinking_enabled": use_thinking,
            "reasoning_effort": self.reasoning_effort if use_thinking else "",
            "token_usage": {
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens"),
                "reasoning_tokens": completion_details.get("reasoning_tokens"),
            },
        }
        return content


def parse_json_object(content: str) -> dict[str, Any]:
    stripped = content.strip()
    if stripped.lower().startswith("```json") and stripped.endswith("```"):
        stripped = stripped[7:-3].strip()
    elif stripped.startswith("```") and stripped.endswith("```"):
        stripped = stripped[3:-3].strip()
    try:
        value = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise ResponseValidationError("The model did not return valid JSON.") from exc
    if not isinstance(value, dict):
        raise ResponseValidationError("The model response must be a JSON object.")
    return value


def validate_writing_input(writing: str, label: str = "draft") -> str:
    if not writing.strip():
        raise InputValidationError(f"Enter some writing in the {label} before continuing.")
    if len(writing) > MAX_DRAFT_CHARS:
        raise InputValidationError(
            f"The {label} is {len(writing):,} characters. The limit is "
            f"{MAX_DRAFT_CHARS:,}; shorten it before review. Nothing was truncated."
        )
    return writing


def validate_context_input(value: str, label: str, limit: int) -> str:
    if len(value) > limit:
        raise InputValidationError(
            f"{label} is {len(value):,} characters. The limit is {limit:,}. "
            "Shorten it before review; nothing was truncated."
        )
    return value
