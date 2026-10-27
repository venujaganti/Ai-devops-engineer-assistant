
from collections import defaultdict
from threading import Lock
from time import perf_counter


class MetricsRegistry:
    def __init__(self) -> None:
        self._lock = Lock()
        self._requests = defaultdict(int)
        self._errors = defaultdict(int)
        self._latency_seconds = defaultdict(list)

    def record_request(
        self,
        component: str,
        operation: str,
        duration_seconds: float,
        success: bool,
    ) -> None:
        if duration_seconds < 0:
            raise ValueError("duration_seconds cannot be negative")

        key = (component[:80], operation[:80])
        with self._lock:
            self._requests[key] += 1
            self._latency_seconds[key].append(duration_seconds)
            if not success:
                self._errors[key] += 1

    def snapshot(self) -> dict:
        with self._lock:
            rows = []
            for component, operation in sorted(self._requests):
                durations = list(
                    self._latency_seconds[(component, operation)]
                )
                rows.append({
                    "component": component,
                    "operation": operation,
                    "requests": self._requests[(component, operation)],
                    "errors": self._errors[(component, operation)],
                    "average_latency_ms": (
                        round(sum(durations) / len(durations) * 1000, 2)
                        if durations else 0.0
                    ),
                    "max_latency_ms": (
                        round(max(durations) * 1000, 2)
                        if durations else 0.0
                    ),
                })
            return {"series": rows}

    def reset(self) -> None:
        with self._lock:
            self._requests.clear()
            self._errors.clear()
            self._latency_seconds.clear()


def timed_operation(
    registry: MetricsRegistry,
    component: str,
    operation: str,
    callback,
):
    started = perf_counter()
    success = False
    try:
        result = callback()
        success = True
        return result
    finally:
        registry.record_request(
            component=component,
            operation=operation,
            duration_seconds=perf_counter() - started,
            success=success,
        )


metrics_registry = MetricsRegistry()
