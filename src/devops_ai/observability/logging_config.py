
import json
import logging
import os
import re
from datetime import datetime, timezone
from typing import Any


_SECRET_PATTERNS = [
    re.compile(
        r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|"
        r"password|client[_-]?secret|secret[_-]?key)\b"
        r"(\s*[:=]\s*)"
        r"(['\"]?)[^\s,'\"}]+"
    ),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?"
               r"-----END [A-Z ]*PRIVATE KEY-----", re.DOTALL),
]


def redact_sensitive(value: Any) -> str:
    text = str(value)
    for pattern in _SECRET_PATTERNS:
        if "PRIVATE KEY" in pattern.pattern:
            text = pattern.sub("[REDACTED_PRIVATE_KEY]", text)
        elif "Bearer" in pattern.pattern:
            text = pattern.sub("Bearer [REDACTED]", text)
        else:
            text = pattern.sub(r"\1\2[REDACTED]", text)
    return text


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": redact_sensitive(record.getMessage()),
        }

        # Only include explicitly supplied, approved scalar fields.
        fields = getattr(record, "event_fields", {})
        if isinstance(fields, dict):
            for key, value in fields.items():
                if key in {"request_id", "component", "operation", "status"}:
                    payload[key] = redact_sensitive(value)[:200]

        if record.exc_info:
            # Avoid emitting exception messages or local variables that may
            # contain credentials. Keep exception class only.
            exc_type = record.exc_info[0]
            payload["exception_type"] = (
                exc_type.__name__ if exc_type else "UnknownException"
            )

        return json.dumps(payload, ensure_ascii=True)


def configure_logging(level: str | None = None) -> None:
    selected = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    numeric_level = getattr(logging, selected, logging.INFO)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(numeric_level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_event(
    logger: logging.Logger,
    level: int,
    message: str,
    **fields: Any,
) -> None:
    approved = {
        key: value
        for key, value in fields.items()
        if key in {"request_id", "component", "operation", "status"}
    }
    logger.log(level, message, extra={"event_fields": approved})
