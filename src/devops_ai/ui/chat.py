import streamlit as st

from src.devops_ai.assistant.assistant_service import (
    DevOpsAssistantService,
)
from src.devops_ai.core.exceptions import DevOpsAssistantError


def render_assistant_chat():
    st.title("AI DevOps Engineer")
    st.caption(
        "Get troubleshooting guidance, pipeline recommendations, "
        "security advice and suggested commands."
    )

    st.info(
        "Commands are suggestions only. This assistant does not "
        "execute infrastructure or shell commands."
    )

    if "devops_messages" not in st.session_state:
        st.session_state.devops_messages = []

    for message in st.session_state.devops_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Describe your DevOps task or error")

    if not prompt:
        return

    st.session_state.devops_messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Reuse a cached service instance within this Streamlit session.
        if "devops_assistant_service" not in st.session_state:
            st.session_state.devops_assistant_service = (
                DevOpsAssistantService()
            )

        history = [
            {
                "role": "user" if item["role"] == "user" else "assistant",
                "content": item["content"],
            }
            for item in st.session_state.devops_messages[-12:-1]
        ]

        with st.chat_message("assistant"):
            with st.spinner("Analyzing your DevOps task..."):
                result = (
                    st.session_state.devops_assistant_service.answer(
                        prompt,
                        history=history,
                    )
                )

            st.markdown(f"**Category:** {result.category}")
            st.markdown(result.summary)

            if result.diagnosis:
                st.markdown("### Possible causes")
                for item in result.diagnosis:
                    st.markdown(f"- {item}")

            if result.recommended_steps:
                st.markdown("### Recommended steps")
                for index, item in enumerate(
                    result.recommended_steps, start=1
                ):
                    st.markdown(f"{index}. {item}")

            if result.commands:
                st.markdown("### Suggested commands")
                for item in result.commands:
                    st.markdown(
                        f"**Risk: {item.risk_level.upper()}** — "
                        f"{item.purpose}"
                    )
                    st.code(item.command, language="bash")
                    st.caption(
                        "Not executed. Review the target, permissions "
                        "and expected effects before using."
                    )

            if result.validation_steps:
                st.markdown("### Validation")
                for item in result.validation_steps:
                    st.markdown(f"- {item}")

            if result.warnings:
                st.markdown("### Warnings")
                for item in result.warnings:
                    st.warning(item)

            if result.sources:
                st.markdown("### Knowledge sources")
                for source in result.sources:
                    st.write(
                        f"- {source.get('source', 'Unknown source')} "
                        f"(chunk {source.get('chunk', '?')})"
                    )

        st.session_state.devops_messages.append(
            {"role": "assistant", "content": result.summary}
        )

        # Keep session memory bounded.
        st.session_state.devops_messages = (
            st.session_state.devops_messages[-30:]
        )

    except (DevOpsAssistantError, ValueError):
        st.error(
            "The assistant couldn't process this request. "
            "Check the configuration and try again."
        )
    except Exception:
        st.error(
            "An unexpected error occurred. Review sanitized application "
            "logs; no commands were executed."
        )

# Stable page-renderer alias used by the application navigation.
def render_chat() -> None:
    render_assistant_chat()
