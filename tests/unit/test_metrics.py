
import pytest

from src.devops_ai.observability.metrics import (
    MetricsRegistry,
    timed_operation,
)


def test_registry_records_success():
    registry = MetricsRegistry()
    result = timed_operation(
        registry, "gemini", "generate", lambda: "ok"
    )

    assert result == "ok"
    series = registry.snapshot()["series"]
    assert series[0]["requests"] == 1
    assert series[0]["errors"] == 0


def test_registry_records_failure():
    registry = MetricsRegistry()

    def fail():
        raise RuntimeError("expected")

    with pytest.raises(RuntimeError):
        timed_operation(registry, "scanner", "scan", fail)

    series = registry.snapshot()["series"]
    assert series[0]["requests"] == 1
    assert series[0]["errors"] == 1


def test_negative_duration_is_rejected():
    registry = MetricsRegistry()

    with pytest.raises(ValueError):
        registry.record_request("app", "test", -1, True)


def test_reset_clears_metrics():
    registry = MetricsRegistry()
    registry.record_request("app", "test", 0.01, True)
    registry.reset()

    assert registry.snapshot()["series"] == []
