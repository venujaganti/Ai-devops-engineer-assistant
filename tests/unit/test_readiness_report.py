import json

from devops_ai.deployment.readiness_report import (
    build_readiness_report,
    report_to_json,
)


def test_report_contains_summary_and_version():
    source = {
        "status": "blocked",
        "summary": {
            "total_findings": 2,
            "blocking_findings": 1,
            "critical_findings": 0,
            "high_findings": 1,
        },
        "sections": {},
        "findings": [
            {"code": "ENV_REQUIRED_MISSING", "severity": "high"}
        ],
        "limitations": ["Static checks only."],
    }

    report = build_readiness_report(source)

    assert report["report_version"] == "1.0"
    assert report["status"] == "blocked"
    assert report["summary"]["blocking_findings"] == 1
    assert report["generated_at"]


def test_report_serializes_to_valid_json():
    report = build_readiness_report({
        "status": "review_required",
        "summary": {},
        "sections": {},
        "findings": [],
        "limitations": [],
    })

    decoded = json.loads(report_to_json(report))

    assert decoded["status"] == "review_required"
    assert decoded["findings"] == []