# AI DevOps Engineer Assistant

A Python-based AI assistant for cloud engineering, DevOps,
CI/CD, infrastructure automation, documentation search,
monitoring, and DevSecOps.

## Initial technology stack

- Python 3.11+
- Streamlit
- Google Gemini API
- Retrieval-Augmented Generation (RAG)
- Podman
- pytest and Ruff

## Planned integrations

AWS, Microsoft Azure, Google Cloud, Docker, Podman,
Kubernetes, Jenkins, Azure Pipelines, Google Cloud Build,
Terraform, Prometheus, Grafana, Trivy, SonarQube,
Gitleaks, and OWASP Dependency-Check.

The current implementation provides local tool-availability diagnostics and policy scaffolding. Provider-specific API operations require separate credentials and configuration.

## Prerequisites

- Python 3.11 or newer
- pip
- Git
- Podman (for the later containerization phase)

A Gemini API key is required only for Gemini-powered chat and embedding requests. Configuration checks and offline tests do not require it.

## Local setup

Create and activate a Python virtual environment using
the instructions for your operating system.

Install the project in editable mode and install dependencies:

    python -m pip install -e .
    python -m pip install -r requirements.txt

Validate configuration:

    python scripts/validate_config.py

Run tests:

    python -m pytest -q

Start the application:

    python -m streamlit run streamlit_app.py

## Configuration

Copy the documented settings from .env.example into a
local .env file and update values as needed.

Never commit .env, real API keys, cloud credentials,
private keys, or generated sensitive data.

Gemini-powered chat and knowledge retrieval require a valid `GEMINI_API_KEY`. Without a key, configuration checks and non-AI features can still be used.

## Security principles

- Default to read-only infrastructure access.
- Require explicit approval for execution.
- Use isolated workers for commands.
- Apply command allowlists, timeouts, and resource limits.
- Never execute model-generated commands directly.
- Keep secrets out of logs and source control.

## Development status

The repository contains UI pages, Gemini integration, documentation retrieval, read-only tool diagnostics, security checks, and execution-policy scaffolding. Cloud and CI/CD integrations report local tool availability unless credentials and provider-specific connectivity are explicitly configured.

## Podman

Create a local `.env` file from `.env.example`, then build and start the container with `podman-compose up --build` (or the equivalent `podman compose` command supported by your installation). The UI listens on port `8501`. Keep `COMMAND_EXECUTION_ENABLED=false` unless a separately reviewed, sandboxed execution backend has been configured.

## Cost

The project is designed for local development and
minimum-cost operation. External API usage and hosted
services may have separate limits or charges.
## Tests and CI/CD

The GitHub Actions workflows validate Python syntax, configuration and documentation, run offline unit/integration tests with coverage, lint with Ruff, validate Terraform formatting/configuration, build and smoke-test the Podman image, scan the image/configuration with Trivy, run Bandit and dependency auditing, and scan repository history for secrets. Gemini live tests are intentionally opt-in and are not required for pull requests.

Run the local checks from the repository root:

```bash
python -m pip install -e .
python -m pip install -r requirements.txt
python scripts/validate_config.py
python scripts/validate_docs.py
python -m ruff check .
python -m pytest tests/unit tests/integration -m "not live" -q
```

The CI container smoke test requires Linux with Podman and network access to pull base images. The application container uses `requirements-runtime.txt` so test/lint/security tooling is not installed in the production image.

## Podman deployment

Create `.env` from `.env.example`, then set a unique `GRAFANA_ADMIN_PASSWORD` (at least 16 characters). Start the application and observability stack:

```bash
podman compose -f podman-compose.yml up --build -d
# If your Podman installation uses the standalone plugin:
podman-compose -f podman-compose.yml up --build -d
```

- App: `http://localhost:8501`
- Prometheus: `http://localhost:9090` (bound to loopback only)
- Grafana: `http://localhost:3000` (bound to loopback only; sign in with the configured Grafana admin credentials)

Prometheus scrapes the application's `/metrics` endpoint on the internal container network and uses Blackbox Exporter to check Streamlit's `/_stcore/health` endpoint. Grafana provisions Prometheus as its data source and loads the `AI DevOps Assistant Overview` dashboard. Alert rules are stored in `monitoring/prometheus/rules/assistant-alerts.yml`. The application metrics endpoint is enabled only when `PROMETHEUS_METRICS_ENABLED=true`.

Check services and logs:

```bash
podman compose -f podman-compose.yml ps
podman compose -f podman-compose.yml logs --tail=100 ai-devops-assistant prometheus grafana
```

Do not expose Prometheus/Grafana directly to the public internet. The default compose port bindings use `127.0.0.1`; use a secure tunnel or a reverse proxy with authentication if remote access is needed. For production, replace pinned demonstration image versions with versions approved by your organization and regularly rebuild to receive security fixes.

## AWS Terraform deployment

`infrastructure/aws` provisions a dedicated VPC, public subnet, internet gateway, route table, security group, encrypted gp3 root disk, EC2 instance, least-privilege Systems Manager instance role, and Podman-hosted application, Prometheus, and Grafana. IMDSv2 is required. SSH and Grafana ingress are closed by default; use Systems Manager Session Manager. The Streamlit port 8501 is internet reachable by default, so put it behind an authenticated HTTPS load balancer and tighten the security group before production use.

Prerequisites:

1. AWS CLI credentials with permission to provision the Terraform resources, plus Terraform 1.6 or newer.
2. Publish the image with `.github/workflows/publish-container.yml`. The EC2 instance pulls from GHCR without registry credentials, so the GHCR package must be public for this starter deployment. If your organization requires a private image, switch to ECR or configure a dedicated pull-secret mechanism before deployment.
3. Create a remote Terraform state S3 bucket with encryption and public access blocked, and a DynamoDB table for state locking. The workflow expects repository/environment variables `AWS_REGION`, `TF_STATE_BUCKET`, and `TF_STATE_LOCK_TABLE`.
4. Configure GitHub OIDC trust for a deployment role and set `AWS_DEPLOY_ROLE_ARN` plus `GRAFANA_ADMIN_PASSWORD` as GitHub environment secrets. Restrict the role trust to this repository and the intended GitHub environment. Configure required reviewers on the `production` GitHub environment. For Gemini-powered features, create an AWS Secrets Manager secret whose `SecretString` is the Gemini API key and set its ARN in the `GEMINI_SECRET_ARN` GitHub environment variable. The EC2 role receives `secretsmanager:GetSecretValue` only for that ARN. Without the optional secret, the app deploys without Gemini-powered requests.
5. Manually run the **Deploy AWS infrastructure** workflow and select the target environment. Configure `grafana_allowed_cidr` only with a trusted admin IP/CIDR if direct access is truly required; otherwise leave it empty.

For local Terraform use, copy `infrastructure/aws/terraform.tfvars.example` to `terraform.tfvars`, replace the example image and password, and initialize with your own backend configuration. Never commit `terraform.tfvars` or real credentials. Terraform state and EC2 user data contain the Grafana bootstrap password; the Gemini API key is fetched from Secrets Manager at boot when configured. This starter implementation is for learning/dev use, and production deployments should retrieve the Grafana password from AWS Secrets Manager or Parameter Store as well, rather than embedding it in Terraform user data.

The AWS deployment is a single EC2 instance intended as a demonstrator, not a highly available production architecture. Review cost, network exposure, backup, patching, TLS, scaling, and disaster-recovery requirements before using it for production workloads.
