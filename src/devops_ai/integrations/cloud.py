from src.devops_ai.integrations.base import IntegrationResult
from src.devops_ai.integrations.command_runner import SafeCommandRunner


class CloudCLIIntegration:
    def __init__(self, runner=None):
        self.runner = runner or SafeCommandRunner()

    def check_cli(self, provider: str) -> IntegrationResult:
        operations = {
            "aws": ("aws", "version"),
            "azure": ("az", "version"),
            "gcp": ("gcloud", "version"),
        }

        provider = provider.casefold().strip()

        if provider not in operations:
            return IntegrationResult(
                tool="Cloud",
                operation="cli-check",
                success=False,
                summary="Unsupported cloud provider.",
            )

        tool, operation = operations[provider]
        result = self.runner.run(tool, operation)

        return IntegrationResult(
            tool=provider.upper(),
            operation="cli-version",
            success=result.success,
            summary=(
                f"{provider.upper()} CLI is available."
                if result.success
                else result.error
            ),
            output=result.stdout or result.stderr,
            warnings=[
                "CLI availability does not confirm account access or permissions."
            ],
        )