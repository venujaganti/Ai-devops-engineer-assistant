
from pathlib import Path

from .config_validator import validate_configuration
from .diagnostics import DiagnosticFinding


SKIP_DIRS = {
    ".git", ".venv", "venv", "__pycache__", "node_modules",
    ".terraform", "dist", "build", ".pytest_cache",
}

MAX_FILE_BYTES = 1_000_000
MAX_FILES = 5_000

SUPPORTED_NAMES = {
    "dockerfile", "containerfile", "docker-compose.yml",
    "podman-compose.yml", "jenkinsfile",
}

SUPPORTED_SUFFIXES = {".tf", ".yaml", ".yml", ".json"}


class RepositoryScanner:
    def __init__(
        self,
        project_root: str | Path,
        max_files: int = MAX_FILES,
        max_file_bytes: int = MAX_FILE_BYTES,
    ) -> None:
        root = Path(project_root).expanduser().resolve(strict=True)
        if not root.is_dir():
            raise ValueError("Repository path must be a directory.")
        if max_files < 1 or max_files > MAX_FILES:
            raise ValueError(f"max_files must be between 1 and {MAX_FILES}.")
        if max_file_bytes < 1 or max_file_bytes > MAX_FILE_BYTES:
            raise ValueError(
                f"max_file_bytes must be between 1 and {MAX_FILE_BYTES}."
            )

        self.root = root
        self.max_files = max_files
        self.max_file_bytes = max_file_bytes

    @staticmethod
    def _supported(path: Path) -> bool:
        return (
            path.name.lower() in SUPPORTED_NAMES
            or path.suffix.lower() in SUPPORTED_SUFFIXES
        )

    def _files(self) -> list[Path]:
        selected: list[Path] = []

        for current, dirs, filenames in __import__("os").walk(
            self.root, followlinks=False
        ):
            current_path = Path(current)
            dirs[:] = sorted(
                name for name in dirs
                if name not in SKIP_DIRS
                and not (current_path / name).is_symlink()
            )

            for filename in sorted(filenames):
                path = current_path / filename
                if path.is_symlink() or not self._supported(path):
                    continue

                try:
                    resolved = path.resolve(strict=True)
                    resolved.relative_to(self.root)
                except (OSError, ValueError):
                    continue

                selected.append(resolved)
                if len(selected) >= self.max_files:
                    return selected

        return selected

    def scan(self) -> dict:
        findings: list[DiagnosticFinding] = []
        scanned_files: list[str] = []
        skipped_files: list[dict[str, str]] = []

        for path in self._files():
            relative = path.relative_to(self.root).as_posix()

            try:
                if path.stat().st_size > self.max_file_bytes:
                    skipped_files.append({
                        "file": relative,
                        "reason": "File exceeds the configured size limit.",
                    })
                    continue

                content = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                skipped_files.append({
                    "file": relative,
                    "reason": "File could not be read as UTF-8.",
                })
                continue

            scanned_files.append(relative)
            findings.extend(validate_configuration(content, relative))

        return {
            "repository": self.root.name,
            "scanned_file_count": len(scanned_files),
            "scanned_files": scanned_files,
            "skipped_files": skipped_files,
            "findings": findings,
            "limitations": [
                "Static checks only; not a complete security audit.",
                "Terraform syntax is not fully validated by an HCL parser.",
                "Files excluded by the scanner are not assessed.",
                "No deployment or infrastructure changes were performed.",
            ],
        }
