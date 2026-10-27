"""Azure Pipelines documentation and CLI integration status."""
from src.devops_ai.integrations.base import IntegrationResult
from src.devops_ai.integrations.command_runner import SafeCommandRunner

class AzurePipelinesIntegration:
    def __init__(self, runner=None): self.runner = runner or SafeCommandRunner()
    def check_cli(self) -> IntegrationResult:
        result = self.runner.run("az", "pipelines", "--help")
        return IntegrationResult(tool="Azure Pipelines", operation="cli-check", success=result.success, summary="Azure Pipelines CLI extension is available." if result.success else result.error, output=result.stdout or result.stderr)
