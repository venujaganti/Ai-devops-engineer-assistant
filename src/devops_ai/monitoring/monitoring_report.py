"""Monitoring readiness report generation."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


def build_monitoring_report(
    results: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Build a report from named diagnostic results."""
    normalized: dict[str, dict[str, Any]] = {}

    for name, result in results.items():
        if not isinstance(name, str) or not isinstance(result, dict):
            continue

        normalized[name] = result

    findings: list[dict[str, Any]] = []
    for section, result in normalized.items():
        section_findings = result.get("findings", [])
        if not isinstance(section_findings, list):
            continue

        for finding in section_findings:
            if isinstance(finding, dict):
                findings.append({**finding, "section": section})

    blocked = any(
        result.get("status") == "blocked"
        for result in normalized.values()
    )
    needs_review = any(
        result.get("status") in {"review_required", "unhealthy", "unreachable"}
        for result in normalized.values()
    )

    return {
        "report_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": (
            "blocked" if blocked
            else "review_required" if needs_review
            else "ready"
        ),
        "summary": {
            "sections_checked": len(normalized),
            "findings": len(findings),
            "high_severity": sum(
                str(item.get("severity", "")).lower() == "high"
                for item in findings
            ),
            "critical_severity": sum(
                str(item.get("severity", "")).lower() == "critical"
                for item in findings
            ),
        },
        "sections": normalized,
        "findings": findings,
        "limitations": [
            "A readiness report is not proof that monitoring is operational.",
            "Metrics and alert delivery require separate runtime verification.",
            "No alert notifications are sent by this report generator.",
        ],
    }


def report_to_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False)