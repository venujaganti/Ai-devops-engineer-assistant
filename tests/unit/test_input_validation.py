from pathlib import Path

import pytest

from devops_ai.security.input_validation import (
    InputValidationError,
    resolve_project_path,
    validate_text,
)


def test_validate_text_strips_whitespace():
    assert validate_text("  inspect pods  ") == "inspect pods"


def test_validate_text_rejects_empty_input():
    with pytest.raises(InputValidationError):
        validate_text("   ")


def test_validate_text_rejects_oversized_input():
    with pytest.raises(InputValidationError):
        validate_text("x" * 11, max_length=10)


def test_validate_text_rejects_non_string():
    with pytest.raises(InputValidationError):
        validate_text(123)


def test_validate_text_rejects_null_character():
    with pytest.raises(InputValidationError):
        validate_text("hello\x00world")


def test_resolve_project_path_accepts_child(tmp_path: Path):
    project_file = tmp_path / "settings.json"
    project_file.write_text("{}", encoding="utf-8")

    resolved = resolve_project_path(tmp_path, "settings.json")

    assert resolved == project_file.resolve()


def test_resolve_project_path_rejects_escape(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()

    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")

    with pytest.raises(InputValidationError):
        resolve_project_path(project, "../outside.txt")


def test_resolve_project_path_rejects_missing_file(tmp_path: Path):
    with pytest.raises(InputValidationError):
        resolve_project_path(tmp_path, "missing.txt")