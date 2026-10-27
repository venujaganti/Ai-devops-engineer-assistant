"""Streamlit interface for the end-to-end DevOps workflow."""

from __future__ import annotations

import json
from typing import Any

import streamlit as st


WORKFLOW_OPTIONS = {
    "Ask the AI assistant": "assistant",
    "Scan the repository": "repository_scan",
    "Check deployment readiness": "deployment_preflight",
    "Validate monitoring configuration": "monitoring_validation",
}


def render_workflow_center(workflow: Any | None = None) -> None:
    st.header("DevOps Workflow Center")
    st.caption(
        "Run approved diagnostic workflows and review their results. "
        "No deployment or infrastructure-changing action is available here."
    )

    if workflow is None:
        st.info("Connect DevOpsWorkflow in the existing application initialization.")
        return

    label = st.selectbox(
        "Select a workflow",
        options=list(WORKFLOW_OPTIONS),
    )
    question = st.text_area(
        "Question or task details",
        max_chars=10_000,
        placeholder="Example: How can I investigate a failing container?",
    )

    include_remediation = st.checkbox(
        "Generate remediation suggestions after repository scanning",
        value=False,
    )
    include_preflight = st.checkbox(
        "Include deployment preflight after repository scanning",
        value=False,
    )
    monitoring_path = st.text_input(
        "Monitoring YAML path (only for monitoring validation)",
        placeholder="monitoring/prometheus.yml",
    )

    if st.button("Run selected workflow", type="primary"):
        task = WORKFLOW_OPTIONS[label]

        if task == "assistant" and not question.strip():
            st.warning("Enter a question for the assistant.")
            return

        if task == "monitoring_validation" and not monitoring_path.strip():
            st.warning("Enter the relative path to an existing monitoring YAML file.")
            return

        try:
            result = workflow.run(
                task,
                question=question,
                run_remediation=(
                    include_remediation and task == "repository_scan"
                ),
                run_deployment_preflight=(
                    include_preflight and task == "repository_scan"
                ),
                monitoring_config_path=(
                    monitoring_path.strip()
                    if task == "monitoring_validation"
                    else None
                ),
            )
            st.session_state["devops_workflow_result"] = result.to_dict()
        except Exception as exc:
            st.error(f"Workflow could not complete: {type(exc).__name__}")

    data = st.session_state.get("devops_workflow_result")
    if not isinstance(data, dict):
        return

    status = data.get("status", "unknown")
    if status == "success":
        st.success(data.get("summary", "Workflow completed."))
    elif status in {"blocked", "failed"}:
        st.error(data.get("summary", "Workflow did not complete successfully."))
    else:
        st.warning(data.get("summary", "Workflow completed with warnings."))

    for step in data.get("steps", []):
        with st.expander(
            f"{step.get('name', 'Step')} — {step.get('status', 'unknown')}",
            expanded=True,
        ):
            st.write(step.get("summary", "No summary available."))
            if step.get("details"):
                st.json(step["details"])

    st.download_button(
        "Download workflow report",
        data=json.dumps(data, indent=2, ensure_ascii=False),
        file_name="devops-workflow-report.json",
        mime="application/json",
    )

    with st.expander("Workflow limitations"):
        for limitation in data.get("limitations", []):
            st.write(f"- {limitation}")