import json

import pytest

from src.devops_ai.assistant.assistant_service import (
    DevOpsAssistantService,
    _extract_json,
)


class FakeGeminiClient:
    def __init__(self, response):
        self.response = response

    def generate_reply(self, message, history):
        assert "User request:" in message
        return self.response


class FakeRAGService:
    def answer(self, message):
        return {
            "answer": "Use the approved Kubernetes runbook.",
            "sources": [
                {
                    "source": "kubernetes.md",
                    "chunk": 1,
                    "similarity": 0.9,
                }
            ],
        }


def test_extracts_valid_json():
    result = _extract_json(
        '{"summary":"Check the pod","commands":[]}'
    )

    assert result["summary"] == "Check the pod"


def test_rejects_invalid_json():
    with pytest.raises(ValueError):
        _extract_json("not JSON")


def test_returns_structured_answer():
    payload = {
        "summary": "Inspect the pod status.",
        "diagnosis": ["The pod may be restarting."],
        "recommended_steps": ["Check recent events."],
        "commands": [
            {
                "command": "kubectl get pods",
                "purpose": "List pods",
            }
        ],
        "validation_steps": ["Confirm pod readiness."],
        "warnings": [],
    }

    service = DevOpsAssistantService(
        gemini_client=FakeGeminiClient(json.dumps(payload)),
        rag_service=FakeRAGService(),
    )

    result = service.answer("Why is my Kubernetes pod failing?")

    assert result.category == "kubernetes"
    assert result.summary == "Inspect the pod status."
    assert result.commands[0].risk_level == "low"
    assert result.commands[0].requires_approval is True
    assert result.sources[0]["source"] == "kubernetes.md"


def test_invalid_gemini_json_returns_safe_response():
    service = DevOpsAssistantService(
        gemini_client=FakeGeminiClient("invalid response"),
    )

    result = service.answer("Explain a CI/CD pipeline")

    assert "couldn't validate" in result.summary
    assert result.commands == []


def test_empty_request_is_rejected():
    service = DevOpsAssistantService(
        gemini_client=FakeGeminiClient("{}"),
    )

    with pytest.raises(ValueError):
        service.answer(" ")


def test_oversized_request_is_rejected():
    service = DevOpsAssistantService(
        gemini_client=FakeGeminiClient("{}"),
    )

    with pytest.raises(ValueError):
        service.answer("x" * 12001)