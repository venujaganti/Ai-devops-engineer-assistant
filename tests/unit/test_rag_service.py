from pathlib import Path

from src.devops_ai.knowledge.rag_service import RAGService


class FakeEmbeddings:
    def embed(self, text):
        return [1.0, 0.0]


class FakeGeminiClient:
    def generate_reply(self, message, history):
        assert "REFERENCE MATERIAL" in message
        assert "approved deployment procedure" in message
        return "The deployment procedure is described in guide.md."


def test_rag_indexes_and_answers_from_local_document(tmp_path: Path):
    docs = tmp_path / "docs"
    indexes = tmp_path / "indexes"
    docs.mkdir()

    (docs / "guide.md").write_text(
        "approved deployment procedure",
        encoding="utf-8",
    )

    # Bypass normal initialization so the test needs no API key.
    service = RAGService.__new__(RAGService)

    from config.settings import get_settings
    from src.devops_ai.knowledge.document_loader import DocumentLoader
    from src.devops_ai.knowledge.vector_store import LocalVectorStore
    from src.devops_ai.knowledge.retriever import KnowledgeRetriever

    service.settings = get_settings()
    service.documents_dir = docs
    service.index_path = indexes / "knowledge_index.json"
    service.embeddings = FakeEmbeddings()
    service.gemini_client = FakeGeminiClient()
    service.store = LocalVectorStore(service.index_path)

    service.retriever = KnowledgeRetriever(
        store=service.store,
        embeddings=service.embeddings,
        top_k=5,
        min_similarity=0.25,
    )

    result = service.index_documents()

    assert result["documents_loaded"] == 1
    assert result["chunks_indexed"] >= 1

    answer = service.answer("What is the deployment procedure?")

    assert "guide.md" in answer["answer"]
    assert answer["sources"]