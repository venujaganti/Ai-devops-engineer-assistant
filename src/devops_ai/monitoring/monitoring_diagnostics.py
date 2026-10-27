"""Local monitoring diagnostics with optional endpoint checks."""

from __future__ import annotations

import ipaddress
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from .alert_rule_validator import AlertRuleValidator
from .prometheus_validator import PrometheusConfigValidator


class MonitoringDiagnostics:
    """Run static monitoring checks without changing system state."""

    def __init__(
        self,
        project_root: str | Path,
        allow_endpoint_checks: bool = False,
        approved_endpoints: tuple[str, ...] = (),
        timeout_seconds: float = 3.0,
    ) -> None:
        self.project_root = Path(project_root).resolve()

        if not self.project_root.is_dir():
            raise ValueError("Project root must be an existing directory.")
        if not 0.5 <= timeout_seconds <= 5.0:
            raise ValueError("Timeout must be between 0.5 and 5 seconds.")

        self.allow_endpoint_checks = allow_endpoint_checks
        self.approved_endpoints = tuple(approved_endpoints)
        self.timeout_seconds = timeout_seconds
        self.prometheus_validator = PrometheusConfigValidator()
        self.alert_validator = AlertRuleValidator()

    def _safe_file(self, relative_path: str) -> Path | None:
        candidate = (self.project_root / relative_path).resolve()
        try:
            candidate.relative_to(self.project_root)
        except ValueError:
            return None

        if candidate.is_symlink() or not candidate.is_file():
            return None

        return candidate

    def inspect_config(self, relative_path: str) -> dict[str, Any]:
        """Inspect a Prometheus config or rule file inside project_root."""
        path = self._safe_file(relative_path)
        if path is None:
            return {
                "status": "blocked",
                "findings": [{
                    "code": "MONITORING_PATH_REJECTED",
                    "severity": "high",
                    "message": (
                        "The selected file is missing, is a symlink, "
                        "or is outside the configured project."
                    ),
                    "file": relative_path,
                }],
                "limitations": [],
            }

        if path.stat().st_size > 1_000_000:
            return {
                "status": "blocked",
                "findings": [{
                    "code": "MONITORING_FILE_TOO_LARGE",
                    "severity": "high",
                    "message": "File exceeds the 1 MB inspection limit.",
                    "file": relative_path,
                }],
                "limitations": [],
            }

        if path.suffix.lower() not in {".yaml", ".yml"}:
            return {
                "status": "blocked",
                "findings": [{
                    "code": "MONITORING_FILE_TYPE_UNSUPPORTED",
                    "severity": "high",
                    "message": "Only YAML monitoring files are supported.",
                    "file": relative_path,
                }],
                "limitations": [],
            }

        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            return {
                "status": "blocked",
                "findings": [{
                    "code": "MONITORING_FILE_UNREADABLE",
                    "severity": "high",
                    "message": "File could not be read as UTF-8.",
                    "file": relative_path,
                }],
                "limitations": [],
            }

        name = path.name.lower()
        if "rule" in name or "alert" in name:
            return self.alert_validator.validate_text(content, path.name)

        return self.prometheus_validator.validate_text(content, path.name)

    def check_metrics_endpoint(self, url: str) -> dict[str, Any]:
        """Optionally perform a GET against an explicitly approved endpoint."""
        if not self.allow_endpoint_checks:
            return {
                "status": "disabled",
                "message": "Endpoint checks are disabled.",
            }

        if url not in self.approved_endpoints:
            return {
                "status": "blocked",
                "message": "Endpoint is not on the approved endpoint list.",
            }

        parsed = urllib.parse.urlsplit(url)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
        ):
            return {
                "status": "blocked",
                "message": "Endpoint URL format is not permitted.",
            }

        hostname = parsed.hostname.lower()
        try:
            ip = ipaddress.ip_address(hostname)
            is_local = ip.is_loopback
        except ValueError:
            is_local = hostname == "localhost"

        if not is_local:
            return {
                "status": "blocked",
                "message": (
                    "Only loopback endpoints are allowed by this diagnostic."
                ),
            }

        request = urllib.request.Request(
            url,
            headers={"User-Agent": "DevOpsAssistant-Monitoring-Diagnostics"},
            method="GET",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout_seconds,
            ) as response:
                status_code = response.status
                content_type = response.headers.get("Content-Type", "")
                return {
                    "status": (
                        "reachable"
                        if 200 <= status_code < 300
                        else "unhealthy"
                    ),
                    "http_status": status_code,
                    "content_type": content_type[:100],
                    "message": "Metrics endpoint responded to HTTP GET.",
                }
        except urllib.error.HTTPError as exc:
            return {
                "status": "unhealthy",
                "http_status": exc.code,
                "message": "Metrics endpoint returned an HTTP error.",
            }
        except (urllib.error.URLError, TimeoutError, OSError):
            return {
                "status": "unreachable",
                "message": "Metrics endpoint could not be reached.",
            }