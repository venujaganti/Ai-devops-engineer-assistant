
import json

from src.devops_ai.integrations.diagnostics import DiagnosticFinding
from src.devops_ai.integrations.report_writer import build_report, report_to_json


def test_report_serializes_findings():
    finding = DiagnosticFinding(
        rule_id="TEST-001",
        severity="low",
        category="test",
        file_path="main.tf",
        line=1,
        message="Test message",
        recommendation="Review the file.",
    )
    scan_result = {
        "repository": "demo",
        "scanned_file_count": 1,
        "scanned_files": ["main.tf"],
        "skipped_files": [],
        "findings": [finding],
        "limitations": [],
    }

    report = build_report(scan_result)
    parsed = json.loads(report_to_json(report))

    assert parsed["schema_version"] == "1.0"
    assert parsed["repository"] == "demo"
    assert parsed["findings"][0]["rule_id"] == "TEST-001"
    assert parsed["summary"]["total"] == 1
