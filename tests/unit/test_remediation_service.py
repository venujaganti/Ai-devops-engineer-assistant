
import json
from unittest.mock import Mock

import pytest

from src.devops_ai.remediation.remediation_service import RemediationService


def valid_response():
    return json.dumps({
        "summary": "Review the container configuration.",
        "items": [{
            "rule_id": "SEC-CONT-001",
            "severity": "high",
            "title": "Privileged container",
            "explanation": "The configuration grants elevated permissions.",
            "steps": ["Remove privileged mode if unnecessary."],
            "verification": "Review the resulting container configuration.",
            "patch": None,
        }],
        "limitations": ["Static checks only."],
    })


def test_service_uses_existing_gemini_client():
    client = Mock()
    client.generate_reply.return_value = valid_response()
    service = RemediationService(client)

    report = service.analyze([{
        "rule_id": "SEC-CONT-001",
        "severity": "high",
        "category": "container",
        "file_path": "podman-compose.yml",
        "line": 4,
        "message": "Privileged mode detected.",
        "recommendation": "Review container privileges.",
    }])

    assert report.items[0].rule_id == "SEC-CONT-001"
    client.generate_reply.assert_called_once()


def test_service_rejects_invalid_json():
    client = Mock()
    client.generate_reply.return_value = "not-json"

    with pytest.raises(ValueError, match="valid JSON"):
        RemediationService(client).analyze([{
            "rule_id": "TEST-1",
            "severity": "low",
            "message": "Test finding",
        }])


def test_service_does_not_call_gemini_for_empty_findings():
    client = Mock()
    report = RemediationService(client).analyze([])

    assert report.items == []
    client.generate_reply.assert_not_called()
