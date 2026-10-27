
from dataclasses import asdict, dataclass


ALLOWED_SEVERITIES = {"critical", "high", "medium", "low", "info"}


@dataclass(frozen=True)
class RemediationItem:
    rule_id: str
    severity: str
    title: str
    explanation: str
    steps: list[str]
    verification: str
    patch: str | None = None

    def __post_init__(self) -> None:
        if not self.rule_id.strip():
            raise ValueError("rule_id must not be empty")
        if self.severity not in ALLOWED_SEVERITIES:
            raise ValueError("Invalid severity")
        if not self.title.strip() or len(self.title) > 200:
            raise ValueError("Title must be between 1 and 200 characters")
        if not self.explanation.strip() or len(self.explanation) > 3000:
            raise ValueError("Explanation must be between 1 and 3000 characters")
        if not 1 <= len(self.steps) <= 8:
            raise ValueError("Provide between 1 and 8 remediation steps")
        if any(not isinstance(step, str) or not step.strip() or len(step) > 500
               for step in self.steps):
            raise ValueError("Each step must be a non-empty string of <= 500 chars")
        if not self.verification.strip() or len(self.verification) > 1000:
            raise ValueError("Verification must be between 1 and 1000 characters")
        if self.patch is not None and len(self.patch) > 8000:
            raise ValueError("Patch exceeds the 8000-character limit")

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class RemediationReport:
    summary: str
    items: list[RemediationItem]
    limitations: list[str]

    def to_dict(self) -> dict:
        return {
            "summary": self.summary,
            "items": [item.to_dict() for item in self.items],
            "limitations": list(self.limitations),
        }


def parse_remediation_response(data: object) -> RemediationReport:
    if not isinstance(data, dict):
        raise ValueError("AI response must be a JSON object")

    summary = data.get("summary")
    raw_items = data.get("items")
    limitations = data.get("limitations", [])

    if not isinstance(summary, str) or not summary.strip() or len(summary) > 3000:
        raise ValueError("Invalid report summary")
    if not isinstance(raw_items, list) or len(raw_items) > 30:
        raise ValueError("Invalid remediation items list")
    if not isinstance(limitations, list) or len(limitations) > 10:
        raise ValueError("Invalid limitations list")
    if any(not isinstance(value, str) or len(value) > 500 for value in limitations):
        raise ValueError("Invalid limitation entry")

    items = []
    for raw in raw_items:
        if not isinstance(raw, dict):
            raise ValueError("Each remediation item must be an object")
        steps = raw.get("steps")
        if not isinstance(steps, list):
            raise ValueError("Remediation steps must be a list")

        items.append(RemediationItem(
            rule_id=str(raw.get("rule_id", "")),
            severity=str(raw.get("severity", "")),
            title=str(raw.get("title", "")),
            explanation=str(raw.get("explanation", "")),
            steps=steps,
            verification=str(raw.get("verification", "")),
            patch=raw.get("patch"),
        ))

    return RemediationReport(
        summary=summary,
        items=items,
        limitations=limitations,
    )
