"""Best-effort redaction of secrets from application output."""

from __future__ import annotations

import re
from typing import Any


REDACTED = "[REDACTED]"

_PATTERNS = [
    re.compile(
        r"(?i)\b(authorization\s*:\s*bearer)\s+[A-Za-z0-9._~+/=-]+"
    ),
    re.compile(
        r"(?i)\b(bearer)\s+[A-Za-z0-9._~+/=-]+"
    ),
    re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"
        r".*?"
        r"-----END (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
        re.DOTALL,
    ),
    re.compile(
        r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|"
        r"client[_-]?secret|password|passwd|secret[_-]?key)"
        r"(\s*[=:]\s*)"
        r"""(?:"[^"]*"|'[^']*'|[^\s,;]+)"""
    ),
    re.compile(
        r"\bAKIA[0-9A-Z]{16}\b"
    ),
]

_SECRET_KEY_PARTS = (
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "api-key",
    "apikey",
    "authorization",
    "private_key",
    "private-key",
    "access_key",
    "access-key",
)


def redact_text(value: str) -> str:
    """Redact common secret formats in text."""
    result = value

    for pattern in _PATTERNS:
        result = pattern.sub(
            lambda match: (
                match.group(1) + match.group(2) + REDACTED
                if pattern is _PATTERNS[3]
                else REDACTED
            ),
            result,
        )

    return result


def _is_sensitive_key(key: object) -> bool:
    normalized = str(key).lower().replace(" ", "_")
    return any(part in normalized for part in _SECRET_KEY_PARTS)


def redact_secrets(value: Any) -> Any:
    """Recursively redact secrets in common JSON-compatible data.

    Returns a new object and does not mutate the input.
    """
    if isinstance(value, str):
        return redact_text(value)

    if isinstance(value, dict):
        result = {}

        for key, item in value.items():
            if _is_sensitive_key(key):
                result[key] = REDACTED
            else:
                result[key] = redact_secrets(item)

        return result

    if isinstance(value, list):
        return [redact_secrets(item) for item in value]

    if isinstance(value, tuple):
        return tuple(redact_secrets(item) for item in value)

    return value