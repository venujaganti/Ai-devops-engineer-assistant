"""Safe orchestration of existing DevOps assistant services."""

from __future__ import annotations

import re
from typing import Any, Callable
from uuid import uuid4

from .workflow_result import WorkflowResult, WorkflowStep


_ALLOWED_TASKS = {
    "assistant",
    "repository_scan",
    "remediation",
    "deployment_preflight",
    "monitoring_validation",
}

_SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|password|secret|token)\s*[:=]\s*\S+"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]+"),
)


def _sanitize_text(value: str, limit: int = 2000) -> str:
    """Limit text and redact common secret-shaped values."""
    text = value[:limit]
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text


class DevOpsWorkflow:
    """Run explicitly selected diagnostic steps without executing commands."""

    def __init__(
        self,
        assistant: Any | None = None,
        repository_scanner: Any | None = None,
        remediation: Any | None = None,
        deployment_preflight: Any | None = None,
        monitoring_diagnostics: Any | None = None,
    ) -> None:
        self.assistant = assistant
        self.repository_scanner = repository_scanner
        self.remediation = remediation
        self.deployment_preflight = deployment_preflight
        self.monitoring_diagnostics = monitoring_diagnostics

    def run(
        self,
        task: str,
        question: str = "",
        *,
        run_repository_scan: bool = False,
        run_remediation: bool = False,
        run_deployment_preflight: bool = False,
        monitoring_config_path: str | None = None,
        environ: dict[str, str] | None = None,
    ) -> WorkflowResult:
        """Execute selected service calls, not shell or deployment commands."""
        if task not in _ALLOWED_TASKS:
            return WorkflowResult(
                workflow_id=str(uuid4()),
                status="blocked",
                summary="The requested workflow task is not allowed.",
                limitations=["Only predefined workflow task names are accepted."],
            )

        if len(question) > 10_000:
            return WorkflowResult(
                workflow_id=str(uuid4()),
                status="blocked",
                summary="The question exceeds the allowed length.",
            )

        steps: list[WorkflowStep] = []
        findings_for_remediation: list[Any] = []

        if task == "assistant":
            if self.assistant is None:
                steps.append(self._skipped("assistant", "Assistant service is not configured."))
            elif not question.strip():
                steps.append(self._blocked("assistant", "A non-empty question is required."))
            else:
                try:
                    # Match this call to your existing AssistantService API.
                    result = self.assistant.answer(question)
                    steps.append(
                        WorkflowStep(
                            name="assistant",
                            status="success",
                            summary="Assistant response generated.",
                            details={"result": self._safe_result(result)},
                        )
                    )
                except Exception as exc:
                    steps.append(
                        WorkflowStep(
                            name="assistant",
                            status="failed",
                            summary="Assistant request failed.",
                            details={"error_type": type(exc).__name__},
                        )
                    )

        if task == "repository_scan" or run_repository_scan:
            if self.repository_scanner is None:
                steps.append(self._skipped("repository_scan", "Repository scanner is not configured."))
            else:
                try:
                    scan_result = self.repository_scanner.scan()
                    normalized = self._normalize_result(scan_result)
                    findings_for_remediation = normalized.get("findings", [])
                    steps.append(
                        WorkflowStep(
                            name="repository_scan",
                            status="success",
                            summary="Repository scan completed.",
                            details=normalized,
                        )
                    )
                except Exception as exc:
                    steps.append(
                        WorkflowStep(
                            name="repository_scan",
                            status="failed",
                            summary="Repository scan failed.",
                            details={"error_type": type(exc).__name__},
                        )
                    )

        if task == "remediation" or run_remediation:
            if self.remediation is None:
                steps.append(self._skipped("remediation", "Remediation service is not configured."))
            elif not findings_for_remediation:
                steps.append(
                    self._skipped(
                        "remediation",
                        "No repository findings are available in this workflow.",
                    )
                )
            else:
                try:
                    # Adapt to the actual remediation service's public method.
                    result = self.remediation.generate(findings_for_remediation)
                    steps.append(
                        WorkflowStep(
                            name="remediation",
                            status="success",
                            summary="Remediation suggestions generated for review.",
                            details={"result": self._safe_result(result)},
                        )
                    )
                except Exception as exc:
                    steps.append(
                        WorkflowStep(
                            name="remediation",
                            status="failed",
                            summary="Remediation generation failed.",
                            details={"error_type": type(exc).__name__},
                        )
                    )

        if task == "deployment_preflight" or run_deployment_preflight:
            if self.deployment_preflight is None:
                steps.append(self._skipped("deployment_preflight", "Deployment preflight is not configured."))
            else:
                try:
                    result = self.deployment_preflight.run(environ=environ)
                    normalized = self._normalize_result(result)
                    status = (
                        "blocked"
                        if normalized.get("status") == "blocked"
                        else "warning"
                    )
                    steps.append(
                        WorkflowStep(
                            name="deployment_preflight",
                            status=status,
                            summary="Deployment preflight report generated; no deployment was performed.",
                            details=normalized,
                        )
                    )
                except Exception as exc:
                    steps.append(
                        WorkflowStep(
                            name="deployment_preflight",
                            status="failed",
                            summary="Deployment preflight failed.",
                            details={"error_type": type(exc).__name__},
                        )
                    )

        if task == "monitoring_validation":
            if self.monitoring_diagnostics is None:
                steps.append(self._skipped("monitoring_validation", "Monitoring diagnostics are not configured."))
            elif not monitoring_config_path:
                steps.append(self._blocked("monitoring_validation", "A monitoring configuration path is required."))
            else:
                try:
                    result = self.monitoring_diagnostics.inspect_config(
                        monitoring_config_path
                    )
                    normalized = self._normalize_result(result)
                    status = (
                        "blocked"
                        if normalized.get("status") == "blocked"
                        else "success"
                        if normalized.get("status") == "ready"
                        else "warning"
                    )
                    steps.append(
                        WorkflowStep(
                            name="monitoring_validation",
                            status=status,
                            summary="Monitoring configuration validation completed.",
                            details=normalized,
                        )
                    )
                except Exception as exc:
                    steps.append(
                        WorkflowStep(
                            name="monitoring_validation",
                            status="failed",
                            summary="Monitoring validation failed.",
                            details={"error_type": type(exc).__name__},
                        )
                    )

        overall_status = self._overall_status(steps)
        return WorkflowResult(
            workflow_id=str(uuid4()),
            status=overall_status,
            summary=self._summary(overall_status, steps),
            steps=steps,
            limitations=[
                "No shell commands, deployments, or infrastructure changes are performed.",
                "Remediation output is advisory and must be reviewed before use.",
                "The workflow uses the public interfaces of injected services.",
            ],
        )

    @staticmethod
    def _normalize_result(result: Any) -> dict[str, Any]:
        if isinstance(result, dict):
            return result
        if hasattr(result, "to_dict"):
            value = result.to_dict()
            if isinstance(value, dict):
                return value
        if hasattr(result, "__dataclass_fields__"):
            from dataclasses import asdict
            value = asdict(result)
            if isinstance(value, dict):
                return value
        if isinstance(result, list):
            return {"findings": result}
        return {"result": DevOpsWorkflow._safe_result(result)}

    @staticmethod
    def _safe_result(value: Any) -> Any:
        """Return a bounded, JSON-friendly result with common secret redaction."""
        if isinstance(value, str):
            return _sanitize_text(value)
        if isinstance(value, (int, float, bool)) or value is None:
            return value
        if isinstance(value, dict):
            safe: dict[str, Any] = {}
            for key, item in list(value.items())[:100]:
                key_text = str(key)[:100]
                if re.search(r"(?i)(password|secret|api[_-]?key|token|private[_-]?key)", key_text):
                    safe[key_text] = "[REDACTED]"
                else:
                    safe[key_text] = DevOpsWorkflow._safe_result(item)
            return safe
        if isinstance(value, (list, tuple)):
            return [DevOpsWorkflow._safe_result(item) for item in value[:100]]
        if hasattr(value, "to_dict"):
            return DevOpsWorkflow._safe_result(value.to_dict())
        if hasattr(value, "__dataclass_fields__"):
            from dataclasses import asdict
            return DevOpsWorkflow._safe_result(asdict(value))
        return _sanitize_text(str(value), limit=500)

    @staticmethod
    def _skipped(name: str, message: str) -> WorkflowStep:
        return WorkflowStep(name, "skipped", message)

    @staticmethod
    def _blocked(name: str, message: str) -> WorkflowStep:
        return WorkflowStep(name, "blocked", message)

    @staticmethod
    def _overall_status(steps: list[WorkflowStep]) -> str:
        if not steps:
            return "failed"
        statuses = {step.status for step in steps}
        if "blocked" in statuses:
            return "blocked"
        if "failed" in statuses:
            return "failed"
        if "warning" in statuses or "skipped" in statuses:
            return "warning"
        return "success"

    @staticmethod
    def _summary(status: str, steps: list[WorkflowStep]) -> str:
        return (
            f"Workflow finished with status '{status}'. "
            f"{len(steps)} step(s) were recorded."
        )