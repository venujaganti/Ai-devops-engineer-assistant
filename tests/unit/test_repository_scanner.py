
import json

import pytest

from src.devops_ai.integrations.repository_scanner import RepositoryScanner


def test_scanner_reads_supported_files_only(tmp_path):
    (tmp_path / "settings.json").write_text(
        json.dumps({"enabled": True}), encoding="utf-8"
    )
    (tmp_path / "notes.txt").write_text("not scanned", encoding="utf-8")

    result = RepositoryScanner(tmp_path).scan()

    assert result["scanned_file_count"] == 1
    assert result["scanned_files"] == ["settings.json"]


def test_scanner_skips_generated_directories(tmp_path):
    generated = tmp_path / ".git"
    generated.mkdir()
    (generated / "broken.json").write_text("{", encoding="utf-8")
    (tmp_path / "valid.json").write_text("{}", encoding="utf-8")

    result = RepositoryScanner(tmp_path).scan()

    assert result["scanned_files"] == ["valid.json"]


def test_scanner_rejects_missing_root(tmp_path):
    with pytest.raises(FileNotFoundError):
        RepositoryScanner(tmp_path / "does-not-exist")


def test_scanner_reports_oversized_file(tmp_path):
    (tmp_path / "large.json").write_text('{"data": "12345"}', encoding="utf-8")

    scanner = RepositoryScanner(tmp_path, max_file_bytes=5)
    result = scanner.scan()

    assert result["scanned_file_count"] == 0
    assert result["skipped_files"][0]["file"] == "large.json"
