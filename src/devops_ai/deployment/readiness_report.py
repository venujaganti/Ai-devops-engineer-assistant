"""Build JSON-safe deployment readiness reports."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


def build_readiness_report(preflight_result: dict[str, Any]) -> dict[str, Any]:
    """Create a timestamped report without exposing environment values."""
    summary = preflight_result.get("summary", {})
    findings = preflight_result.get("findings", [])

    return {
        "report_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": preflight_result.get("status", "unknown"),
        "summary": {
            "total_findings": int(summary.get("total_findings", len(findings))),
            "blocking_findings": int(summary.get("blocking_findings", 0)),
            "critical_findings": int(summary.get("critical_findings", 0)),
            "high_findings": int(summary.get("high_findings", 0)),
        },
        "sections": preflight_result.get("sections", {}),
        "findings": findings,
        "limitations": preflight_result.get("limitations", []),
    }


def report_to_json(report: dict[str, Any]) -> str:
    """Serialize a readiness report as readable JSON."""
    return json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False)