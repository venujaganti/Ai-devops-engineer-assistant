from pathlib import Path

from devops_ai.deployment.container_readiness import (
    ContainerReadinessChecker,
)


def test_empty_project_is_reported_without_crashing(tmp_path: Path):
    result = ContainerReadinessChecker(tmp_path).check()

    assert result["status"] == "ready"
    assert result["build_files"] == []
    assert result["compose_files"] == []


def test_containerfile_without_from_is_blocked(tmp_path: Path):
    (tmp_path / "Containerfile").write_text(
        "RUN echo test\n",
        encoding="utf-8",
    )

    result = ContainerReadinessChecker(tmp_path).check()

    codes = {item["code"] for item in result["findings"]}
    assert "CONTAINER_FROM_MISSING" in codes
    assert result["status"] == "blocked"


def test_latest_base_image_is_flagged(tmp_path: Path):
    (tmp_path / "Containerfile").write_text(
        "FROM python:latest\n"
        "CMD [\"python\", \"--version\"]\n",
        encoding="utf-8",
    )

    result = ContainerReadinessChecker(tmp_path).check()

    codes = {item["code"] for item in result["findings"]}
    assert "CONTAINER_LATEST_TAG" in codes


def test_privileged_compose_service_is_blocked(tmp_path: Path):
    (tmp_path / "podman-compose.yml").write_text(
        "services:\n"
        "  app:\n"
        "    image: example/app:1.0\n"
        "    privileged: true\n",
        encoding="utf-8",
    )

    result = ContainerReadinessChecker(tmp_path).check()

    assert result["status"] == "blocked"
    assert any(
        item["code"] == "COMPOSE_PRIVILEGED"
        for item in result["findings"]
    )


def test_ignore_file_is_detected(tmp_path: Path):
    (tmp_path / "Containerfile").write_text(
        "FROM python:3.12-slim\n",
        encoding="utf-8",
    )
    (tmp_path / ".containerignore").write_text(
        ".git\n.env\n",
        encoding="utf-8",
    )

    result = ContainerReadinessChecker(tmp_path).check()

    assert ".containerignore" in result["ignore_files"]
    assert not any(
        item["code"] == "CONTAINER_IGNORE_MISSING"
        for item in result["findings"]
    )