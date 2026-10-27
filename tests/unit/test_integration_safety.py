
from unittest.mock import Mock

import pytest

from src.devops_ai.integrations.command_runner import SafeCommandRunner
from src.devops_ai.integrations.terraform import TerraformIntegration


def test_command_runner_rejects_unapproved_operation():
    runner = SafeCommandRunner()

    result = runner.run("podman", "delete-everything")

    assert result.success is False


def test_terraform_rejects_path_outside_project(tmp_path):
    project_root = tmp_path / "project"
    outside = tmp_path / "outside"
    project_root.mkdir()
    outside.mkdir()

    runner = Mock()
    integration = TerraformIntegration(project_root, runner)

    result = integration.validate_configuration(outside)

    assert result.success is False
    runner.run.assert_not_called()
