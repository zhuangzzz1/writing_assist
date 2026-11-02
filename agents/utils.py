import json
import os
from typing import Any

import requests
from dotenv import load_dotenv


class WritingAssistantError(Exception):
    pass


class ConfigurationError(WritingAssistantError):
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
        timeout: float = 30,
        thinking: bool = False,
        session: requests.Session | None = None,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.thinking = thinking
        self.session = session or requests.Session()

    @classmethod
    def from_env(cls) -> "DeepSeekClient":
        load_dotenv()
        api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        if not api_key:
            raise ConfigurationError(
                "DEEPSEEK_API_KEY is missing. Add it to .env before running an analysis."
            )
        thinking = os.getenv("DEEPSEEK_THINKING", "false").strip().lower() == "true"
        return cls(
            api_key=api_key,
            base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com"),
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-flash"),
            thinking=thinking,
        )

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 2000,
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
            payload["reasoning_effort"] = "high"
        else:
            payload["temperature"] = temperature
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

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

        if response.status_code == 401:
            raise AuthError("DeepSeek authentication failed.", status_code=401)
        if response.status_code == 429:
            raise RateLimitError("DeepSeek rate limit reached.", status_code=429)
        if response.status_code >= 400:
            raise APIError(
                f"DeepSeek returned HTTP {response.status_code}.",
                status_code=response.status_code,
            )

        try:
            body = response.json()
            content = body["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise APIError("DeepSeek returned an unexpected response format.") from exc
        if not isinstance(content, str) or not content.strip():
            raise APIError("DeepSeek returned an empty response.")
        return content


def parse_json_object(content: str) -> dict[str, Any]:
    stripped = content.strip()
    if stripped.startswith("```json") and stripped.endswith("```"):
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


def validate_writing_input(writing: str) -> str:
    if not writing.strip():
        raise InputValidationError("Enter some writing before starting an analysis.")
    return writing
