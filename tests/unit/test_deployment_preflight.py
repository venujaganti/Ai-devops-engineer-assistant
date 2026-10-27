from pathlib import Path

from devops_ai.deployment.deployment_preflight import DeploymentPreflight
from devops_ai.deployment.environment_validator import EnvironmentValidator


class FakeRepositoryScanner:
    def scan(self):
        return {
            "status": "completed",
            "findings": [
                {
                    "rule_id": "TEST001",
                    "severity": "medium",
                    "message": "Example repository finding",
                }
            ],
            "limitations": [],
        }


def test_preflight_combines_all_sections(tmp_path: Path):
    validator = EnvironmentValidator(
        required_variables=("APP_ENV",)
    )
    preflight = DeploymentPreflight(
        project_root=tmp_path,
        environment_validator=validator,
        repository_scanner=FakeRepositoryScanner(),
    )

    result = preflight.run({"APP_ENV": "test"})

    assert set(result["sections"]) == {
        "environment",
        "containers",
        "repository",
    }
    assert result["summary"]["total_findings"] >= 1
    assert result["status"] == "review_required"


def test_missing_required_environment_blocks_preflight(tmp_path: Path):
    validator = EnvironmentValidator(
        required_variables=("APP_ENV",)
    )
    preflight = DeploymentPreflight(
        project_root=tmp_path,
        environment_validator=validator,
    )

    result = preflight.run({})

    assert result["status"] == "blocked"
    assert result["summary"]["blocking_findings"] >= 1


def test_nonexistent_project_root_is_rejected(tmp_path: Path):
    missing = tmp_path / "not-created"

    try:
        DeploymentPreflight(project_root=missing)
    except ValueError as exc:
        assert "existing directory" in str(exc)
    else:
        raise AssertionError("Expected ValueError for nonexistent project root")