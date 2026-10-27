from src.devops_ai.ai.prompts import SYSTEM_INSTRUCTION


def test_prompt_covers_required_devops_platforms():
    required_terms = [
        "AWS",
        "Azure",
        "Google Cloud",
        "Docker",
        "Podman",
        "Kubernetes",
        "Jenkins",
        "Terraform",
        "Azure Pipelines",
        "Google Cloud Build",
        "Prometheus",
        "Grafana",
        "Trivy",
        "Gitleaks",
    ]

    for term in required_terms:
        assert term in SYSTEM_INSTRUCTION


def test_prompt_forbids_command_execution():
    assert "Do not execute commands" in SYSTEM_INSTRUCTION


def test_prompt_treats_retrieved_content_as_untrusted():
    assert "untrusted data" in SYSTEM_INSTRUCTION


def test_prompt_requires_honest_validation_claims():
    assert "without testing it" in SYSTEM_INSTRUCTION