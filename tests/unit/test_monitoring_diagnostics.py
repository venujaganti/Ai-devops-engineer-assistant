from devops_ai.monitoring.monitoring_diagnostics import MonitoringDiagnostics


def test_monitoring_config_path_traversal_is_rejected(tmp_path):
    diagnostics = MonitoringDiagnostics(tmp_path)

    result = diagnostics.inspect_config("../outside.yml")

    assert result["status"] == "blocked"
    assert result["findings"][0]["code"] == "MONITORING_PATH_REJECTED"


def test_endpoint_checks_are_disabled_by_default(tmp_path):
    diagnostics = MonitoringDiagnostics(tmp_path)

    result = diagnostics.check_metrics_endpoint("http://localhost:9090/metrics")

    assert result["status"] == "disabled"


def test_unapproved_endpoint_is_rejected(tmp_path):
    diagnostics = MonitoringDiagnostics(
        tmp_path,
        allow_endpoint_checks=True,
        approved_endpoints=("http://localhost:9090/metrics",),
    )

    result = diagnostics.check_metrics_endpoint(
        "http://localhost:9090/api/v1/targets"
    )

    assert result["status"] == "blocked"


def test_remote_endpoint_is_rejected(tmp_path):
    url = "https://monitoring.example.com/metrics"
    diagnostics = MonitoringDiagnostics(
        tmp_path,
        allow_endpoint_checks=True,
        approved_endpoints=(url,),
    )

    result = diagnostics.check_metrics_endpoint(url)

    assert result["status"] == "blocked"