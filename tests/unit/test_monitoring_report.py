import json

from devops_ai.monitoring.monitoring_report import (
    build_monitoring_report,
    report_to_json,
)


def test_blocked_section_blocks_report():
    report = build_monitoring_report({
        "prometheus": {
            "status": "blocked",
            "findings": [
                {"code": "PROM_INVALID_YAML", "severity": "high"}
            ],
        }
    })

    assert report["status"] == "blocked"
    assert report["summary"]["findings"] == 1
    assert report["findings"][0]["section"] == "prometheus"


def test_clean_report_is_ready():
    report = build_monitoring_report({
        "prometheus": {"status": "ready", "findings": []},
    })

    assert report["status"] == "ready"
    assert report["summary"]["findings"] == 0


def test_report_is_valid_json():
    report = build_monitoring_report({
        "alert_rules": {"status": "review_required", "findings": []},
    })

    parsed = json.loads(report_to_json(report))

    assert parsed["status"] == "review_required"
    assert parsed["report_version"] == "1.0"