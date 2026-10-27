import pytest

from src.devops_ai.assistant.task_classifier import classify_task


def test_classifies_kubernetes_task():
    result = classify_task("Why is my Kubernetes pod failing?")

    assert result.category == "kubernetes"


def test_classifies_terraform_task():
    result = classify_task("Review my Terraform plan")

    assert result.category == "terraform"


def test_detects_potentially_destructive_request():
    result = classify_task("Run terraform destroy in production")

    assert result.requires_caution is True


def test_rejects_empty_request():
    with pytest.raises(ValueError):
        classify_task(" ")