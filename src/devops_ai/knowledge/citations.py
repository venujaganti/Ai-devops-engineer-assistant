"""Citation formatting for retrieved document chunks."""
from collections.abc import Mapping

def format_citation(source: str, chunk_number: int | str | None = None) -> str:
    clean_source = str(source).strip() or "Unknown source"
    return f"{clean_source} (chunk {chunk_number})" if chunk_number is not None else clean_source

def cite_result(result: Mapping[str, object]) -> str:
    return format_citation(str(result.get("source", "Unknown source")), result.get("chunk"))
