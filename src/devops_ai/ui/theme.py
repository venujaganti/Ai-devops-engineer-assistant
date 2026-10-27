import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            color-scheme: dark;
        }

        .stApp {
            background: #0b1020;
            color: #e5eaf5;
        }

        [data-testid="stSidebar"] {
            background: #101729;
            border-right: 1px solid #253047;
        }

        [data-testid="stHeader"] {
            background: rgba(11, 16, 32, 0.92);
        }

        h1, h2, h3 {
            color: #f4f7ff;
            letter-spacing: -0.035em;
        }

        p, label, li {
            color: #c4cde0;
        }

        .hero-card {
            padding: 1.6rem;
            border: 1px solid #2b3954;
            border-radius: 18px;
            background: linear-gradient(135deg, #17243c, #101729);
            margin-bottom: 1rem;
        }

        .eyebrow {
            color: #8ab4ff;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        .muted {
            color: #9ba9c3;
            font-size: 0.92rem;
        }

        .metric-card {
            padding: 1rem;
            min-height: 112px;
            border-radius: 14px;
            border: 1px solid #2b3954;
            background: #121b2d;
        }

        .metric-label {
            color: #a6b4cc;
            font-size: 0.85rem;
        }

        .metric-value {
            color: #f4f7ff;
            font-size: 1.65rem;
            font-weight: 700;
            margin-top: 0.45rem;
        }

        .status-pill {
            display: inline-block;
            border-radius: 999px;
            padding: 0.22rem 0.6rem;
            background: #1d3048;
            border: 1px solid #355173;
            color: #b8d7ff;
            font-size: 0.75rem;
        }

        div[data-testid="stChatMessage"] {
            border: 1px solid #26334b;
            border-radius: 14px;
            background: #111a2c;
            padding: 0.8rem;
        }

        div.stButton > button {
            border-radius: 10px;
            min-height: 2.6rem;
            border: 1px solid #354968;
        }

        div.stButton > button[kind="primary"] {
            background: #3867d6;
            border-color: #3867d6;
            color: white;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid #26334b;
            border-radius: 12px;
        }

        section[data-testid="stMain"] > div {
            padding-top: 1.5rem;
        }

        #MainMenu, footer {
            visibility: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(title: str, description: str, eyebrow: str) -> None:
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p class="muted">{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric(label: str, value: str, note: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="muted">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )