"""Static Prometheus configuration validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class PrometheusConfigValidator:
    """Validate common Prometheus YAML configuration requirements."""

    def validate_file(self, file_path: str | Path) -> dict[str, Any]:
        path = Path(file_path).expanduser().resolve()

        if not path.is_file():
            return self._result(
                "blocked",
                [{
                    "code": "PROM_FILE_MISSING",
                    "severity": "high",
                    "message": "Prometheus configuration file was not found.",
                    "file": str(path),
                }],
            )

        try:
            if path.stat().st_size > 1_000_000:
                return self._result(
                    "blocked",
                    [{
                        "code": "PROM_FILE_TOO_LARGE",
                        "severity": "high",
                        "message": "Configuration exceeds the 1 MB inspection limit.",
                        "file": path.name,
                    }],
                )
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            return self._result(
                "blocked",
                [{
                    "code": "PROM_FILE_UNREADABLE",
                    "severity": "high",
                    "message": "Configuration could not be read as UTF-8.",
                    "file": path.name,
                }],
            )

        return self.validate_text(content, filename=path.name)

    def validate_text(
        self,
        content: str,
        filename: str = "prometheus.yml",
    ) -> dict[str, Any]:
        findings: list[dict[str, str]] = []

        try:
            import yaml
        except ImportError:
            return self._result(
                "review_required",
                [{
                    "code": "PROM_YAML_DEPENDENCY_MISSING",
                    "severity": "medium",
                    "message": (
                        "PyYAML is unavailable; install the project's declared "
                        "YAML dependency to validate configuration structure."
                    ),
                    "file": filename,
                }],
            )

        try:
            config = yaml.safe_load(content)
        except yaml.YAMLError:
            return self._result(
                "blocked",
                [{
                    "code": "PROM_INVALID_YAML",
                    "severity": "high",
                    "message": "Prometheus configuration contains invalid YAML.",
                    "file": filename,
                }],
            )

        if not isinstance(config, dict):
            findings.append({
                "code": "PROM_ROOT_NOT_MAPPING",
                "severity": "high",
                "message": "The YAML root must be a mapping.",
                "file": filename,
            })
            return self._result("blocked", findings)

        global_config = config.get("global", {})
        if not isinstance(global_config, dict):
            findings.append({
                "code": "PROM_INVALID_GLOBAL",
                "severity": "high",
                "message": "'global' must be a mapping.",
                "file": filename,
            })

        jobs = config.get("scrape_configs")
        if not isinstance(jobs, list) or not jobs:
            findings.append({
                "code": "PROM_NO_SCRAPE_JOBS",
                "severity": "high",
                "message": "No scrape_configs were defined.",
                "file": filename,
            })
            jobs = []

        job_names: set[str] = set()

        for index, job in enumerate(jobs):
            location = f"scrape_configs[{index}]"

            if not isinstance(job, dict):
                findings.append({
                    "code": "PROM_INVALID_JOB",
                    "severity": "high",
                    "message": f"{location} must be a mapping.",
                    "file": filename,
                })
                continue

            name = job.get("job_name")
            if not isinstance(name, str) or not name.strip():
                findings.append({
                    "code": "PROM_JOB_NAME_MISSING",
                    "severity": "high",
                    "message": f"{location} has no valid job_name.",
                    "file": filename,
                })
            elif name in job_names:
                findings.append({
                    "code": "PROM_DUPLICATE_JOB_NAME",
                    "severity": "high",
                    "message": f"Duplicate scrape job name: {name}.",
                    "file": filename,
                })
            else:
                job_names.add(name)

            targets = job.get("static_configs", [])
            if not isinstance(targets, list):
                findings.append({
                    "code": "PROM_INVALID_STATIC_CONFIG",
                    "severity": "high",
                    "message": f"{location}.static_configs must be a list.",
                    "file": filename,
                })
                continue

            for target_index, target in enumerate(targets):
                if not isinstance(target, dict):
                    findings.append({
                        "code": "PROM_INVALID_TARGET",
                        "severity": "high",
                        "message": (
                            f"{location}.static_configs[{target_index}] "
                            "must be a mapping."
                        ),
                        "file": filename,
                    })
                    continue

                endpoints = target.get("targets", [])
                if not isinstance(endpoints, list):
                    findings.append({
                        "code": "PROM_INVALID_TARGET_LIST",
                        "severity": "high",
                        "message": "A targets field must be a list.",
                        "file": filename,
                    })
                elif not endpoints or any(
                    not isinstance(endpoint, str) or not endpoint.strip()
                    for endpoint in endpoints
                ):
                    findings.append({
                        "code": "PROM_EMPTY_TARGET",
                        "severity": "medium",
                        "message": f"{location} contains an empty target list or target.",
                        "file": filename,
                    })

            if job.get("scheme") == "http":
                findings.append({
                    "code": "PROM_HTTP_SCRAPE",
                    "severity": "info",
                    "message": (
                        f"{location} uses HTTP. Confirm this is appropriate "
                        "for the network and deployment environment."
                    ),
                    "file": filename,
                })

            if job.get("basic_auth") and not job.get("authorization"):
                findings.append({
                    "code": "PROM_BASIC_AUTH_REVIEW",
                    "severity": "medium",
                    "message": (
                        f"{location} uses basic authentication; verify that "
                        "credentials are supplied securely and not committed."
                    ),
                    "file": filename,
                })

        blocking = any(
            item["severity"] == "high" for item in findings
        )
        review = any(
            item["severity"] == "medium" for item in findings
        )

        return self._result(
            "blocked" if blocking else "review_required" if review else "ready",
            findings,
        )

    @staticmethod
    def _result(
        status: str,
        findings: list[dict[str, str]],
    ) -> dict[str, Any]:
        return {
            "status": status,
            "findings": findings,
            "limitations": [
                "Static checks only; Prometheus itself has not parsed this file.",
                "Target reachability and scrape success are not tested.",
                "Advanced relabeling, service discovery, and PromQL are not fully validated.",
            ],
        }