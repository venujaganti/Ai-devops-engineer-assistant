import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_env: str
    log_level: str
    gemini_api_key: str
    gemini_model: str
    gemini_max_output_tokens: int
    gemini_temperature: float
    gemini_max_history_messages: int
    command_execution_enabled: bool
    require_command_approval: bool
    command_timeout_seconds: int
    gemini_embedding_model: str
    rag_chunk_size: int
    rag_chunk_overlap: int
    rag_top_k: int
    rag_min_similarity: float
    rag_max_document_mb: int
    rag_max_files: int
    rag_max_context_chars: int


def _read_int(name: str, default: str, minimum: int, maximum: int) -> int:
    raw_value = os.getenv(name, default)

    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer.") from exc

    if not minimum <= value <= maximum:
        raise ValueError(
            f"{name} must be between {minimum} and {maximum}."
        )

    return value


def _read_bool(name: str, default: str) -> bool:
    value = os.getenv(name, default).strip().lower()

    if value not in {"true", "false"}:
        raise ValueError(f"{name} must be true or false.")

    return value == "true"



def _read_float(name: str, default: str, minimum: float, maximum: float) -> float:
    raw_value = os.getenv(name, default)
    try:
        value = float(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number.") from exc
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}.")
    return value


def get_settings() -> Settings:
    load_dotenv()

    timeout = _read_int("COMMAND_TIMEOUT_SECONDS", "30", 1, 300)
    chunk_size = _read_int("RAG_CHUNK_SIZE", "1200", 100, 20000)
    chunk_overlap = _read_int("RAG_CHUNK_OVERLAP", "200", 0, 19999)
    if chunk_overlap >= chunk_size:
        raise ValueError("RAG_CHUNK_OVERLAP must be smaller than RAG_CHUNK_SIZE.")
    max_tokens = _read_int(
        "GEMINI_MAX_OUTPUT_TOKENS", "2048", 128, 8192
    )
    max_history = _read_int(
        "GEMINI_MAX_HISTORY_MESSAGES", "12", 2, 30
    )

    try:
        temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.2"))
    except ValueError as exc:
        raise ValueError(
            "GEMINI_TEMPERATURE must be a number."
        ) from exc

    if not 0.0 <= temperature <= 2.0:
        raise ValueError(
            "GEMINI_TEMPERATURE must be between 0 and 2."
        )

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ValueError("LOG_LEVEL is not a supported logging level.")

    return Settings(
        app_name=os.getenv(
            "APP_NAME", "AI DevOps Engineer Assistant"
        ),
        app_env=os.getenv("APP_ENV", "development"),
        log_level=log_level,
        gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
        gemini_model=os.getenv(
            "GEMINI_MODEL", "gemini-2.5-flash"
        ).strip(),
        gemini_max_output_tokens=max_tokens,
        gemini_temperature=temperature,
        gemini_max_history_messages=max_history,
        command_execution_enabled=_read_bool(
            "COMMAND_EXECUTION_ENABLED", "false"
        ),
        require_command_approval=_read_bool(
            "REQUIRE_COMMAND_APPROVAL", "true"
        ),
        command_timeout_seconds=timeout,
        gemini_embedding_model=os.getenv(
            "GEMINI_EMBEDDING_MODEL", "gemini-embedding-001"
        ).strip(),
        rag_chunk_size=chunk_size,
        rag_chunk_overlap=chunk_overlap,
        rag_top_k=_read_int("RAG_TOP_K", "5", 1, 50),
        rag_min_similarity=_read_float("RAG_MIN_SIMILARITY", "0.25", 0.0, 1.0),
        rag_max_document_mb=_read_int("RAG_MAX_DOCUMENT_MB", "10", 1, 100),
        rag_max_files=_read_int("RAG_MAX_FILES", "200", 1, 10000),
        rag_max_context_chars=_read_int("RAG_MAX_CONTEXT_CHARS", "18000", 1000, 100000),
    )
