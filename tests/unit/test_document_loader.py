from pathlib import Path

import pytest

from src.devops_ai.knowledge.document_loader import DocumentLoader


def test_load_markdown_file(tmp_path: Path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "guide.md").write_text(
        "# Kubernetes\nUse readiness probes.",
        encoding="utf-8",
    )

    result = DocumentLoader().load_file(docs / "guide.md", docs)

    assert result.source == "guide.md"
    assert "readiness probes" in result.text


def test_reject_file_outside_approved_directory(tmp_path: Path):
    docs = tmp_path / "docs"
    docs.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("not approved", encoding="utf-8")

    with pytest.raises(ValueError):
        DocumentLoader().load_file(outside, docs)


def test_reject_oversized_file(tmp_path: Path):
    docs = tmp_path / "docs"
    docs.mkdir()
    file_path = docs / "large.md"
    file_path.write_text("x" * 100, encoding="utf-8")

    loader = DocumentLoader(max_document_mb=1)
    loader.max_bytes = 50

    with pytest.raises(ValueError):
        loader.load_file(file_path, docs)