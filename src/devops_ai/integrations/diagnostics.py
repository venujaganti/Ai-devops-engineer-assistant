
from dataclasses import asdict, dataclass
from typing import Any


VALID_SEVERITIES = {"critical", "high", "medium", "low", "info"}


@dataclass(frozen=True)
class DiagnosticFinding:
    rule_id: str
    severity: str
    category: str
    file_path: str
    line: int | None
    message: str
    recommendation: str

    def __post_init__(self) -> None:
        if self.severity not in VALID_SEVERITIES:
            raise ValueError(f"Invalid severity: {self.severity}")
        if not self.rule_id.strip():
            raise ValueError("rule_id must not be empty")
        if self.line is not None and self.line < 1:
            raise ValueError("line must be >= 1")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalize_findings(
    findings: list[DiagnosticFinding],
) -> list[dict[str, Any]]:
    """Return findings in a stable order for display and reporting."""
    ordered = sorted(
        findings,
        key=lambda item: (
            {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}[
                item.severity
            ],
            item.file_path.lower(),
            item.line or 0,
            item.rule_id,
        ),
    )
    return [item.to_dict() for item in ordered]


def summarize_findings(
    findings: list[DiagnosticFinding],
) -> dict[str, int]:
    summary = {severity: 0 for severity in VALID_SEVERITIES}
    for finding in findings:
        summary[finding.severity] += 1
    summary["total"] = len(findings)
    return summary
