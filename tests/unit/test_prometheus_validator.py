from devops_ai.monitoring.prometheus_validator import PrometheusConfigValidator


def test_valid_prometheus_configuration():
    content = """
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: prometheus
    static_configs:
      - targets:
          - localhost:9090
"""

    result = PrometheusConfigValidator().validate_text(content)

    assert result["status"] == "ready"
    assert result["findings"] == []


def test_invalid_yaml_is_blocked():
    result = PrometheusConfigValidator().validate_text(
        "scrape_configs:\n  - job_name: [unterminated"
    )

    assert result["status"] == "blocked"
    assert result["findings"][0]["code"] == "PROM_INVALID_YAML"


def test_missing_scrape_jobs_is_blocked():
    result = PrometheusConfigValidator().validate_text(
        "global:\n  scrape_interval: 15s\n"
    )

    assert result["status"] == "blocked"
    assert any(
        item["code"] == "PROM_NO_SCRAPE_JOBS"
        for item in result["findings"]
    )


def test_duplicate_job_names_are_reported():
    content = """
scrape_configs:
  - job_name: app
    static_configs:
      - targets: ["localhost:8000"]
  - job_name: app
    static_configs:
      - targets: ["localhost:9000"]
"""

    result = PrometheusConfigValidator().validate_text(content)

    assert any(
        item["code"] == "PROM_DUPLICATE_JOB_NAME"
        for item in result["findings"]
    )


def test_missing_target_is_reported():
    content = """
scrape_configs:
  - job_name: app
    static_configs:
      - targets: []
"""

    result = PrometheusConfigValidator().validate_text(content)

    assert any(
        item["code"] == "PROM_EMPTY_TARGET"
        for item in result["findings"]
    )