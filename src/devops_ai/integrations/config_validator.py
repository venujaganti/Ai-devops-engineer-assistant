
import json
from pathlib import Path
from typing import Any

from .diagnostics import DiagnosticFinding


def _finding(
    rule_id: str,
    severity: str,
    category: str,
    path: str,
    message: str,
    recommendation: str,
    line: int | None = None,
) -> DiagnosticFinding:
    return DiagnosticFinding(
        rule_id=rule_id,
        severity=severity,
        category=category,
        file_path=path,
        line=line,
        message=message,
        recommendation=recommendation,
    )


def validate_json(text: str, relative_path: str) -> list[DiagnosticFinding]:
    try:
        json.loads(text)
        return []
    except json.JSONDecodeError as exc:
        return [
            _finding(
                "CFG-JSON-001", "high", "syntax", relative_path,
                f"Invalid JSON: {exc.msg}",
                "Correct the JSON syntax and validate the file again.",
                exc.lineno,
            )
        ]


def validate_yaml(text: str, relative_path: str) -> list[DiagnosticFinding]:
    """Use PyYAML if installed; otherwise report that syntax was not verified."""
    try:
        import yaml
    except ImportError:
        return [
            _finding(
                "CFG-YAML-000", "info", "validation", relative_path,
                "YAML syntax was not verified because PyYAML is unavailable.",
                "Install the project's declared YAML dependency to enable parsing.",
            )
        ]

    try:
        yaml.safe_load(text)
        return []
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        line = mark.line + 1 if mark is not None else None
        return [
            _finding(
                "CFG-YAML-001", "high", "syntax", relative_path,
                "YAML syntax could not be parsed.",
                "Correct the YAML indentation, quoting, and structure.",
                line,
            )
        ]


def validate_terraform(text: str, relative_path: str) -> list[DiagnosticFinding]:
    findings: list[DiagnosticFinding] = []

    # This is a basic heuristic, not a complete HCL parser.
    opening = text.count("{")
    closing = text.count("}")
    if opening != closing:
        findings.append(
            _finding(
                "CFG-TF-001", "high", "syntax", relative_path,
                "The number of opening and closing braces differs.",
                "Review Terraform block boundaries. Use `terraform validate` "
                "in a controlled local environment for full validation.",
            )
        )

    if 'access_key =' in text or 'secret_key =' in text:
        findings.append(
            _finding(
                "SEC-TF-001", "high", "secrets", relative_path,
                "A possible hard-coded cloud credential assignment was found.",
                "Use an approved secret manager or environment-based credentials; "
                "rotate any exposed credential.",
            )
        )

    if "0.0.0.0/0" in text:
        findings.append(
            _finding(
                "SEC-TF-002", "medium", "network", relative_path,
                "A rule may allow traffic from every IPv4 address.",
                "Verify the port and restrict the source CIDR where possible.",
            )
        )

    return findings


def validate_configuration(
    text: str,
    relative_path: str,
) -> list[DiagnosticFinding]:
    name = Path(relative_path).name.lower()
    suffix = Path(relative_path).suffix.lower()

    if suffix == ".json":
        return validate_json(text, relative_path)

    if suffix in {".yaml", ".yml"}:
        findings = validate_yaml(text, relative_path)
        if name == "docker-compose.yml" or name == "podman-compose.yml":
            if "privileged: true" in text:
                findings.append(
                    _finding(
                        "SEC-CONT-001", "high", "container", relative_path,
                        "A privileged container setting was detected.",
                        "Remove privileged mode unless it is necessary and "
                        "approved for this workload.",
                    )
                )
        return findings

    if suffix == ".tf":
        return validate_terraform(text, relative_path)

    findings: list[DiagnosticFinding] = []
    lines = text.splitlines()

    for index, line in enumerate(lines, start=1):
        stripped = line.strip()

        if name in {"dockerfile", "containerfile"}:
            if stripped.upper().startswith("FROM ") and ":latest" in stripped:
                findings.append(
                    _finding(
                        "SEC-CONT-002", "low", "container", relative_path,
                        "A container base image uses the mutable `latest` tag.",
                        "Pin a tested image version or digest for reproducible builds.",
                        index,
                    )
                )
            if stripped.upper().startswith("USER ROOT"):
                findings.append(
                    _finding(
                        "SEC-CONT-003", "medium", "container", relative_path,
                        "The image explicitly switches to root.",
                        "Use a dedicated non-root user when compatible with the app.",
                        index,
                    )
                )

        if name == "jenkinsfile" and "withCredentials" not in text:
            if "password" in stripped.lower() and "=" in stripped:
                findings.append(
                    _finding(
                        "SEC-CI-001", "medium", "ci-cd", relative_path,
                        "A possible password assignment appears in the pipeline.",
                        "Use Jenkins Credentials and avoid literal secrets.",
                        index,
                    )
                )

    return findings
