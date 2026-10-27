from src.devops_ai.knowledge.embeddings import GeminiEmbeddings
from src.devops_ai.knowledge.vector_store import LocalVectorStore


class KnowledgeRetriever:
    def __init__(
        self,
        store: LocalVectorStore,
        embeddings: GeminiEmbeddings,
        top_k: int = 5,
        min_similarity: float = 0.25,
    ):
        self.store = store
        self.embeddings = embeddings
        self.top_k = top_k
        self.min_similarity = min_similarity

    def retrieve(self, question: str) -> list[dict]:
        if not question or not question.strip():
            raise ValueError("Question must not be empty")

        query_vector = self.embeddings.embed(question)

        return self.store.search(
            query_embedding=query_vector,
            top_k=self.top_k,
            min_similarity=self.min_similarity,
        )