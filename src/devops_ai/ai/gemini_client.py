import logging
from collections.abc import Sequence
from typing import Any

try:
    from google import genai
    from google.genai import types
except ImportError:  # Keep deterministic unit tests usable without the optional SDK.
    from dataclasses import dataclass
    from types import SimpleNamespace

    genai = None

    @dataclass
    class _Part:
        text: str

        @classmethod
        def from_text(cls, *, text: str):
            return cls(text=text)

    @dataclass
    class _Content:
        role: str
        parts: list[_Part]

    types = SimpleNamespace(
        Content=_Content,
        Part=_Part,
        GenerateContentConfig=lambda **kwargs: SimpleNamespace(**kwargs),
    )

from config.settings import Settings, get_settings
from src.devops_ai.ai.prompts import SYSTEM_INSTRUCTION
from src.devops_ai.ai.response_guard import validate_response
from src.devops_ai.core.exceptions import (
    GeminiConfigurationError,
    GeminiServiceError,
)

logger = logging.getLogger(__name__)

MAX_PROMPT_CHARACTERS = 12000


class GeminiClient:
    def __init__(
        self,
        settings: Settings | None = None,
        client: Any | None = None,
    ) -> None:
        self.settings = settings or get_settings()

        if not self.settings.gemini_model:
            raise GeminiConfigurationError(
                "Set GEMINI_MODEL in your local environment."
            )

        self._client = client

        if self._client is None:
            if not self.settings.gemini_api_key:
                raise GeminiConfigurationError(
                    "Gemini API key is missing. Configure GEMINI_API_KEY "
                    "in your local environment."
                )

            try:
                if genai is None:
                    raise RuntimeError("google-genai SDK is not installed")
                self._client = genai.Client(
                    api_key=self.settings.gemini_api_key
                )
            except Exception as exc:
                logger.warning(
                    "Gemini client initialization failed: %s",
                    type(exc).__name__,
                )
                raise GeminiServiceError(
                    "Unable to initialize Gemini. Check your SDK "
                    "installation and local configuration."
                ) from None

    def generate_reply(
        self,
        message: str,
        history: Sequence[dict[str, str]] | None = None,
    ) -> str:
        if not isinstance(message, str) or not message.strip():
            raise GeminiConfigurationError(
                "Enter a non-empty DevOps question."
            )

        if len(message) > MAX_PROMPT_CHARACTERS:
            raise GeminiConfigurationError(
                f"Your question exceeds the "
                f"{MAX_PROMPT_CHARACTERS}-character limit."
            )

        contents: list[types.Content] = []

        recent_history = list(history or [])[
            -(self.settings.gemini_max_history_messages - 1):
        ]

        for item in recent_history:
            role = item.get("role")
            content = item.get("content", "")

            if role not in {"user", "assistant", "model"}:
                continue

            if not isinstance(content, str) or not content.strip():
                continue

            if len(content) > MAX_PROMPT_CHARACTERS:
                continue

            api_role = "model" if role in {"assistant", "model"} else "user"

            contents.append(
                types.Content(
                    role=api_role,
                    parts=[types.Part.from_text(text=content)],
                )
            )

        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=message.strip())],
            )
        )

        generation_config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=self.settings.gemini_temperature,
            max_output_tokens=self.settings.gemini_max_output_tokens,
        )

        try:
            response = self._client.models.generate_content(
                model=self.settings.gemini_model,
                contents=contents,
                config=generation_config,
            )

            return validate_response(response.text)

        except GeminiServiceError:
            raise
        except Exception as exc:
            # Do not log the exception text: provider errors can contain
            # request details that should not be written to application logs.
            logger.warning(
                "Gemini request failed with exception type %s",
                type(exc).__name__,
            )
            raise GeminiServiceError(
                "Gemini could not complete the request. Check model "
                "availability, API quota, connectivity, and credentials. "
                "Details were not included to protect sensitive data."
            ) from None