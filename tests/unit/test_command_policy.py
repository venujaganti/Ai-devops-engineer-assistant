import pytest

from src.devops_ai.assistant.command_policy import assess_command


def test_terraform_destroy_is_high_risk():
    result = assess_command("terraform destroy")

    assert result.risk_level == "high"
    assert result.requires_human_review is True


def test_kubectl_apply_is_medium_risk():
    result = assess_command("kubectl apply -f deployment.yaml")

    assert result.risk_level == "medium"


def test_read_only_command_is_not_flagged_by_known_patterns():
    result = assess_command("kubectl get pods")

    assert result.risk_level == "low"
    assert result.requires_human_review is True


def test_empty_command_is_rejected():
    with pytest.raises(ValueError):
        assess_command("")


def test_overlong_command_is_rejected():
    with pytest.raises(ValueError):
        assess_command("x" * 4001)