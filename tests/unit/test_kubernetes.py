from unittest.mock import Mock

from src.devops_ai.integrations.command_runner import CommandResult
from src.devops_ai.integrations.kubernetes import KubernetesIntegration


def test_kubernetes_lists_pods_using_allowlisted_operation():
    runner = Mock()
    runner.run.return_value = CommandResult(
        success=True,
        returncode=0,
        stdout="NAME       READY   STATUS",
        stderr="",
    )

    result = KubernetesIntegration(runner).list_pods()

    assert result.success is True
    assert result.operation == "list-pods"
    runner.run.assert_called_once_with("kubectl", "get-pods")