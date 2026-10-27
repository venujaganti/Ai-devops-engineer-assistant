from pathlib import Path

from src.devops_ai.integrations.base import IntegrationResult
from src.devops_ai.integrations.command_runner import SafeCommandRunner


class TerraformIntegration:
    def __init__(self, project_root: Path, runner=None):
        self.project_root = Path(project_root).resolve()
        self.runner = runner or SafeCommandRunner()

    def inspect_version(self) -> IntegrationResult:
        result = self.runner.run("terraform", "version")

        return IntegrationResult(
            tool="Terraform",
            operation="version",
            success=result.success,
            summary=(
                "Terraform version retrieved."
                if result.success
                else result.error
            ),
            output=result.stdout or result.stderr,
        )

    def validate_configuration(self, working_directory: Path) -> IntegrationResult:
        target = Path(working_directory).resolve()

        if not target.is_relative_to(self.project_root):
            return IntegrationResult(
                tool="Terraform",
                operation="validate",
                success=False,
                summary="The Terraform directory is outside the approved project root.",
            )

        if not target.is_dir():
            return IntegrationResult(
                tool="Terraform",
                operation="validate",
                success=False,
                summary="The Terraform directory does not exist.",
            )

        if not any(target.glob("*.tf")):
            return IntegrationResult(
                tool="Terraform",
                operation="validate",
                success=False,
                summary="No Terraform configuration files were found.",
            )

        # This runner executes only from the process's current directory.
        # A dedicated working-directory-aware runner is needed before
        # enabling Terraform validation through this integration.
        return IntegrationResult(
            tool="Terraform",
            operation="validate",
            success=False,
            summary=(
                "Validation is not enabled yet: the shared runner does not "
                "support a controlled working directory."
            ),
            warnings=[
                "Do not run Terraform against an arbitrary directory."
            ],
        )