
import streamlit as st

from src.devops_ai.observability.diagnostic_service import DiagnosticService


def render_monitoring(service: DiagnosticService) -> None:
    st.header("Application Monitoring")
    st.caption(
        "Local process health, in-memory operation metrics, and sanitized status."
    )

    if st.button("Refresh diagnostics"):
        report = service.create_report()
        st.session_state["observability_report"] = report

    report = st.session_state.get("observability_report")
    if report is None:
        report = service.create_report()
        st.session_state["observability_report"] = report

    health = report["health"]
    if health["status"] == "healthy":
        st.success("Application health: healthy")
    else:
        st.warning("Application health: degraded")

    st.caption(f"Checked at: {health['checked_at']}")

    st.subheader("Health checks")
    st.dataframe(health["checks"], use_container_width=True)

    st.subheader("Operation metrics")
    series = report["metrics"]["series"]

    if series:
        st.dataframe(series, use_container_width=True)

        total_requests = sum(item["requests"] for item in series)
        total_errors = sum(item["errors"] for item in series)
        col1, col2 = st.columns(2)
        col1.metric("Recorded operations", total_requests)
        col2.metric("Recorded errors", total_errors)
    else:
        st.info(
            "No operations have been recorded yet. "
            "Instrument the relevant services to populate these metrics."
        )

    with st.expander("Monitoring limitations"):
        for note in report["security_notes"]:
            st.write(f"- {note}")
