"""Input validation and safe project path resolution."""

from __future__ import annotations

from pathlib import Path


class InputValidationError(ValueError):
    """Raised when input fails security validation."""


def validate_text(
    value: object,
    *,
    field_name: str = "input",
    max_length: int = 10_000,
    allow_empty: bool = False,
) -> str:
    """Validate and normalize a user-provided text value."""
    if not isinstance(value, str):
        raise InputValidationError(f"{field_name} must be text.")

    if max_length < 1:
        raise ValueError("max_length must be greater than zero.")

    normalized = value.strip()

    if not allow_empty and not normalized:
        raise InputValidationError(f"{field_name} cannot be empty.")

    if len(normalized) > max_length:
        raise InputValidationError(
            f"{field_name} exceeds the maximum length of {max_length}."
        )

    if "\x00" in normalized:
        raise InputValidationError(
            f"{field_name} contains an invalid null character."
        )

    return normalized


def resolve_project_path(
    project_root: str | Path,
    requested_path: str | Path,
    *,
    must_exist: bool = True,
) -> Path:
    """Resolve a path and ensure it stays inside the approved project root.

    Symlinks that resolve outside the project root are rejected.
    """
    root = Path(project_root).expanduser().resolve(strict=True)

    if not root.is_dir():
        raise InputValidationError("Project root must be a directory.")

    raw_path = str(requested_path)

    if not raw_path.strip():
        raise InputValidationError("Project path cannot be empty.")

    candidate = Path(raw_path).expanduser()

    if not candidate.is_absolute():
        candidate = root / candidate

    try:
        resolved = candidate.resolve(strict=must_exist)
        resolved.relative_to(root)
    except (OSError, RuntimeError, ValueError) as exc:
        raise InputValidationError(
            "Requested path is invalid or outside the project root."
        ) from exc

    if must_exist and not resolved.exists():
        raise InputValidationError("Requested path does not exist.")

    return resolved