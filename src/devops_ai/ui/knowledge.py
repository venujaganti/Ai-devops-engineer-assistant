import streamlit as st

from src.devops_ai.knowledge.rag_service import RAGService

SOURCES = {
    "AWS documentation": "https://docs.aws.amazon.com/",
    "Microsoft Azure documentation": "https://learn.microsoft.com/azure/",
    "Google Cloud documentation": "https://cloud.google.com/docs",
    "Kubernetes documentation": "https://kubernetes.io/docs/",
    "Terraform documentation": "https://developer.hashicorp.com/terraform/docs",
}


def render_knowledge_page():
    st.title("DevOps Knowledge Base")
    st.caption(
        "Index approved documentation and ask questions grounded "
        "in your local reference library."
    )

    st.warning(
        "Only index documents you are authorized to use. "
        "Do not include credentials, tokens, or private keys."
    )

    if st.button("Index / Update Documents", type="primary"):
        try:
            with st.spinner("Reading documents and generating embeddings..."):
                service = RAGService()
                result = service.index_documents()

            st.success(
                f"Indexed {result['chunks_indexed']} chunks "
                f"from {result['documents_loaded']} documents."
            )
        except Exception:
            st.error(
                "Indexing failed. Check the application configuration, "
                "document directory, and sanitized logs."
            )

    question = st.text_area(
        "Ask a question about your DevOps documentation",
        placeholder=(
            "Example: What security checks should run before "
            "a Terraform deployment?"
        ),
        max_chars=4000,
    )

    if st.button("Search and Answer"):
        if not question.strip():
            st.warning("Enter a question first.")
            return

        try:
            with st.spinner("Searching documentation and preparing an answer..."):
                result = RAGService().answer(question.strip())

            st.markdown("### Answer")
            st.markdown(result["answer"])

            st.markdown("### Retrieved sources")
            if result["sources"]:
                for source in result["sources"]:
                    st.write(
                        f"- `{source['source']}` — "
                        f"chunk {source['chunk']}, "
                        f"similarity {source['similarity']}"
                    )
            else:
                st.info("No relevant sources were found.")

        except Exception:
            st.error(
                "The knowledge query failed. Check the configuration "
                "and application logs; do not display raw exceptions."
            )

# Stable navigation API.
def render_knowledge() -> None:
    render_knowledge_page()
