from devops_ai.security.secret_redactor import (
    REDACTED,
    redact_secrets,
    redact_text,
)


def test_redacts_bearer_token():
    result = redact_text("Authorization: Bearer abc.def.ghi")

    assert "abc.def.ghi" not in result
    assert REDACTED in result


def test_redacts_secret_assignment():
    result = redact_text('password="super-secret-value"')

    assert "super-secret-value" not in result
    assert REDACTED in result


def test_redacts_aws_access_key():
    result = redact_text("key=AKIA1234567890ABCDEF")

    assert "AKIA1234567890ABCDEF" not in result
    assert REDACTED in result


def test_redacts_sensitive_dictionary_keys():
    source = {
        "username": "devops-user",
        "api_key": "private-value",
        "nested": {"client_secret": "another-private-value"},
    }

    result = redact_secrets(source)

    assert result["username"] == "devops-user"
    assert result["api_key"] == REDACTED
    assert result["nested"]["client_secret"] == REDACTED

    # Original object is not modified.
    assert source["api_key"] == "private-value"


def test_redacts_nested_lists():
    result = redact_secrets(
        [{"password": "hidden-value"}, "Bearer token-value"]
    )

    assert result[0]["password"] == REDACTED
    assert "token-value" not in result[1]


def test_does_not_modify_non_string_values():
    assert redact_secrets(42) == 42
    assert redact_secrets(None) is None