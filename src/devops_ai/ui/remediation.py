
import streamlit as st

from src.devops_ai.remediation.remediation_service import RemediationService
from src.devops_ai.remediation.patch_validator import validate_proposed_patch


def render_remediation(
    findings: list[dict],
    service: RemediationService,
) -> None:
    st.header("AI Remediation Assistant")
    st.caption(
        "Gemini explains scan findings and suggests fixes. "
        "Suggestions are not applied automatically."
    )

    if not findings:
        st.info("Run a repository scan in Phase 7 before requesting remediation.")
        return

    st.write(f"Available findings: {len(findings)}")

    selected = st.multiselect(
        "Select findings to analyze",
        options=list(range(len(findings))),
        format_func=lambda index: (
            f"{findings[index].get('severity', 'info').upper()} — "
            f"{findings[index].get('rule_id', 'UNKNOWN')} — "
            f"{findings[index].get('file_path', 'unknown file')}"
        ),
        default=list(range(min(5, len(findings)))),
    )

    if not st.button("Analyze selected findings", type="primary"):
        return

    if not selected:
        st.warning("Select at least one finding.")
        return

    if len(selected) > 30:
        st.warning("Select no more than 30 findings at a time.")
        return

    selected_findings = [findings[index] for index in selected]

    try:
        with st.spinner("Analyzing findings with Gemini..."):
            report = service.analyze(selected_findings)
    except (ValueError, RuntimeError, TimeoutError) as exc:
        st.error(f"Remediation analysis failed: {exc}")
        return
    except Exception:
        # Avoid exposing raw provider errors or request contents in the UI.
        st.error(
            "An unexpected error occurred. Check sanitized application logs "
            "for details."
        )
        return

    st.subheader("Assessment")
    st.write(report.summary)

    for item in report.items:
        with st.expander(
            f"{item.severity.upper()} — {item.rule_id}: {item.title}",
            expanded=item.severity in {"critical", "high"},
        ):
            st.write(item.explanation)

            st.markdown("**Recommended steps**")
            for step in item.steps:
                st.write(f"- {step}")

            st.markdown("**How to verify**")
            st.write(item.verification)

            if item.patch:
                valid, reason = validate_proposed_patch(item.patch)
                if valid:
                    st.markdown("**Proposed patch — review only**")
                    st.code(item.patch, language="diff")
                    st.caption(
                        "This patch has not been applied or tested. "
                        "Review it in version control before use."
                    )
                else:
                    st.warning(f"Patch hidden: {reason}")

    if report.limitations:
        st.markdown("**Limitations**")
        for limitation in report.limitations:
            st.write(f"- {limitation}")
