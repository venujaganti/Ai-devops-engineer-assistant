
from src.devops_ai.observability.diagnostic_service import DiagnosticService
from src.devops_ai.observability.metrics import MetricsRegistry


def test_diagnostic_report_has_expected_sections():
    registry = MetricsRegistry()
    registry.record_request("gemini", "generate", 0.25, True)

    report = DiagnosticService(registry).create_report()

    assert "health" in report
    assert "metrics" in report
    assert report["metrics"]["series"][0]["requests"] == 1
    assert report["security_notes"]
