from types import SimpleNamespace

import pytest

from config.settings import get_settings
from src.devops_ai.ai.gemini_client import GeminiClient
from src.devops_ai.core.exceptions import (
    GeminiConfigurationError,
    GeminiServiceError,
)


class FakeModels:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)

        if self.error:
            raise self.error

        return self.response


class FakeClient:
    def __init__(self, models):
        self.models = models


def make_settings(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-not-real")
    monkeypatch.setenv("GEMINI_MODEL", "test-model")
    monkeypatch.setenv("GEMINI_MAX_HISTORY_MESSAGES", "12")
    return get_settings()


def test_generate_reply_returns_response(monkeypatch):
    settings = make_settings(monkeypatch)
    models = FakeModels(
        response=SimpleNamespace(text="Use kubectl describe pod.")
    )
    client = GeminiClient(
        settings=settings,
        client=FakeClient(models),
    )

    answer = client.generate_reply("Why is my pod failing?")

    assert answer == "Use kubectl describe pod."
    assert len(models.calls) == 1
    assert models.calls[0]["model"] == "test-model"


def test_empty_prompt_is_rejected(monkeypatch):
    client = GeminiClient(
        settings=make_settings(monkeypatch),
        client=FakeClient(FakeModels()),
    )

    with pytest.raises(
        GeminiConfigurationError,
        match="non-empty",
    ):
        client.generate_reply("  ")


def test_oversized_prompt_is_rejected(monkeypatch):
    client = GeminiClient(
        settings=make_settings(monkeypatch),
        client=FakeClient(FakeModels()),
    )

    with pytest.raises(
        GeminiConfigurationError,
        match="character limit",
    ):
        client.generate_reply("x" * 12001)


def test_api_failure_is_sanitized(monkeypatch):
    settings = make_settings(monkeypatch)
    models = FakeModels(error=RuntimeError("sensitive provider detail"))
    client = GeminiClient(
        settings=settings,
        client=FakeClient(models),
    )

    with pytest.raises(GeminiServiceError) as error:
        client.generate_reply("Explain Terraform state.")

    assert "sensitive provider detail" not in str(error.value)


def test_missing_api_key_is_rejected(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("GEMINI_MODEL", "test-model")

    settings = get_settings()

    with pytest.raises(
        GeminiConfigurationError,
        match="API key is missing",
    ):
        GeminiClient(settings=settings)


def test_history_is_included(monkeypatch):
    settings = make_settings(monkeypatch)
    models = FakeModels(
        response=SimpleNamespace(text="A valid answer.")
    )
    client = GeminiClient(
        settings=settings,
        client=FakeClient(models),
    )

    client.generate_reply(
        "What next?",
        history=[
            {"role": "user", "content": "My pod is failing."},
            {"role": "assistant", "content": "Check pod events."},
        ],
    )

    contents = models.calls[0]["contents"]

    assert len(contents) == 3
    assert contents[0].role == "user"
    assert contents[1].role == "model"
    assert contents[2].role == "user"