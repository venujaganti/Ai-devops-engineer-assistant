import streamlit as st

from src.devops_ai.ui.theme import render_hero


PIPELINES = [
    {
        "platform": "Jenkins",
        "purpose": "Build, test, and deployment automation",
    },
    {
        "platform": "Azure Pipelines",
        "purpose": "YAML-based CI/CD and release pipelines",
    },
    {
        "platform": "Google Cloud Build",
        "purpose": "Cloud-native build and deployment workflows",
    },
    {
        "platform": "GitHub Actions",
        "purpose": "Repository automation and CI/CD",
    },
]


def render_pipelines() -> None:
    render_hero(
        "CI/CD Control Center",
        "Review pipeline platforms, deployment workflows, "
        "build status, and release diagnostics.",
        "DELIVERY ENGINEERING",
    )

    st.info(
        "Pipeline integrations are not connected in Phase 2. "
        "No real build status is being retrieved."
    )

    for pipeline in PIPELINES:
        with st.container(border=True):
            st.subheader(pipeline["platform"])
            st.write(pipeline["purpose"])
            st.caption("Status: Not connected")

    st.markdown("### Planned workflow")
    st.code(
        "Source control → Build → Test → Security scan "
        "→ Approval → Deployment → Health check",
        language="text",
    )

    st.caption(
        "Production deployments will require explicit authorization "
        "and policy checks in the execution phase."
    )