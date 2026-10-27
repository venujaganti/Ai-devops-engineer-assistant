
import json

from src.devops_ai.integrations.repository_scanner import RepositoryScanner
from src.devops_ai.integrations.report_writer import build_report, report_to_json


def test_repository_scan_to_json_report(tmp_path):
    (tmp_path / "settings.json").write_text(
        '{"enabled": true}', encoding="utf-8"
    )
    (tmp_path / "network.tf").write_text(
        'resource "example" "network" {\n'
        '  cidr_blocks = ["0.0.0.0/0"]\n'
        '}\n',
        encoding="utf-8",
    )

    scan_result = RepositoryScanner(tmp_path).scan()
    report = build_report(scan_result)
    parsed = json.loads(report_to_json(report))

    assert parsed["scanned_file_count"] == 2
    assert parsed["summary"]["total"] >= 1
    assert any(
        finding["rule_id"] == "SEC-TF-002"
        for finding in parsed["findings"]
    )
    assert parsed["schema_version"] == "1.0"
