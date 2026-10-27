"""Combine deployment-readiness checks without performing deployment."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .container_readiness import ContainerReadinessChecker
from .environment_validator import EnvironmentValidator
from dataclasses import asdict, is_dataclass


class DeploymentPreflight:
    """Create a deployment preflight result from static/local checks."""

    def __init__(
        self,
        project_root: str | Path,
        environment_validator: EnvironmentValidator | None = None,
        repository_scanner: Any | None = None,
    ) -> None:
        self.project_root = Path(project_root).resolve()
        if not self.project_root.is_dir():
            raise ValueError("Project root must be an existing directory.")

        self.environment_validator = (
            environment_validator or EnvironmentValidator()
        )
        self.repository_scanner = repository_scanner
        self.container_checker = ContainerReadinessChecker(self.project_root)

    def run(
        self,
        environ: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        environment_result = self.environment_validator.validate(environ)
        container_result = self.container_checker.check()

        repository_result: dict[str, Any] = {
            "status": "not_run",
            "findings": [],
            "limitations": [
                "No repository scanner was supplied to the preflight service."
            ],
        }

        if self.repository_scanner is not None:
                scan_result = self.repository_scanner.scan()

                if isinstance(scan_result, dict):
                    repository_result = scan_result
                elif is_dataclass(scan_result):
                    repository_result = asdict(scan_result)
                elif hasattr(scan_result, "to_dict"):
                    repository_result = scan_result.to_dict()
                else:
                    repository_result = {
                        "status": "unsupported_result",
                        "findings": [],
                        "limitations": [
                            "Adapt the repository scanner result to a dictionary "
                            "or dataclass before using this preflight service."
                        ],
                    }

        sections = {
            "environment": environment_result,
            "containers": container_result,
            "repository": repository_result,
        }

        all_findings: list[dict[str, Any]] = []
        for section_name, section in sections.items():
            findings = section.get("findings", [])
            if not isinstance(findings, list):
                continue

            for finding in findings:
                if isinstance(finding, dict):
                    all_findings.append({
                        **finding,
                        "section": section_name,
                    })
                elif hasattr(finding, "__dict__"):
                    all_findings.append({
                        **vars(finding),
                        "section": section_name,
                    })

        blockers = [
            finding for finding in all_findings
            if str(finding.get("severity", "")).lower()
            in {"critical", "high"}
        ]

        return {
            "status": "blocked" if blockers else "review_required",
            "project_root": str(self.project_root),
            "sections": sections,
            "summary": {
                "total_findings": len(all_findings),
                "blocking_findings": len(blockers),
                "critical_findings": sum(
                    str(item.get("severity", "")).lower() == "critical"
                    for item in all_findings
                ),
                "high_findings": sum(
                    str(item.get("severity", "")).lower() == "high"
                    for item in all_findings
                ),
            },
            "findings": all_findings,
            "limitations": [
                "A successful preflight does not guarantee deployment success.",
                "Cloud identity, remote services, and target-cluster readiness are not verified.",
                "No deployment, build, push, or infrastructure-changing command is executed.",
            ],
        }