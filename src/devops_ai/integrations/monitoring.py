"""Monitoring-tool CLI availability checks."""
from src.devops_ai.integrations.base import IntegrationResult
from src.devops_ai.integrations.command_runner import SafeCommandRunner

class MonitoringIntegration:
    def __init__(self, runner=None): self.runner = runner or SafeCommandRunner()
    def check_cli(self, tool: str) -> IntegrationResult:
        commands = {"prometheus": ("promtool", "--version"), "grafana": ("grafana", "--version"), "trivy": ("trivy", "version")}
        key = tool.strip().casefold()
        if key not in commands:
            return IntegrationResult(tool="Monitoring", operation="cli-check", success=False, summary="Unsupported monitoring tool.")
        result = self.runner.run(*commands[key])
        return IntegrationResult(tool=key, operation="version", success=result.success, summary=f"{key} CLI is available." if result.success else result.error, output=result.stdout or result.stderr)
