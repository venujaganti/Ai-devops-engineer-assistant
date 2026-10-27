"""Serializable result types for end-to-end workflows."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


VALID_STATUSES = {
    "success",
    "warning",
    "failed",
    "skipped",
    "blocked",
}


@dataclass
class WorkflowStep:
    """Result of one workflow operation."""

    name: str
    status: str
    summary: str
    details: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Workflow step name must not be empty.")
        if self.status not in VALID_STATUSES:
            raise ValueError(f"Unsupported workflow status: {self.status}")
        if not self.summary.strip():
            raise ValueError("Workflow step summary must not be empty.")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WorkflowResult:
    """Top-level result for one DevOps workflow."""

    workflow_id: str
    status: str
    summary: str
    steps: list[WorkflowStep] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        if not self.workflow_id.strip():
            raise ValueError("Workflow ID must not be empty.")
        if self.status not in VALID_STATUSES:
            raise ValueError(f"Unsupported workflow status: {self.status}")
        if not self.summary.strip():
            raise ValueError("Workflow summary must not be empty.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "status": self.status,
            "summary": self.summary,
            "created_at": self.created_at,
            "steps": [step.to_dict() for step in self.steps],
            "limitations": list(self.limitations),
        }