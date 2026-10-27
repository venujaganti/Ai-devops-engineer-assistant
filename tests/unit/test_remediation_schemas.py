
import pytest

from src.devops_ai.remediation.schemas import parse_remediation_response


def valid_payload():
    return {
        "summary": "Two findings need attention.",
        "items": [{
            "rule_id": "SEC-CONT-001",
            "severity": "high",
            "title": "Privileged container",
            "explanation": "Privileged mode expands container permissions.",
            "steps": ["Remove privileged mode if it is not required."],
            "verification": "Review the container configuration.",
            "patch": None,
        }],
        "limitations": ["Static analysis only."],
    }


def test_valid_response_is_parsed():
    report = parse_remediation_response(valid_payload())

    assert report.items[0].rule_id == "SEC-CONT-001"
    assert report.items[0].severity == "high"


def test_invalid_severity_is_rejected():
    payload = valid_payload()
    payload["items"][0]["severity"] = "urgent"

    with pytest.raises(ValueError):
        parse_remediation_response(payload)


def test_missing_steps_are_rejected():
    payload = valid_payload()
    payload["items"][0]["steps"] = []

    with pytest.raises(ValueError):
        parse_remediation_response(payload)


def test_too_many_items_are_rejected():
    payload = valid_payload()
    payload["items"] = payload["items"] * 31

    with pytest.raises(ValueError):
        parse_remediation_response(payload)
