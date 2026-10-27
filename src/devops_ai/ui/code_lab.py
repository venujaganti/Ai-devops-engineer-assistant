import streamlit as st

from src.devops_ai.ui.theme import render_hero


EXAMPLES = {
    "Terraform": """terraform {
  required_version = ">= 1.5.0"
}

variable "aws_region" {
  type    = string
  default = "ap-south-1"
}

provider "aws" {
  region = var.aws_region
}
""",
    "Kubernetes": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: example-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: example-app
  template:
    metadata:
      labels:
        app: example-app
    spec:
      containers:
        - name: app
          image: nginx:stable
          ports:
            - containerPort: 80
""",
    "Jenkins": """pipeline {
    agent any

    stages {
        stage('Validate') {
            steps {
                echo 'Run validation here'
            }
        }
    }
}
""",
    "Docker / Podman": """FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

USER 10001

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run",
     "streamlit_app.py",
     "--server.address=0.0.0.0"]
""",
    "Azure Pipelines": """trigger:
  - main

pool:
  vmImage: ubuntu-latest

steps:
  - script: python --version
    displayName: Check Python
""",
    "Google Cloud Build": """steps:
  - name: python:3.12-slim
    entrypoint: python
    args:
      - --version

options:
  logging: CLOUD_LOGGING_ONLY
""",
}


def render_code_lab() -> None:
    render_hero(
        "DevOps Code Lab",
        "Explore infrastructure code, container definitions, "
        "Kubernetes manifests, and CI/CD examples.",
        "CODE WORKSPACE",
    )

    technology = st.selectbox(
        "Configuration type",
        list(EXAMPLES.keys()),
    )

    code = st.text_area(
        "Configuration preview",
        value=EXAMPLES[technology],
        height=350,
        key=f"code_editor_{technology}",
    )

    st.caption(
        "Examples are editable previews, not production-ready "
        "infrastructure. Review variables, permissions, provider "
        "versions, image versions, and security requirements."
    )

    if st.button("Validate configuration"):
        st.info(
            "Automated validation will be added in Phase 5. "
            "No code was executed."
        )

    if st.button("Reset example"):
        st.session_state[f"code_editor_{technology}"] = (
            EXAMPLES[technology]
        )
        st.rerun()

    st.download_button(
        "Download configuration",
        data=code,
        file_name={
            "Terraform": "main.tf",
            "Kubernetes": "deployment.yaml",
            "Jenkins": "Jenkinsfile",
            "Docker / Podman": "Containerfile",
            "Azure Pipelines": "azure-pipelines.yml",
            "Google Cloud Build": "cloudbuild.yaml",
        }[technology],
        mime="text/plain",
    )