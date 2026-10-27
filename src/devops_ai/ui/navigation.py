"""Streamlit page navigation registry."""
import streamlit as st

PAGES = {
    "Overview": "overview",
    "AI Chat": "chat",
    "Knowledge Base": "knowledge",
    "Code Lab": "code_lab",
    "Cloud Inventory": "cloud_inventory",
    "CI/CD Pipelines": "pipelines",
    "Security Center": "security",
    "Settings": "settings",
}


def render_navigation() -> str:
    return st.sidebar.radio("NAVIGATION", list(PAGES), key="navigation_page")
