from src.devops_ai.integrations.base import IntegrationResult
from src.devops_ai.integrations.command_runner import SafeCommandRunner


class PodmanIntegration:
    def __init__(self, runner=None):
        self.runner = runner or SafeCommandRunner()

    def inspect_status(self) -> IntegrationResult:
        result = self.runner.run("podman", "version")

        return IntegrationResult(
            tool="Podman",
            operation="version",
            success=result.success,
            summary=(
                "Podman is available."
                if result.success
                else result.error
            ),
            output=result.stdout or result.stderr,
        )

    def list_containers(self) -> IntegrationResult:
        result = self.runner.run("podman", "ps")

        return IntegrationResult(
            tool="Podman",
            operation="list-running-containers",
            success=result.success,
            summary=(
                "Container status retrieved."
                if result.success
                else result.error
            ),
            output=result.stdout or result.stderr,
        )

    def list_images(self) -> IntegrationResult:
        result = self.runner.run("podman", "images")

        return IntegrationResult(
            tool="Podman",
            operation="list-images",
            success=result.success,
            summary=(
                "Image inventory retrieved."
                if result.success
                else result.error
            ),
            output=result.stdout or result.stderr,
        )