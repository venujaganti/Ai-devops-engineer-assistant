from src.devops_ai.integrations.base import IntegrationResult
from src.devops_ai.integrations.command_runner import SafeCommandRunner


class KubernetesIntegration:
    def __init__(self, runner=None):
        self.runner = runner or SafeCommandRunner()

    def inspect_client(self) -> IntegrationResult:
        result = self.runner.run("kubectl", "version")

        return IntegrationResult(
            tool="Kubernetes",
            operation="client-version",
            success=result.success,
            summary=(
                "Kubernetes client inspected."
                if result.success
                else result.error
            ),
            output=result.stdout or result.stderr,
        )

    def list_pods(self) -> IntegrationResult:
        result = self.runner.run("kubectl", "get-pods")

        return IntegrationResult(
            tool="Kubernetes",
            operation="list-pods",
            success=result.success,
            summary=(
                "Pod inventory retrieved."
                if result.success
                else result.error
            ),
            output=result.stdout or result.stderr,
            warnings=[
                "Output is scoped to the current kubectl context and namespace."
            ],
        )

    def list_nodes(self) -> IntegrationResult:
        result = self.runner.run("kubectl", "get-nodes")

        return IntegrationResult(
            tool="Kubernetes",
            operation="list-nodes",
            success=result.success,
            summary=(
                "Node inventory retrieved."
                if result.success
                else result.error
            ),
            output=result.stdout or result.stderr,
        )