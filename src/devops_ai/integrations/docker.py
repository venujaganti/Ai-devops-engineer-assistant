"""Docker CLI availability check; Podman remains the preferred runtime."""
from src.devops_ai.integrations.base import IntegrationResult
from src.devops_ai.integrations.command_runner import SafeCommandRunner

class DockerIntegration:
    def __init__(self, runner=None):
        self.runner = runner or SafeCommandRunner()
    def check_cli(self) -> IntegrationResult:
        result = self.runner.run("docker", "--version")
        return IntegrationResult(tool="Docker", operation="version", success=result.success, summary="Docker CLI is available." if result.success else result.error, output=result.stdout or result.stderr)
