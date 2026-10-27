import logging
import math

try:
    from google import genai
    from google.genai import types
except ImportError:  # Defer SDK requirement until a real API client is needed.
    from types import SimpleNamespace

    genai = None
    types = SimpleNamespace(HttpOptions=lambda **kwargs: kwargs)

from config.settings import get_settings
from src.devops_ai.core.exceptions import (
    GeminiConfigurationError,
    GeminiServiceError,
)

logger = logging.getLogger(__name__)


class GeminiEmbeddings:
    def __init__(self, client=None, settings=None):
        self.settings = settings or get_settings()

        if client is None:
            if not self.settings.gemini_api_key:
                raise GeminiConfigurationError(
                    "Gemini API key is not configured"
                )

            if genai is None:
                raise GeminiServiceError(
                    "The google-genai SDK is not installed. Install requirements.txt."
                )
            client = genai.Client(
                api_key=self.settings.gemini_api_key,
                http_options=types.HttpOptions(timeout=30000),
            )

        self.client = client

    def embed(self, text: str) -> list[float]:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Embedding text must not be empty")

        try:
            response = self.client.models.embed_content(
                model=self.settings.gemini_embedding_model,
                contents=text,
            )

            if not response.embeddings:
                raise GeminiServiceError(
                    "Embedding service returned no vectors"
                )

            values = response.embeddings[0].values

            if not values:
                raise GeminiServiceError(
                    "Embedding service returned an empty vector"
                )

            vector = [float(value) for value in values]

            if not all(math.isfinite(value) for value in vector):
                raise GeminiServiceError(
                    "Embedding service returned invalid values"
                )

            return vector

        except GeminiServiceError:
            raise
        except Exception as exc:
            logger.warning(
                "Embedding request failed: %s",
                type(exc).__name__,
            )
            raise GeminiServiceError(
                "Could not generate document embeddings"
            ) from None