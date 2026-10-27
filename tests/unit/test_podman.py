from unittest.mock import Mock

from src.devops_ai.integrations.command_runner import CommandResult
from src.devops_ai.integrations.podman import PodmanIntegration


def test_podman_status():
    runner = Mock()
    runner.run.return_value = CommandResult(
        success=True,
        returncode=0,
        stdout="Podman version 5.x",
        stderr="",
    )

    result = PodmanIntegration(runner).inspect_status()

    assert result.success is True
    assert result.tool == "Podman"
    assert "Podman version" in result.output