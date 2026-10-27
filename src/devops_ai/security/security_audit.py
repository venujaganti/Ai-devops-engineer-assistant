"""Read-only heuristic security audit for project files."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path

from devops_ai.security.input_validation import resolve_project_path
from devops_ai.security.secret_redactor import redact_secrets


@dataclass(frozen=True)
class SecurityFinding:
    rule_id: str
    severity: str
    file_path: str
    line: int
    message: str
    recommendation: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class SecurityAuditResult:
    project_root: str
    scanned_files: int
    skipped_files: int
    findings: list[SecurityFinding]
    limitations: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "project_root": self.project_root,
            "scanned_files": self.scanned_files,
            "skipped_files": self.skipped_files,
            "findings": [finding.to_dict() for finding in self.findings],
            "limitations": list(self.limitations),
        }


_SECRET_ASSIGNMENT = re.compile(
    r"""(?ix)
    \b(
        password|passwd|client_secret|api_key|api-key|
        secret_key|access_token|private_key
    )\b
    \s*[:=]\s*
    (["'][^"']{4,}["']|[^\s,;]{4,})
    """
)

_AWS_ACCESS_KEY = re.compile(r"\bAKIA[0-9A-Z]{16}\b")

_PERMISSIVE_INGRESS = re.compile(
    r"(?i)(0\.0\.0\.0/0|::/0)"
)

_DANGEROUS_SETTINGS = re.compile(
    r"(?i)^\s*(privileged|allowPrivilegeEscalation)\s*:\s*true\b"
)

_LATEST_IMAGE = re.compile(
    r"(?i)^\s*image\s*:\s*['\"]?[^#\s]+:latest\b"
)

_SENSITIVE_EXTENSIONS = {
    ".py", ".env", ".example", ".yaml", ".yml", ".json",
    ".toml", ".ini", ".cfg", ".conf", ".tf", ".sh",
    ".properties", ".xml", ".txt", ".md", ".dockerfile",
}

_IGNORED_DIRS = {
    ".git", ".venv", "venv", "__pycache__", "node_modules",
    ".terraform", "dist", "build", ".pytest_cache",
}


class SecurityAuditor:
    """Scan bounded project files using non-executing heuristic checks."""

    def __init__(
        self,
        project_root: str | Path,
        *,
        max_files: int = 5_000,
        max_file_bytes: int = 1_000_000,
    ) -> None:
        if max_files < 1:
            raise ValueError("max_files must be greater than zero.")

        if max_file_bytes < 1:
            raise ValueError("max_file_bytes must be greater than zero.")

        self.project_root = Path(project_root).expanduser().resolve(strict=True)

        if not self.project_root.is_dir():
            raise ValueError("Project root must be a directory.")

        self.max_files = max_files
        self.max_file_bytes = max_file_bytes

    @staticmethod
    def _is_scannable(path: Path) -> bool:
        name = path.name.lower()

        return (
            name in {
                "dockerfile", "containerfile", "jenkinsfile",
                ".env", ".env.example", ".env.sample",
            }
            or path.suffix.lower() in _SENSITIVE_EXTENSIONS
        )

    def _scan_file(
        self,
        path: Path,
    ) -> list[SecurityFinding]:
        findings: list[SecurityFinding] = []

        try:
            safe_path = resolve_project_path(self.project_root, path)
            if safe_path.is_symlink() or not safe_path.is_file():
                return findings

            if safe_path.stat().st_size > self.max_file_bytes:
                return findings

            content = safe_path.read_text(
                encoding="utf-8",
                errors="replace",
            )
        except (OSError, ValueError):
            return findings

        relative_path = safe_path.relative_to(self.project_root).as_posix()

        for line_number, line in enumerate(content.splitlines(), start=1):
            if _SECRET_ASSIGNMENT.search(line) or _AWS_ACCESS_KEY.search(line):
                findings.append(
                    SecurityFinding(
                        rule_id="SEC001",
                        severity="high",
                        file_path=relative_path,
                        line=line_number,
                        message="Possible hardcoded credential detected.",
                        recommendation=(
                            "Remove the credential, rotate it if real, and "
                            "load secrets from a managed secret store or "
                            "environment configuration."
                        ),
                    )
                )

            if _PERMISSIVE_INGRESS.search(line):
                findings.append(
                    SecurityFinding(
                        rule_id="SEC002",
                        severity="medium",
                        file_path=relative_path,
                        line=line_number,
                        message=(
                            "A rule may allow traffic from every IPv4 or "
                            "IPv6 address."
                        ),
                        recommendation=(
                            "Restrict source ranges to the smallest required "
                            "trusted network."
                        ),
                    )
                )

            if _DANGEROUS_SETTINGS.search(line):
                findings.append(
                    SecurityFinding(
                        rule_id="SEC003",
                        severity="high",
                        file_path=relative_path,
                        line=line_number,
                        message="A privileged container security setting is enabled.",
                        recommendation=(
                            "Disable privileged mode unless explicitly "
                            "required and formally reviewed."
                        ),
                    )
                )

            if _LATEST_IMAGE.search(line):
                findings.append(
                    SecurityFinding(
                        rule_id="SEC004",
                        severity="low",
                        file_path=relative_path,
                        line=line_number,
                        message="A container image uses the mutable latest tag.",
                        recommendation=(
                            "Pin an approved image version or immutable digest."
                        ),
                    )
                )

        # Ensure future changes do not accidentally include line contents.
        return [
            SecurityFinding(
                rule_id=finding.rule_id,
                severity=finding.severity,
                file_path=str(redact_secrets(finding.file_path)),
                line=finding.line,
                message=str(redact_secrets(finding.message)),
                recommendation=str(redact_secrets(finding.recommendation)),
            )
            for finding in findings
        ]

    def scan(self) -> SecurityAuditResult:
        findings: list[SecurityFinding] = []
        scanned_files = 0
        skipped_files = 0

        for current_root, directories, filenames in __import__("os").walk(
            self.project_root,
            followlinks=False,
        ):
            directories[:] = [
                directory
                for directory in directories
                if directory not in _IGNORED_DIRS
            ]

            for filename in filenames:
                path = Path(current_root) / filename

                if not self._is_scannable(path):
                    continue

                if scanned_files + skipped_files >= self.max_files:
                    skipped_files += 1
                    continue

                try:
                    if path.stat().st_size > self.max_file_bytes:
                        skipped_files += 1
                        continue
                except OSError:
                    skipped_files += 1
                    continue

                file_findings = self._scan_file(path)
                findings.extend(file_findings)
                scanned_files += 1

        return SecurityAuditResult(
            project_root=str(self.project_root),
            scanned_files=scanned_files,
            skipped_files=skipped_files,
            findings=findings,
            limitations=[
                "Heuristic checks only; findings can include false positives.",
                "This audit does not execute files or commands.",
                "This is not a replacement for Trivy, Gitleaks, Semgrep, "
                "SonarQube, or OWASP Dependency-Check.",
                "A clean result does not prove that the project is secure.",
            ],
        )