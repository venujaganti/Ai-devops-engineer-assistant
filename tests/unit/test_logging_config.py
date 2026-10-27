
import json
import logging

from src.devops_ai.observability.logging_config import (
    JsonFormatter,
    redact_sensitive,
)


def test_api_key_is_redacted():
    result = redact_sensitive("api_key=example-secret-value")
    assert "example-secret-value" not in result
    assert "[REDACTED]" in result


def test_bearer_token_is_redacted():
    result = redact_sensitive("Authorization: Bearer abc.def.ghi")
    assert "abc.def.ghi" not in result


def test_formatter_outputs_json():
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="Application started",
        args=(),
        exc_info=None,
    )

    result = json.loads(JsonFormatter().format(record))
    assert result["level"] == "INFO"
    assert result["message"] == "Application started"
