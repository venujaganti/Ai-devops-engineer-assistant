from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_terraform_declares_network_compute_and_secure_defaults():
    main = (ROOT / "infrastructure/aws/main.tf").read_text()
    variables = (ROOT / "infrastructure/aws/variables.tf").read_text()
    assert 'resource "aws_vpc" "main"' in main
    assert 'resource "aws_internet_gateway" "main"' in main
    assert 'resource "aws_route_table" "public"' in main
    assert 'resource "aws_instance" "app"' in main
    assert 'http_tokens                 = "required"' in main
    assert 'encrypted             = true' in main
    assert 'AmazonSSMManagedInstanceCore' in main
    assert 'variable "grafana_allowed_cidr"' in variables
    assert 'variable "gemini_secret_arn"' in variables


def test_aws_bootstrap_configures_prometheus_grafana_and_disables_command_execution():
    user_data = (ROOT / "infrastructure/aws/user_data.sh.tftpl").read_text()
    assert "PROMETHEUS_METRICS_ENABLED=true" in user_data
    assert "COMMAND_EXECUTION_ENABLED=false" in user_data
    assert "docker.io/prom/prometheus:" in user_data
    assert "docker.io/grafana/grafana:" in user_data
    assert "docker.io/prom/blackbox-exporter:" in user_data
    assert "ai-devops-assistant-health" in user_data
    assert "aws secretsmanager get-secret-value" in user_data
