from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_prometheus_config_has_app_and_health_jobs():
    config = yaml.safe_load((ROOT / "monitoring/prometheus/prometheus.yml").read_text())
    jobs = {job["job_name"]: job for job in config["scrape_configs"]}
    assert "ai-devops-assistant" in jobs
    assert "ai-devops-assistant-health" in jobs
    assert jobs["ai-devops-assistant"]["static_configs"][0]["targets"] == [
        "ai-devops-assistant:8000"
    ]


def test_alert_rules_and_grafana_provisioning_are_valid_yaml():
    files = [
        ROOT / "monitoring/prometheus/blackbox.yml",
        ROOT / "monitoring/prometheus/rules/assistant-alerts.yml",
        ROOT / "monitoring/grafana/provisioning/datasources/prometheus.yml",
        ROOT / "monitoring/grafana/provisioning/dashboards/dashboards.yml",
    ]
    for path in files:
        assert isinstance(yaml.safe_load(path.read_text()), dict), path


def test_compose_contains_app_monitoring_and_local_only_ui_ports():
    compose = yaml.safe_load((ROOT / "podman-compose.yml").read_text())
    services = compose["services"]
    assert {"ai-devops-assistant", "prometheus", "grafana", "blackbox-exporter"} <= set(services)
    assert services["prometheus"]["ports"] == ["127.0.0.1:9090:9090"]
    assert services["grafana"]["ports"] == ["127.0.0.1:3000:3000"]
    assert services["ai-devops-assistant"]["environment"]["COMMAND_EXECUTION_ENABLED"] == "false"
