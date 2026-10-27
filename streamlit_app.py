"""Streamlit entry point for the AI DevOps Engineer Assistant."""
import streamlit as st

from src.devops_ai.ui import chat, cloud_inventory, code_lab, knowledge, navigation, pipelines, security, settings_page, theme

st.set_page_config(page_title="AI DevOps Engineer Assistant", page_icon="🛠️", layout="wide")

theme.apply_theme()
st.sidebar.title("AI DevOps Engineer")
st.sidebar.caption("ENGINEERING WORKSPACE")
page_label = st.sidebar.radio("NAVIGATION", list(navigation.PAGES), key="navigation_page")
page = navigation.PAGES[page_label]

if page == "overview":
    st.title("AI DevOps Engineer Assistant")
    st.caption("A safety-first workspace for cloud, CI/CD, infrastructure, and DevSecOps tasks.")
    left, middle, right = st.columns(3)
    left.metric("Command execution", "Disabled")
    middle.metric("AI provider", "Gemini")
    right.metric("Mode", "Local-first")
    st.info("Commands are suggestions only. Review any command before running it; destructive execution is not enabled by default.")
    st.markdown("### Workspaces")
    st.markdown("Use the sidebar to open AI Chat, Knowledge Base, Code Lab, Cloud Inventory, CI/CD Pipelines, Security Center, or Settings.")
elif page == "chat":
    chat.render_chat()
elif page == "knowledge":
    knowledge.render_knowledge()
elif page == "code_lab":
    code_lab.render_code_lab()
elif page == "cloud_inventory":
    cloud_inventory.render_cloud_inventory()
elif page == "pipelines":
    pipelines.render_pipelines()
elif page == "security":
    security.render_security()
elif page == "settings":
    settings_page.render_settings()
