
import json
from datetime import datetime, timezone

from .diagnostics import DiagnosticFinding, normalize_findings, summarize_findings


def build_report(scan_result: dict) -> dict:
    findings = scan_result.get("findings", [])

    if any(not isinstance(item, DiagnosticFinding) for item in findings):
        raise TypeError("findings must contain DiagnosticFinding objects.")

    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": scan_result["repository"],
        "scanned_file_count": scan_result["scanned_file_count"],
        "scanned_files": scan_result["scanned_files"],
        "skipped_files": scan_result["skipped_files"],
        "summary": summarize_findings(findings),
        "findings": normalize_findings(findings),
        "limitations": scan_result["limitations"],
    }


def report_to_json(report: dict) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False)
