import streamlit as st

from src.devops_ai.integrations.cloud import CloudCLIIntegration
from src.devops_ai.integrations.kubernetes import KubernetesIntegration
from src.devops_ai.integrations.podman import PodmanIntegration
from src.devops_ai.integrations.security_scanners import (
    SecurityScannerIntegration,
)

PROVIDERS = [
    {"provider": "AWS", "cli": "aws"},
    {"provider": "Microsoft Azure", "cli": "az"},
    {"provider": "Google Cloud", "cli": "gcloud"},
]


def render_cloud_inventory():
    st.title("DevOps Integrations")
    st.caption("Check local tool availability and read-only status.")

    st.warning(
        "Checks may reveal local infrastructure metadata. "
        "Use this page only in a trusted environment."
    )

    selected = st.selectbox(
        "Integration",
        [
            "Podman",
            "Kubernetes",
            "AWS CLI",
            "Azure CLI",
            "Google Cloud CLI",
            "Trivy",
            "Gitleaks",
        ],
    )

    if st.button("Run diagnostic", type="primary"):
        with st.spinner("Checking integration..."):
            if selected == "Podman":
                result = PodmanIntegration().inspect_status()
            elif selected == "Kubernetes":
                result = KubernetesIntegration().inspect_client()
            elif selected == "AWS CLI":
                result = CloudCLIIntegration().check_cli("aws")
            elif selected == "Azure CLI":
                result = CloudCLIIntegration().check_cli("azure")
            elif selected == "Google Cloud CLI":
                result = CloudCLIIntegration().check_cli("gcp")
            elif selected in ("Trivy", "Gitleaks"):
                result = SecurityScannerIntegration().check_version(
                    selected.casefold()
                )
            else:
                st.error("Unsupported integration.")
                return

        if result.success:
            st.success(result.summary)
        else:
            st.error(result.summary)

        if result.output:
            st.code(result.output)

        for warning in result.warnings:
            st.warning(warning)