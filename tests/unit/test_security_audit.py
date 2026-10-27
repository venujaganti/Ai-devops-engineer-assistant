from pathlib import Path

from devops_ai.security.security_audit import SecurityAuditor


def test_detects_hardcoded_password_without_exposing_value(
    tmp_path: Path,
):
    project_file = tmp_path / "settings.py"
    project_file.write_text(
        'password = "do-not-print-this-secret"\n',
        encoding="utf-8",
    )

    result = SecurityAuditor(tmp_path).scan()

    assert any(
        finding.rule_id == "SEC001"
        for finding in result.findings
    )

    report_text = str(result.to_dict())
    assert "do-not-print-this-secret" not in report_text


def test_detects_permissive_ingress_rule(tmp_path: Path):
    project_file = tmp_path / "network.tf"
    project_file.write_text(
        'cidr_blocks = ["0.0.0.0/0"]\n',
        encoding="utf-8",
    )

    result = SecurityAuditor(tmp_path).scan()

    assert any(
        finding.rule_id == "SEC002"
        for finding in result.findings
    )


def test_detects_privileged_container_setting(tmp_path: Path):
    project_file = tmp_path / "deployment.yaml"
    project_file.write_text(
        "securityContext:\n  privileged: true\n",
        encoding="utf-8",
    )

    result = SecurityAuditor(tmp_path).scan()

    assert any(
        finding.rule_id == "SEC003"
        for finding in result.findings
    )


def test_detects_latest_image_tag(tmp_path: Path):
    project_file = tmp_path / "deployment.yaml"
    project_file.write_text(
        "image: nginx:latest\n",
        encoding="utf-8",
    )

    result = SecurityAuditor(tmp_path).scan()

    assert any(
        finding.rule_id == "SEC004"
        for finding in result.findings
    )


def test_skips_ignored_directories(tmp_path: Path):
    ignored = tmp_path / ".git"
    ignored.mkdir()
    (ignored / "config.py").write_text(
        'password = "hidden-value"\n',
        encoding="utf-8",
    )

    result = SecurityAuditor(tmp_path).scan()

    assert result.scanned_files == 0
    assert not result.findings


def test_report_contains_limitations(tmp_path: Path):
    result = SecurityAuditor(tmp_path).scan()
    report = result.to_dict()

    assert report["project_root"] == str(tmp_path.resolve())
    assert report["scanned_files"] == 0
    assert report["limitations"]