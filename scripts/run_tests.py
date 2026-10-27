"""Run the project's offline unit and integration test suite."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    command = [
        sys.executable,
        "-m",
        "pytest",
        "tests/unit",
        "tests/integration",
        *sys.argv[1:],
    ]
    raise SystemExit(subprocess.call(command, cwd=ROOT))
