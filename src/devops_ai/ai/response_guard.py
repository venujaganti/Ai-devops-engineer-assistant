from src.devops_ai.core.exceptions import GeminiServiceError


MAX_RESPONSE_CHARACTERS = 30000


def validate_response(text: str | None) -> str:
    if not isinstance(text, str) or not text.strip():
        raise GeminiServiceError(
            "Gemini returned an empty response. Please retry."
        )

    cleaned = text.strip()

    if len(cleaned) > MAX_RESPONSE_CHARACTERS:
        cleaned = (
            cleaned[:MAX_RESPONSE_CHARACTERS].rstrip()
            + "\n\n[Response shortened by the application.]"
        )

    return cleaned