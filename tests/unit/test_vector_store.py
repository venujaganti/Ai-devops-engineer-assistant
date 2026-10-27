import pytest

from src.devops_ai.knowledge.vector_store import LocalVectorStore


def test_store_save_and_load(tmp_path):
    store = LocalVectorStore(tmp_path / "index.json")
    store.upsert(
        [
            {
                "chunk_id": "guide.md::chunk-1",
                "source": "guide.md",
                "chunk_number": 1,
                "text": "Kubernetes deployments",
                "embedding": [1.0, 0.0],
            }
        ]
    )
    store.save()

    loaded = LocalVectorStore(tmp_path / "index.json")
    loaded.load()

    assert len(loaded.records) == 1
    assert loaded.records[0]["source"] == "guide.md"


def test_cosine_similarity():
    score = LocalVectorStore.cosine_similarity(
        [1.0, 0.0],
        [1.0, 0.0],
    )
    assert score == pytest.approx(1.0)


def test_dimension_mismatch_is_rejected():
    with pytest.raises(ValueError):
        LocalVectorStore.cosine_similarity([1.0], [1.0, 0.0])


def test_search_returns_best_match():
    store = LocalVectorStore("unused.json")
    store.records = [
        {
            "chunk_id": "a",
            "source": "a.md",
            "chunk_number": 1,
            "text": "best match",
            "embedding": [1.0, 0.0],
        },
        {
            "chunk_id": "b",
            "source": "b.md",
            "chunk_number": 1,
            "text": "other match",
            "embedding": [0.0, 1.0],
        },
    ]

    results = store.search([1.0, 0.0], top_k=1, min_similarity=0.5)

    assert len(results) == 1
    assert results[0]["source"] == "a.md"