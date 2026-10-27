import pytest

from src.devops_ai.ai.response_guard import (
    MAX_RESPONSE_CHARACTERS,
    validate_response,
)
from src.devops_ai.core.exceptions import GeminiServiceError


def test_valid_response_is_preserved():
    assert validate_response("  Terraform example  ") == (
        "Terraform example"
    )


@pytest.mark.parametrize("value", [None, "", "   ", "\n\t"])
def test_empty_response_is_rejected(value):
    with pytest.raises(GeminiServiceError):
        validate_response(value)


def test_oversized_response_is_truncated():
    result = validate_response("x" * (MAX_RESPONSE_CHARACTERS + 100))

    assert len(result) < MAX_RESPONSE_CHARACTERS + 100
    assert result.endswith("[Response shortened by the application.]")