"""Streamlit monitoring diagnostics center."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

from devops_ai.monitoring.monitoring_report import (
    build_monitoring_report,
    report_to_json,
)


def render_monitoring_center(
    diagnostics: Any | None = None,
) -> None:
    st.header("Monitoring Center")
    st.caption(
        "Validate Prometheus configuration and alert rules. "
        "No services are started or modified."
    )

    if diagnostics is None:
        st.info(
            "Connect MonitoringDiagnostics from the existing application "
            "initialization before running checks."
        )
        return

    relative_path = st.text_input(
        "Monitoring YAML file relative to project root",
        placeholder="monitoring/prometheus.yml",
    )

    if st.button("Validate monitoring configuration", type="primary"):
        if not relative_path.strip():
            st.warning("Enter an existing YAML file path.")
        else:
            result = diagnostics.inspect_config(relative_path.strip())
            report = build_monitoring_report({
                "configuration": result,
            })
            st.session_state["monitoring_center_report"] = report

    report = st.session_state.get("monitoring_center_report")
    if not isinstance(report, dict):
        return

    status = report.get("status")
    if status == "blocked":
        st.error("Monitoring configuration is blocked by findings.")
    elif status == "review_required":
        st.warning("Review the monitoring findings before relying on this setup.")
    else:
        st.success("No blocking findings were reported by the checks performed.")

    summary = report.get("summary", {})
    first, second, third = st.columns(3)
    first.metric("Files / sections checked", summary.get("sections_checked", 0))
    second.metric("Findings", summary.get("findings", 0))
    third.metric("High severity", summary.get("high_severity", 0))

    findings = report.get("findings", [])
    if findings:
        st.dataframe(findings, use_container_width=True, hide_index=True)

    st.download_button(
        "Download monitoring report",
        data=report_to_json(report),
        file_name="monitoring-readiness-report.json",
        mime="application/json",
    )

    with st.expander("Full report"):
        st.json(report)