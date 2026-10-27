from unittest.mock import patch

from src.devops_ai.integrations.command_runner import SafeCommandRunner


def test_rejects_unapproved_operation():
    result = SafeCommandRunner().run("terraform", "destroy")

    assert result.success is False
    assert "allowlist" in result.error


def test_reports_missing_executable():
    with patch(
        "src.devops_ai.integrations.command_runner.shutil.which",
        return_value=None,
    ):
        result = SafeCommandRunner().run("podman", "version")

    assert result.success is False
    assert "not installed" in result.error


def test_successful_command():
    from subprocess import CompletedProcess

    with (
        patch(
            "src.devops_ai.integrations.command_runner.shutil.which",
            return_value="/usr/bin/podman",
        ),
        patch(
            "src.devops_ai.integrations.command_runner.subprocess.run",
            return_value=CompletedProcess(
                args=["podman", "version"],
                returncode=0,
                stdout="Podman version test",
                stderr="",
            ),
        ) as mock_run,
    ):
        result = SafeCommandRunner().run("podman", "version")

    assert result.success is True
    assert "Podman version" in result.stdout
    assert mock_run.call_args.kwargs["shell"] is False
    assert mock_run.call_args.kwargs["stdin"] is not None


def test_nonzero_exit_is_reported():
    from subprocess import CompletedProcess

    with (
        patch(
            "src.devops_ai.integrations.command_runner.shutil.which",
            return_value="/usr/bin/kubectl",
        ),
        patch(
            "src.devops_ai.integrations.command_runner.subprocess.run",
            return_value=CompletedProcess(
                args=["kubectl"],
                returncode=1,
                stdout="",
                stderr="context unavailable",
            ),
        ),
    ):
        result = SafeCommandRunner().run("kubectl", "get-pods")

    assert result.success is False
    assert result.returncode == 1