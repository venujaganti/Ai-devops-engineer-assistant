
import pytest

from src.devops_ai.integrations.diagnostics import (
    DiagnosticFinding,
    normalize_findings,
    summarize_findings,
)


def make_finding(severity: str, rule_id: str = "TEST-001"):
    return DiagnosticFinding(
        rule_id=rule_id,
        severity=severity,
        category="test",
        file_path="config.yaml",
        line=1,
        message="Example finding",
        recommendation="Review the configuration.",
    )


def test_findings_are_sorted_by_severity():
    findings = [
        make_finding("low"),
        make_finding("critical"),
        make_finding("medium"),
    ]

    result = normalize_findings(findings)

    assert [item["severity"] for item in result] == [
        "critical", "medium", "low"
    ]


def test_summary_counts_findings():
    summary = summarize_findings([
        make_finding("high"),
        make_finding("high", "TEST-002"),
        make_finding("info"),
    ])

    assert summary["high"] == 2
    assert summary["info"] == 1
    assert summary["total"] == 3


def test_invalid_severity_is_rejected():
    with pytest.raises(ValueError):
        make_finding("urgent")
