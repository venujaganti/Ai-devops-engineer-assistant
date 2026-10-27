"""Google Cloud Build CLI integration."""
from src.devops_ai.integrations.base import IntegrationResult
from src.devops_ai.integrations.command_runner import SafeCommandRunner

class GoogleCloudBuildIntegration:
    def __init__(self, runner=None): self.runner = runner or SafeCommandRunner()
    def check_cli(self) -> IntegrationResult:
        result = self.runner.run("gcloud", "builds", "--help")
        return IntegrationResult(tool="Google Cloud Build", operation="cli-check", success=result.success, summary="Cloud Build CLI command is available." if result.success else result.error, output=result.stdout or result.stderr)
