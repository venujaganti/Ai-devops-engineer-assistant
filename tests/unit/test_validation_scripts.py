"""Regression tests for command-line validation scripts."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_validate_config_runs_outside_repository_root(tmp_path: Path) -> None:
    env = os.environ.copy()
    env.pop("GEMINI_API_KEY", None)

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_config.py")],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
    )

    assert result.returncode == 0, result.stderr
    assert "Configuration validation passed." in result.stdout
    assert "Gemini API key configured: False" in result.stdout


def test_validate_docs_runs_outside_repository_root(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_docs.py")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
    )

    assert result.returncode == 0, result.stderr
    assert "11 categories" in result.stdout
