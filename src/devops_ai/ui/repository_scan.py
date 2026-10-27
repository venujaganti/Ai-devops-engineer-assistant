
from pathlib import Path

import streamlit as st

from src.devops_ai.integrations.repository_scanner import RepositoryScanner
from src.devops_ai.integrations.report_writer import build_report, report_to_json


def render_repository_scan() -> None:
    st.header("Repository Configuration Scan")
    st.caption(
        "Read-only static checks for DevOps configuration files. "
        "This page does not deploy, apply Terraform, or execute project scripts."
    )

    root_text = st.text_input(
        "Local repository path",
        value=".",
        help="Enter the path to the repository you want to inspect.",
    )

    if not st.button("Scan repository", type="primary"):
        return

    try:
        root = Path(root_text).expanduser()
        if not root.exists() or not root.is_dir():
            st.error("Enter an existing local directory.")
            return

        scanner = RepositoryScanner(root)
        with st.spinner("Scanning supported configuration files..."):
            result = scanner.scan()
            report = build_report(result)
            report_json = report_to_json(report)

    except (OSError, ValueError, TypeError) as exc:
        st.error(f"Scan could not be completed: {exc}")
        return

    st.success(f"Scanned {report['scanned_file_count']} file(s).")
    st.subheader("Finding summary")

    columns = st.columns(5)
    for column, severity in zip(
        columns, ["critical", "high", "medium", "low", "info"]
    ):
        column.metric(severity.title(), report["summary"][severity])

    if report["findings"]:
        st.dataframe(
            [
                {
                    "Severity": item["severity"].upper(),
                    "Rule": item["rule_id"],
                    "File": item["file_path"],
                    "Line": item["line"],
                    "Finding": item["message"],
                    "Recommendation": item["recommendation"],
                }
                for item in report["findings"]
            ],
            use_container_width=True,
        )
    else:
        st.info("No findings were reported by the enabled static checks.")

    with st.expander("Scanned files"):
        st.write(report["scanned_files"])

    with st.expander("Skipped files"):
        st.write(report["skipped_files"])

    with st.expander("Scope and limitations"):
        for limitation in report["limitations"]:
            st.write(f"- {limitation}")

    st.download_button(
        "Download JSON report",
        data=report_json,
        file_name="devops-repository-scan.json",
        mime="application/json",
    )
