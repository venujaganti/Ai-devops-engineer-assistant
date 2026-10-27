
import pytest


@pytest.fixture
def sample_finding() -> dict:
    return {
        "rule_id": "SEC-CONT-001",
        "severity": "high",
        "category": "container",
        "file_path": "podman-compose.yml",
        "line": 8,
        "message": "A privileged container setting was detected.",
        "recommendation": (
            "Remove privileged mode unless it is necessary and approved."
        ),
    }


@pytest.fixture
def sample_findings(sample_finding: dict) -> list[dict]:
    return [
        sample_finding,
        {
            "rule_id": "SEC-TF-002",
            "severity": "medium",
            "category": "network",
            "file_path": "terraform/network.tf",
            "line": 12,
            "message": "A rule may allow traffic from every IPv4 address.",
            "recommendation": "Restrict the source CIDR where possible.",
        },
    ]
