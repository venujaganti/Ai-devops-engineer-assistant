import pytest

from src.devops_ai.knowledge.chunker import chunk_document


def test_empty_document_returns_no_chunks():
    assert chunk_document("guide.md", "   ") == []


def test_short_document_returns_one_chunk():
    chunks = chunk_document("guide.md", "Terraform plan")

    assert len(chunks) == 1
    assert chunks[0].source == "guide.md"
    assert chunks[0].text == "Terraform plan"


def test_large_document_creates_multiple_chunks():
    text = "Deploy safely. " * 300

    chunks = chunk_document(
        "deployment.md",
        text,
        chunk_size=200,
        overlap=30,
    )

    assert len(chunks) > 1
    assert all(chunk.text for chunk in chunks)


def test_invalid_overlap_is_rejected():
    with pytest.raises(ValueError):
        chunk_document("guide.md", "some text", 100, 100)