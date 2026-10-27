import pytest

from config.settings import get_settings


def test_default_settings(monkeypatch):
    for key in (
        "APP_NAME",
        "APP_ENV",
        "LOG_LEVEL",
        "GEMINI_API_KEY",
        "GEMINI_MODEL",
        "COMMAND_EXECUTION_ENABLED",
        "REQUIRE_COMMAND_APPROVAL",
        "COMMAND_TIMEOUT_SECONDS",
    ):
        monkeypatch.delenv(key, raising=False)

    settings = get_settings()

    assert settings.app_name == "AI DevOps Engineer Assistant"
    assert settings.app_env == "development"
    assert settings.log_level == "INFO"
    assert settings.gemini_api_key == ""
    assert settings.command_execution_enabled is False
    assert settings.require_command_approval is True
    assert settings.command_timeout_seconds == 30


def test_invalid_timeout_is_rejected(monkeypatch):
    monkeypatch.setenv("COMMAND_TIMEOUT_SECONDS", "invalid")

    with pytest.raises(ValueError, match="must be an integer"):
        get_settings()


def test_timeout_outside_allowed_range_is_rejected(monkeypatch):
    monkeypatch.setenv("COMMAND_TIMEOUT_SECONDS", "301")

    with pytest.raises(ValueError, match="between 1 and 300"):
        get_settings()


def test_invalid_execution_flag_is_rejected(monkeypatch):
    monkeypatch.setenv("COMMAND_EXECUTION_ENABLED", "sometimes")

    with pytest.raises(ValueError, match="must be true or false"):
        get_settings()