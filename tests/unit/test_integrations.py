from unittest.mock import Mock

from src.devops_ai.integrations.cloud import CloudCLIIntegration
from src.devops_ai.integrations.command_runner import CommandResult
from src.devops_ai.integrations.security_scanners import (
    SecurityScannerIntegration,
)


def test_cloud_rejects_unknown_provider():
    result = CloudCLIIntegration().check_cli("unknown")

    assert result.success is False
    assert "Unsupported" in result.summary


def test_security_scanner_rejects_unknown_tool():
    result = SecurityScannerIntegration().check_version("unknown")

    assert result.success is False


def test_aws_cli_check_uses_allowlisted_command():
    runner = Mock()
    runner.run.return_value = CommandResult(
        success=True,
        returncode=0,
        stdout="aws-cli/2.x",
        stderr="",
    )

    result = CloudCLIIntegration(runner).check_cli("aws")

    assert result.success is True
    runner.run.assert_called_once_with("aws", "version")