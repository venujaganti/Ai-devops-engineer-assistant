from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    source: str
    text: str
    chunk_number: int


def chunk_document(
    source: str,
    text: str,
    chunk_size: int = 1200,
    overlap: int = 200,
) -> list[DocumentChunk]:
    if chunk_size < 1:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    text = text.strip()

    if not text:
        return []

    chunks = []
    start = 0
    number = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        # Prefer ending on a line or word boundary.
        if end < len(text):
            boundary = text.rfind("\n", start, end)

            if boundary <= start + chunk_size // 2:
                boundary = text.rfind(" ", start, end)

            if boundary > start + chunk_size // 2:
                end = boundary

        content = text[start:end].strip()

        if content:
            number += 1
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{source}::chunk-{number}",
                    source=source,
                    text=content,
                    chunk_number=number,
                )
            )

        if end >= len(text):
            break

        start = max(start + 1, end - overlap)

    return chunks