from src.devops_ai.integrations.base import IntegrationResult
from src.devops_ai.integrations.command_runner import SafeCommandRunner


class SecurityScannerIntegration:
    def __init__(self, runner=None):
        self.runner = runner or SafeCommandRunner()

    def check_version(self, scanner: str) -> IntegrationResult:
        supported = {
            "trivy": ("trivy", "version"),
            "gitleaks": ("gitleaks", "version"),
        }

        scanner = scanner.casefold().strip()

        if scanner not in supported:
            return IntegrationResult(
                tool="Security Scanner",
                operation="version",
                success=False,
                summary="Scanner is not supported by this integration.",
            )

        tool, operation = supported[scanner]
        result = self.runner.run(tool, operation)

        return IntegrationResult(
            tool=scanner,
            operation="version",
            success=result.success,
            summary=(
                f"{scanner} is installed."
                if result.success
                else result.error
            ),
            output=result.stdout or result.stderr,
        )