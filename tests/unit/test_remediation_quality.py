
from src.devops_ai.remediation.schemas import parse_remediation_response


def test_remediation_has_actionable_steps():
    payload = {
        "summary": "The configuration needs a security review.",
        "items": [{
            "rule_id": "SEC-TF-002",
            "severity": "medium",
            "title": "Review unrestricted ingress",
            "explanation": (
                "The provided configuration may allow inbound traffic "
                "from every IPv4 address."
            ),
            "steps": [
                "Identify the service and port that require access.",
                "Restrict the allowed source CIDR.",
                "Review the change before applying it.",
            ],
            "verification": (
                "Inspect the resulting network rule and test the intended access."
            ),
            "patch": None,
        }],
        "limitations": ["The finding is based on static analysis."],
    }

    report = parse_remediation_response(payload)

    assert report.items
    for item in report.items:
        assert item.title.strip()
        assert item.explanation.strip()
        assert len(item.steps) >= 1
        assert item.verification.strip()
        assert item.severity in {"critical", "high", "medium", "low", "info"}
