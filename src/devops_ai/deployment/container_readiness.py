"""Static container packaging readiness checks."""

from __future__ import annotations

from pathlib import Path
from typing import Any


BUILD_FILES = ("Containerfile", "Dockerfile")
COMPOSE_FILES = ("podman-compose.yml", "docker-compose.yml", "compose.yaml")
IGNORE_FILES = (".containerignore", ".dockerignore")

EXCLUDED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".terraform",
    "dist",
    "build",
}


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


class ContainerReadinessChecker:
    """Inspect container packaging files without executing them."""

    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root).resolve()
        if not self.project_root.is_dir():
            raise ValueError("Project root must be an existing directory.")

    def _iter_files(self):
        for current, directories, filenames in __import__("os").walk(
            self.project_root, followlinks=False
        ):
            current_path = Path(current)
            directories[:] = [
                name
                for name in directories
                if name not in EXCLUDED_DIRECTORIES
                and not (current_path / name).is_symlink()
            ]
            for filename in filenames:
                path = current_path / filename
                if path.is_file() and _is_within(path.resolve(), self.project_root):
                    yield path

    def check(self) -> dict[str, Any]:
        files = list(self._iter_files())
        findings: list[dict[str, str]] = []

        build_files = [
            path for path in files if path.name in BUILD_FILES
        ]
        compose_files = [
            path for path in files if path.name in COMPOSE_FILES
        ]
        ignore_files = [
            path for path in files if path.name in IGNORE_FILES
        ]

        for path in build_files:
            relative = path.relative_to(self.project_root).as_posix()

            try:
                if path.stat().st_size > 1_000_000:
                    findings.append({
                        "code": "CONTAINER_FILE_TOO_LARGE",
                        "severity": "medium",
                        "file": relative,
                        "message": "Container build file exceeds the 1 MB inspection limit.",
                    })
                    continue

                content = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                findings.append({
                    "code": "CONTAINER_FILE_UNREADABLE",
                    "severity": "medium",
                    "file": relative,
                    "message": "Container build file could not be read as UTF-8.",
                })
                continue

            if not content.strip():
                findings.append({
                    "code": "CONTAINER_FILE_EMPTY",
                    "severity": "high",
                    "file": relative,
                    "message": "Container build file is empty.",
                })
                continue

            if any(
                line.strip().upper().startswith("FROM ")
                and line.strip().upper().endswith(":LATEST")
                for line in content.splitlines()
            ):
                findings.append({
                    "code": "CONTAINER_LATEST_TAG",
                    "severity": "medium",
                    "file": relative,
                    "message": "A base image uses the mutable latest tag.",
                })

            if not any(
                line.strip().upper().startswith("FROM ")
                for line in content.splitlines()
            ):
                findings.append({
                    "code": "CONTAINER_FROM_MISSING",
                    "severity": "high",
                    "file": relative,
                    "message": "No FROM instruction was detected.",
                })

            if not any(
                line.strip().upper().startswith("HEALTHCHECK ")
                for line in content.splitlines()
            ):
                findings.append({
                    "code": "CONTAINER_HEALTHCHECK_MISSING",
                    "severity": "info",
                    "file": relative,
                    "message": (
                        "No Docker-compatible HEALTHCHECK instruction was detected. "
                        "Confirm health monitoring is configured elsewhere if needed."
                    ),
                })

        for path in compose_files:
            relative = path.relative_to(self.project_root).as_posix()
            try:
                if path.stat().st_size > 1_000_000:
                    findings.append({
                        "code": "COMPOSE_FILE_TOO_LARGE",
                        "severity": "medium",
                        "file": relative,
                        "message": "Compose file exceeds the 1 MB inspection limit.",
                    })
                    continue
                content = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                findings.append({
                    "code": "COMPOSE_FILE_UNREADABLE",
                    "severity": "medium",
                    "file": relative,
                    "message": "Compose file could not be read as UTF-8.",
                })
                continue

            if "privileged: true" in content.lower():
                findings.append({
                    "code": "COMPOSE_PRIVILEGED",
                    "severity": "high",
                    "file": relative,
                    "message": "Privileged container mode was detected.",
                })

        if build_files and not ignore_files:
            findings.append({
                "code": "CONTAINER_IGNORE_MISSING",
                "severity": "info",
                "file": ".",
                "message": (
                    "No .containerignore or .dockerignore file was detected. "
                    "Confirm build context excludes secrets and unnecessary files."
                ),
            })

        return {
            "status": (
                "blocked"
                if any(item["severity"] == "high" for item in findings)
                else "review"
                if any(item["severity"] in {"medium", "low"} for item in findings)
                else "ready"
            ),
            "build_files": sorted(
                path.relative_to(self.project_root).as_posix()
                for path in build_files
            ),
            "compose_files": sorted(
                path.relative_to(self.project_root).as_posix()
                for path in compose_files
            ),
            "ignore_files": sorted(
                path.relative_to(self.project_root).as_posix()
                for path in ignore_files
            ),
            "findings": findings,
            "limitations": [
                "Static checks only; no image build or container execution occurs.",
                "Does not verify registry access, image signatures, or image vulnerabilities.",
                "A HEALTHCHECK instruction is not proof that the application is healthy.",
                "Compose files are inspected heuristically, not fully parsed.",
            ],
        }