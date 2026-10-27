
from src.devops_ai.observability.health import (
    application_liveness,
    configuration_readiness,
    run_health_checks,
)
from src.devops_ai.observability.metrics import MetricsRegistry


class DiagnosticService:
    def __init__(self, metrics: MetricsRegistry) -> None:
        self.metrics = metrics

    def create_report(self) -> dict:
        health = run_health_checks({
            "application": application_liveness,
            "configuration": configuration_readiness,
        })

        return {
            "health": health.to_dict(),
            "metrics": self.metrics.snapshot(),
            "security_notes": [
                "Metrics do not intentionally include prompts or credentials.",
                "Health checks do not prove cloud or deployment availability.",
                "In-memory metrics reset when the process restarts.",
            ],
        }
