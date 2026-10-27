import os

import pytest

from src.devops_ai.ai.gemini_client import GeminiClient
from src.devops_ai.core.exceptions import DevOpsAssistantError


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_GEMINI_LIVE_TESTS") != "1",
    reason="Set RUN_GEMINI_LIVE_TESTS=1 to enable live API tests.",
)


def test_live_gemini_response():
    assistant = GeminiClient()

    try:
        response = assistant.generate_reply(
            "Reply with exactly: GEMINI_CONNECTION_OK"
        )
    except DevOpsAssistantError as exc:
        pytest.fail(f"Gemini integration failed: {exc}")

    assert isinstance(response, str)
    assert response.strip()
    assert len(response) <= 30000