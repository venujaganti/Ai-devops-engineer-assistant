import json
import math
import os
import tempfile
from pathlib import Path


class LocalVectorStore:
    def __init__(self, index_path: Path):
        self.index_path = Path(index_path)
        self.records = []

    def load(self) -> None:
        if not self.index_path.exists():
            self.records = []
            return

        try:
            data = json.loads(
                self.index_path.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError("Vector index is unreadable") from exc

        if not isinstance(data, dict) or data.get("version") != 1:
            raise ValueError("Unsupported vector index format")

        records = data.get("records")

        if not isinstance(records, list):
            raise ValueError("Vector index records are invalid")

        for record in records:
            if not isinstance(record, dict):
                raise ValueError("Invalid vector record")

            vector = record.get("embedding")
            text = record.get("text")
            source = record.get("source")

            if (
                not isinstance(vector, list)
                or not vector
                or not isinstance(text, str)
                or not isinstance(source, str)
            ):
                raise ValueError("Invalid vector record fields")

            if not all(
                isinstance(value, (int, float))
                and math.isfinite(value)
                for value in vector
            ):
                raise ValueError("Invalid vector values")

        self.records = records

    def upsert(self, records: list[dict]) -> None:
        by_id = {
            record["chunk_id"]: record
            for record in self.records
        }

        for record in records:
            by_id[record["chunk_id"]] = record

        self.records = list(by_id.values())

    def save(self) -> None:
        self.index_path.parent.mkdir(
            parents=True, exist_ok=True
        )

        payload = {
            "version": 1,
            "records": self.records,
        }

        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.index_path.parent,
                delete=False,
                suffix=".tmp",
            ) as handle:
                json.dump(payload, handle, ensure_ascii=False)
                handle.flush()
                os.fsync(handle.fileno())
                temp_path = Path(handle.name)

            os.replace(temp_path, self.index_path)
        finally:
            if temp_path and temp_path.exists():
                temp_path.unlink()

    @staticmethod
    def cosine_similarity(a: list[float], b: list[float]) -> float:
        if not a or len(a) != len(b):
            raise ValueError("Embedding dimensions do not match")

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        min_similarity: float = 0.25,
    ) -> list[dict]:
        if top_k < 1:
            raise ValueError("top_k must be positive")

        matches = []

        for record in self.records:
            score = self.cosine_similarity(
                query_embedding,
                record["embedding"],
            )

            if score >= min_similarity:
                matches.append({**record, "score": score})

        return sorted(
            matches,
            key=lambda item: item["score"],
            reverse=True,
        )[:top_k]