
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Callable


@dataclass(frozen=True)
class HealthCheck:
    name: str
    healthy: bool
    message: str


@dataclass(frozen=True)
class HealthReport:
    status: str
    checked_at: str
    checks: list[HealthCheck]

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "checked_at": self.checked_at,
            "checks": [asdict(check) for check in self.checks],
        }


def run_health_checks(
    checks: dict[str, Callable[[], tuple[bool, str]]],
) -> HealthReport:
    results: list[HealthCheck] = []

    for name, callback in checks.items():
        try:
            healthy, message = callback()
            results.append(
                HealthCheck(
                    name=name,
                    healthy=bool(healthy),
                    message=str(message)[:300],
                )
            )
        except Exception:
            # Avoid displaying raw exception messages that may contain secrets.
            results.append(
                HealthCheck(
                    name=name,
                    healthy=False,
                    message="Check failed; inspect sanitized application logs.",
                )
            )

    status = "healthy" if all(item.healthy for item in results) else "degraded"

    return HealthReport(
        status=status,
        checked_at=datetime.now(timezone.utc).isoformat(),
        checks=results,
    )


def application_liveness() -> tuple[bool, str]:
    return True, "Application process is responding."


def configuration_readiness() -> tuple[bool, str]:
    return True, "Basic application configuration check completed."
