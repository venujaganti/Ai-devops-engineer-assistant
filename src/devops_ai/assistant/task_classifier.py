from dataclasses import dataclass


@dataclass(frozen=True)
class TaskClassification:
    category: str
    confidence: float
    requires_caution: bool


CATEGORY_KEYWORDS = {
    "kubernetes": (
        "kubernetes", "kubectl", "pod", "deployment",
        "service", "ingress", "helm",
    ),
    "terraform": (
        "terraform", "infrastructure as code", "terraform plan",
        "terraform apply", "state file",
    ),
    "cicd": (
        "jenkins", "github actions", "pipeline", "ci/cd",
        "azure pipelines", "cloud build", "build failure",
    ),
    "containers": (
        "podman", "docker", "containerfile", "dockerfile",
        "container", "image build",
    ),
    "cloud": (
        "aws", "azure", "gcp", "cloud", "ec2", "iam",
        "vpc", "s3", "load balancer",
    ),
    "security": (
        "trivy", "gitleaks", "sonarqube", "vulnerability",
        "secret scan", "dependency-check", "security scan",
    ),
    "monitoring": (
        "prometheus", "grafana", "alertmanager", "loki",
        "logs", "metrics", "alert",
    ),
    "troubleshooting": (
        "error", "failed", "failure", "debug", "troubleshoot",
        "not working", "crash", "timeout",
    ),
}

CAUTION_KEYWORDS = (
    "delete",
    "destroy",
    "terminate",
    "drop database",
    "production",
    "rotate credentials",
    "revoke",
    "terraform apply",
    "kubectl delete",
    "rm -rf",
)


def classify_task(message: str) -> TaskClassification:
    if not isinstance(message, str) or not message.strip():
        raise ValueError("A non-empty task description is required")

    normalized = message.casefold()
    scores = {
        category: sum(
            1 for keyword in keywords if keyword in normalized
        )
        for category, keywords in CATEGORY_KEYWORDS.items()
    }

    highest = max(scores.values(), default=0)

    if highest == 0:
        category = "general"
        confidence = 0.5
    else:
        winners = [
            name for name, score in scores.items()
            if score == highest
        ]
        category = winners[0] if len(winners) == 1 else "multi-domain"
        confidence = min(0.95, 0.55 + highest * 0.1)

    requires_caution = any(
        keyword in normalized for keyword in CAUTION_KEYWORDS
    )

    return TaskClassification(
        category=category,
        confidence=confidence,
        requires_caution=requires_caution,
    )