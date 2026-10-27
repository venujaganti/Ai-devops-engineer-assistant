from src.devops_ai.knowledge.retriever import KnowledgeRetriever
from src.devops_ai.knowledge.vector_store import LocalVectorStore


class FakeEmbeddings:
    def embed(self, text):
        return [1.0, 0.0]


def test_retriever_returns_relevant_document():
    store = LocalVectorStore("unused.json")
    store.records = [
        {
            "chunk_id": "guide::1",
            "source": "guide.md",
            "chunk_number": 1,
            "text": "Kubernetes readiness probes",
            "embedding": [1.0, 0.0],
        },
        {
            "chunk_id": "other::1",
            "source": "other.md",
            "chunk_number": 1,
            "text": "Unrelated information",
            "embedding": [0.0, 1.0],
        },
    ]

    retriever = KnowledgeRetriever(
        store=store,
        embeddings=FakeEmbeddings(),
        top_k=3,
        min_similarity=0.5,
    )

    results = retriever.retrieve("How do readiness probes work?")

    assert len(results) == 1
    assert results[0]["source"] == "guide.md"


def test_retriever_rejects_empty_question():
    retriever = KnowledgeRetriever(
        store=LocalVectorStore("unused.json"),
        embeddings=FakeEmbeddings(),
    )

    try:
        retriever.retrieve(" ")
        assert False, "Expected ValueError"
    except ValueError:
        pass