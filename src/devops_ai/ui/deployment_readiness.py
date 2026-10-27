"""Streamlit UI for deployment preflight checks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st

from devops_ai.deployment.readiness_report import build_readiness_report


def render_deployment_readiness(
    preflight: Any | None = None,
) -> None:
    """Render the deployment readiness dashboard."""
    st.header("Deployment Readiness")
    st.caption(
        "Static and local checks only. This page does not deploy, build, "
        "push images, or modify infrastructure."
    )

    project_root = st.text_input(
        "Existing project directory",
        value=str(Path.cwd()),
        help="Enter the path to your already-existing project directory.",
    )

    if st.button("Run preflight checks", type="primary"):
        if preflight is None:
            st.error(
                "Preflight service is not configured. Connect the existing "
                "DeploymentPreflight service in the application entry point."
            )
            return

        if not project_root.strip():
            st.warning("Enter a project directory first.")
            return

        try:
            requested_path = Path(project_root).expanduser().resolve()
            service_root = getattr(preflight, "project_root", None)

            if service_root is not None:
                configured_root = Path(service_root).resolve()
                if requested_path != configured_root:
                    st.error(
                        "The entered path does not match the configured "
                        "preflight project root."
                    )
                    return

            if not requested_path.is_dir():
                st.error("The selected path is not an existing directory.")
                return

            result = preflight.run()
            report = build_readiness_report(result)

            st.session_state["deployment_readiness_report"] = report

        except (OSError, ValueError, TypeError) as exc:
            st.error(f"Preflight could not complete: {type(exc).__name__}")

    report = st.session_state.get("deployment_readiness_report")
    if not isinstance(report, dict):
        return

    status = report.get("status", "unknown")
    if status == "blocked":
        st.error("Preflight status: BLOCKED")
    else:
        st.warning(
            "Preflight requires review. A clean static report does not "
            "guarantee deployment readiness."
        )

    summary = report.get("summary", {})
    first, second, third = st.columns(3)
    first.metric("Findings", summary.get("total_findings", 0))
    second.metric("Blocking", summary.get("blocking_findings", 0))
    third.metric("High severity", summary.get("high_findings", 0))

    findings = report.get("findings", [])
    if findings:
        st.subheader("Findings")
        st.dataframe(findings, use_container_width=True, hide_index=True)
    else:
        st.info("No findings were returned by the configured checks.")

    report_json = json.dumps(report, indent=2, ensure_ascii=False)
    st.download_button(
        "Download readiness report",
        data=report_json,
        file_name="deployment-readiness-report.json",
        mime="application/json",
    )

    with st.expander("Detailed report"):
        st.json(report)