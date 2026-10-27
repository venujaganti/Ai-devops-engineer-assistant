# Changelog

## Unreleased

- Added a dependency-free Prometheus metrics endpoint for the assistant's operation registry.
- Added Podman Compose services for Prometheus, Blackbox Exporter, and Grafana, including provisioning, a dashboard, and alert rules.
- Added an AWS Terraform starter deployment with VPC/networking, EC2, encrypted storage, an SSM instance profile, optional least-privilege Secrets Manager access for Gemini, and Podman-hosted app/monitoring services.
- Expanded GitHub Actions with Terraform validation, container build/health smoke tests, image/config scans, dependency audit, GHCR publishing, and an OIDC-based manual AWS deployment workflow.
- Split runtime container dependencies from development/test tools and added regression tests for observability configuration.
- Retained command execution as disabled by default and bound local Prometheus/Grafana UI ports to loopback.
