from pathlib import Path

from src.devops_ai.integrations.terraform import TerraformIntegration


def test_terraform_rejects_directory_outside_project(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()

    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "main.tf").write_text(
        'terraform { required_version = ">= 1.5.0" }',
        encoding="utf-8",
    )

    result = TerraformIntegration(project).validate_configuration(outside)

    assert result.success is False
    assert "outside" in result.summary.lower()