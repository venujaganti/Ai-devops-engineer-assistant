import streamlit as st

from config.settings import get_settings
from src.devops_ai.ui.theme import render_hero


def render_settings() -> None:
    render_hero(
        "Workspace Settings",
        "Review the local configuration and future integration "
        "options for your AI DevOps assistant.",
        "CONFIGURATION",
    )

    settings = get_settings()

    st.markdown("### Application")
    st.write("Application:", settings.app_name)
    st.write("Environment:", settings.app_env)
    st.write("Logging level:", settings.log_level)

    st.markdown("### AI provider")
    st.write("Provider: Google Gemini")
    st.write(
        "API key configured:",
        "Yes" if settings.gemini_api_key else "No",
    )
    st.write(
        "Model configured:",
        "Yes" if settings.gemini_model else "No",
    )
    st.caption(
        "Model selection and API connectivity will be implemented "
        "in Phase 3. Secret values are never displayed."
    )

    st.markdown("### Command execution")
    st.write(
        "Execution enabled:",
        "Yes" if settings.command_execution_enabled else "No",
    )
    st.write(
        "Approval required:",
        "Yes" if settings.require_command_approval else "No",
    )
    st.write(
        "Maximum configured timeout:",
        f"{settings.command_timeout_seconds} seconds",
    )

    st.markdown("### Future integrations")
    st.checkbox("AWS", value=False, disabled=True)
    st.checkbox("Microsoft Azure", value=False, disabled=True)
    st.checkbox("Google Cloud", value=False, disabled=True)
    st.checkbox("Kubernetes", value=False, disabled=True)
    st.checkbox("Jenkins", value=False, disabled=True)

    st.caption(
        "These controls are informational. They do not change "
        "credentials, permissions, or execution policies."
    )