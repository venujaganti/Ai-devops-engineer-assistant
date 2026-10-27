
from src.devops_ai.observability.health import run_health_checks


def test_all_successful_checks_report_healthy():
    report = run_health_checks({
        "application": lambda: (True, "Running"),
        "configuration": lambda: (True, "Valid"),
    })

    assert report.status == "healthy"
    assert len(report.checks) == 2


def test_failed_check_reports_degraded():
    report = run_health_checks({
        "application": lambda: (True, "Running"),
        "dependency": lambda: (False, "Unavailable"),
    })

    assert report.status == "degraded"


def test_exception_does_not_leak_exception_message():
    report = run_health_checks({
        "dependency": lambda: (_ for _ in ()).throw(
            RuntimeError("password=do-not-leak")
        ),
    })

    assert report.status == "degraded"
    assert "do-not-leak" not in report.checks[0].message
