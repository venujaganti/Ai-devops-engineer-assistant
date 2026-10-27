import pytest

from devops_ai.deployment.environment_validator import EnvironmentValidator


def test_missing_required_variable_blocks_readiness():
    validator = EnvironmentValidator(
        required_variables=("GEMINI_API_KEY",)
    )

    result = validator.validate({})

    assert result["status"] == "blocked"
    assert result["findings"][0]["code"] == "ENV_REQUIRED_MISSING"


def test_present_required_variable_passes_presence_check():
    validator = EnvironmentValidator(
        required_variables=("GEMINI_API_KEY",)
    )

    result = validator.validate({"GEMINI_API_KEY": "test-secret"})

    assert result["status"] == "ready"
    assert result["findings"] == []
    assert "test-secret" not in str(result)


def test_empty_value_counts_as_missing():
    validator = EnvironmentValidator(
        required_variables=("DATABASE_URL",)
    )

    result = validator.validate({"DATABASE_URL": "   "})

    assert result["status"] == "blocked"


def test_invalid_variable_name_is_rejected():
    with pytest.raises(ValueError):
        EnvironmentValidator(required_variables=("api-key",))


def test_duplicate_variable_names_are_rejected():
    with pytest.raises(ValueError):
        EnvironmentValidator(
            required_variables=("DATABASE_URL",),
            optional_variables=("DATABASE_URL",),
        )


def test_missing_optional_variable_is_informational():
    validator = EnvironmentValidator(
        optional_variables=("AWS_REGION",)
    )

    result = validator.validate({})

    assert result["status"] == "ready"
    assert result["findings"][0]["severity"] == "info"