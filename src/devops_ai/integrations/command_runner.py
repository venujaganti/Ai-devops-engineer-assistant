import os
import shutil
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandResult:
    success: bool
    returncode: int | None
    stdout: str
    stderr: str
    error: str = ""


# Fixed commands and argument shapes only.
# Do not add arbitrary command strings supplied by an LLM or user.
ALLOWED_COMMANDS = {
    ("podman", "version"): ("podman", "version"),
    ("podman", "ps"): ("podman", "ps", "--format", "json"),
    ("podman", "images"): ("podman", "images", "--format", "json"),
    ("kubectl", "version"): ("kubectl", "version", "--client=true", "-o", "json"),
    ("kubectl", "get-pods"): ("kubectl", "get", "pods", "-o", "wide"),
    ("kubectl", "get-nodes"): ("kubectl", "get", "nodes", "-o", "wide"),
    ("terraform", "version"): ("terraform", "version"),
    ("terraform", "validate"): ("terraform", "validate", "-no-color"),
    ("aws", "version"): ("aws", "--version"),
    ("az", "version"): ("az", "version", "--output", "json"),
    ("gcloud", "version"): ("gcloud", "version", "--format=json"),
    ("trivy", "version"): ("trivy", "--version"),
    ("gitleaks", "version"): ("gitleaks", "version"),
    ("jenkins", "health"): (),
}


class SafeCommandRunner:
    def __init__(self, timeout_seconds: int = 15, max_output_chars: int = 12000):
        if not 1 <= timeout_seconds <= 60:
            raise ValueError("Timeout must be between 1 and 60 seconds")

        if not 100 <= max_output_chars <= 50000:
            raise ValueError("Output limit must be between 100 and 50000")

        self.timeout_seconds = timeout_seconds
        self.max_output_chars = max_output_chars

    def run(self, tool: str, operation: str) -> CommandResult:
        key = (tool, operation)

        if key not in ALLOWED_COMMANDS:
            return CommandResult(
                success=False,
                returncode=None,
                stdout="",
                stderr="",
                error="Operation is not on the approved read-only allowlist.",
            )

        argv = ALLOWED_COMMANDS[key]

        if not argv:
            return CommandResult(
                success=False,
                returncode=None,
                stdout="",
                stderr="",
                error="This operation must use its dedicated integration.",
            )

        executable = shutil.which(argv[0])

        if executable is None:
            return CommandResult(
                success=False,
                returncode=None,
                stdout="",
                stderr="",
                error=f"Required tool is not installed: {argv[0]}",
            )

        # Do not inherit credential-bearing environment variables wholesale.
        # Preserve only basic process environment settings.
        env = {
            key: value
            for key, value in os.environ.items()
            if key.upper() in {
                "PATH", "SYSTEMROOT", "WINDIR", "HOME", "USERPROFILE",
                "TEMP", "TMP", "LANG", "LC_ALL",
            }
        }

        try:
            completed = subprocess.run(
                [executable, *argv[1:]],
                shell=False,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
                env=env,
                stdin=subprocess.DEVNULL,
            )

            stdout = completed.stdout[:self.max_output_chars]
            stderr = completed.stderr[:self.max_output_chars]

            return CommandResult(
                success=completed.returncode == 0,
                returncode=completed.returncode,
                stdout=stdout,
                stderr=stderr,
                error="" if completed.returncode == 0 else (
                    f"Command returned exit code {completed.returncode}"
                ),
            )

        except subprocess.TimeoutExpired:
            return CommandResult(
                success=False,
                returncode=None,
                stdout="",
                stderr="",
                error="Command timed out.",
            )
        except OSError:
            return CommandResult(
                success=False,
                returncode=None,
                stdout="",
                stderr="",
                error="Could not start the requested tool.",
            )