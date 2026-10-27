"""Security tools catalogue and read-only security audit page."""

TOOLS = [
    ("Trivy", "Container, filesystem, and dependency vulnerability scanning"),
    ("SonarQube", "Static analysis and code quality checks"),
    ("Gitleaks", "Secret detection in repositories and history"),
    ("OWASP Dependency-Check", "Known vulnerable dependency detection"),
]

def render_security_hardening() -> None:
    """Render read-only security audit controls in Streamlit."""
    import json
    from pathlib import Path

    import streamlit as st

    from devops_ai.security.security_audit import SecurityAuditor

    st.subheader("Security Hardening Audit")
    st.caption(
        "Read-only heuristic checks. No shell commands, deployment, "
        "or infrastructure changes are performed."
    )

    project_path = st.text_input(
        "Approved project directory",
        value=".",
        key="security_hardening_project_path",
    )

    if not st.button(
        "Run security audit",
        key="security_hardening_run_audit",
    ):
        return

    try:
        root = Path(project_path).expanduser().resolve(strict=True)

        if not root.is_dir():
            st.error("The selected path must be a directory.")
            return

        result = SecurityAuditor(root).scan()
        report = result.to_dict()

        st.metric("Files scanned", result.scanned_files)
        st.metric("Files skipped", result.skipped_files)
        st.metric("Findings", len(result.findings))

        if result.findings:
            st.dataframe(
                [
                    finding.to_dict()
                    for finding in result.findings
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.success(
                "No findings detected by these heuristic checks. "
                "This does not prove the project is secure."
            )

        st.download_button(
            "Download security audit JSON",
            data=json.dumps(report, indent=2),
            file_name="security-audit-report.json",
            mime="application/json",
            key="security_hardening_download",
        )

    except (OSError, ValueError) as exc:
        st.error(f"Unable to run the security audit: {exc}")

# Stable navigation API.
def render_security() -> None:
    render_security_hardening()
