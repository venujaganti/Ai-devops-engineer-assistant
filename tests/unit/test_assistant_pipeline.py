
import json
from unittest.mock import Mock

from src.devops_ai.remediation.remediation_service import RemediationService


def test_remediation_pipeline_uses_mocked_gemini(sample_finding):
    client = Mock()
    client.generate_reply.return_value = json.dumps({
        "summary": "Review the container privileges.",
        "items": [{
            "rule_id": sample_finding["rule_id"],
            "severity": sample_finding["severity"],
            "title": "Review privileged mode",
            "explanation": "Privileged mode can grant additional host access.",
            "steps": [
                "Confirm whether privileged mode is required.",
                "Remove it if the workload does not need it.",
            ],
            "verification": "Review the updated configuration and test it.",
            "patch": None,
        }],
        "limitations": ["Static analysis only."],
    })

    service = RemediationService(client)
    report = service.analyze([sample_finding])

    assert report.items
    assert report.items[0].rule_id == sample_finding["rule_id"]
    assert report.items[0].steps
    client.generate_reply.assert_called_once()
