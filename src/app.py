"""
Frontend Application for Infrastructure RAG Assistant.
Architecture: Pure LCEL + Mermaid.js Visualization + Conversational Memory + Source Citations.
Modes: Architect (Builder) vs Auditor (SecOps).
"""

import os
import re
from operator import itemgetter
from typing import Any, Dict, List

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings

# --- Configuration ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GITHUB_REPO_URL = os.getenv("GITHUB_REPO_URL")

# Define base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "vector_db")
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Streamlit Page Config
st.set_page_config(page_title="InfraOps Guardian", page_icon="🛡️", layout="wide")


def render_mermaid(code: str) -> None:
    """
    Renders Mermaid.js diagrams using a lightweight HTML wrapper.

    Args:
        code (str): The raw Mermaid.js graph definition.
    """
    html_code = f"""
    <script type="module">
      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
      mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});
    </script>
    <div class="mermaid">
    {code}
    </div>
    """
    # Render HTML with a reasonable height
    components.html(html_code, height=500, scrolling=True)


def format_docs(docs: List[Document]) -> str:
    """
    Format retrieved documents into a single string with source attribution.
    It prepends the filename to each chunk of text so the LLM knows the origin.

    Args:
        docs (List[Document]): List of retrieved documents.

    Returns:
        str: Combined content with source metadata.
    """
    formatted_chunks = []
    for doc in docs:
        # Extract filename from path (e.g., /data/main.tf -> main.tf)
        source_path = doc.metadata.get("source", "Unknown Source")
        filename = os.path.basename(source_path)

        # Structure the context so the LLM can reference it
        chunk = f"--- SOURCE FILE: {filename} ---\n{doc.page_content}\n"
        formatted_chunks.append(chunk)

    return "\n".join(formatted_chunks)


def format_chat_history(messages: List[Dict[str, Any]]) -> List[BaseMessage]:
    """
    Converts Streamlit session state messages into LangChain message objects.
    This allows the LLM to understand the context of the conversation.

    Args:
        messages (List[Dict[str, Any]]): List of message dictionaries from st.session_state.

    Returns:
        List[BaseMessage]: List of HumanMessage and AIMessage objects.
    """
    history: List[BaseMessage] = []
    for msg in messages:
        if msg["role"] == "user":
            history.append(HumanMessage(content=str(msg["content"])))
        elif msg["role"] == "assistant":
            history.append(AIMessage(content=str(msg["content"])))
    return history


def main() -> None:
    """
    Main function to render the Streamlit application.
    """
    st.title("🛡️ InfraOps Guardian")

    # --- Sidebar Controls ---
    with st.sidebar:
        st.header("⚙️ Operation Mode")

        # 1. Security Toggle (Switch between Architect and Auditor)
        is_security_mode = st.toggle("🕵️ Security Auditor Mode", value=False)

        if is_security_mode:
            st.warning("⚠️ MODE: PARANOID. Analyzing for vulnerabilities (CIS/NIST).")
        else:
            st.info("ℹ️ MODE: ARCHITECT. Helping you build and visualize.")

        st.divider()

        # 2. Repo Info
        st.caption("📂 Data Source")
        if GITHUB_REPO_URL:
            # Show only the repo name for brevity
            repo_name = GITHUB_REPO_URL.split("/")[-1]
            st.success(f"Repo: {repo_name}")
        else:
            st.info("Local Data")

        st.caption(f"Embedding: {EMBEDDING_MODEL_NAME}")

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # Check if there is a mermaid block to render in history
            content = str(message["content"])
            if "```mermaid" in content:
                mermaid_blocks = re.findall(r"```mermaid\n(.*?)\n```", content, re.DOTALL)
                for block in mermaid_blocks:
                    render_mermaid(block)

    # Chat Input Handler
    if input_text := st.chat_input("Input command..."):
        # 1. Append user message immediately to UI
        st.session_state.messages.append({"role": "user", "content": input_text})
        with st.chat_message("user"):
            st.markdown(input_text)

        # 2. Process with Assistant
        with st.chat_message("assistant"):
            placeholder = st.empty()

            # Dynamic status message based on mode
            if is_security_mode:
                placeholder.markdown("🕵️ *Auditing Codebase...*")
            else:
                placeholder.markdown("⚡ *Architecting...*")

            try:
                # Prepare inputs: Context from DB + Conversation History
                chat_history_objects = format_chat_history(st.session_state.messages[:-1])

                # Initialize Resources
                embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

                if not os.path.exists(DB_PATH):
                    st.error("❌ Vector DB not found. Please run ingest.py first.")
                    return

                vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)

                # --- ADAPTIVE RETRIEVAL ---
                # In Security Mode, we increase 'k' (retrieval depth) to catch cross-resource issues.
                k_retrieval = 7 if is_security_mode else 5
                retriever = vector_db.as_retriever(search_kwargs={"k": k_retrieval})

                # Initialize LLM
                if not GOOGLE_API_KEY:
                    st.error("❌ GOOGLE_API_KEY missing in environment.")
                    return

                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    google_api_key=GOOGLE_API_KEY,
                    temperature=0,  # Always 0 for deterministic code analysis
                )

                # --- DYNAMIC PROMPT ENGINEERING ---
                if is_security_mode:
                    system_prompt = """You are an Elite DevSecOps Auditor (Red Team).
                    Your goal is to find security holes, misconfigurations, and compliance violations (CIS, NIST, PCI).
                    
                    TONE:
                    - Critical, direct, and "Paranoid".
                    - Do not sugarcoat. If something is insecure, state "CRITICAL RISK".
                    
                    OUTPUT FORMAT:
                    1. 🚨 **Vulnerability Analysis**: List issues found.
                    2. 🔥 **Severity**: [CRITICAL / HIGH / MEDIUM / LOW]
                    3. 🛡️ **Remediation**: Specific Terraform code fix.
                    4. 📜 **Reference**: Cite the source file AND the security standard (e.g., CIS 4.1).

                    Context:
                    {context}
                    """
                else:
                    system_prompt = """You are a Senior Cloud Architect.
                    Answer based on the following context and the conversation history.

                    RULES:
                    1. Always cite the source file name (e.g., 'According to main.tf...') when mentioning resources.
                    2. At the end of your response, list the 'Sources Used'.
                    
                    VISUALIZATION:
                    - If asked for a diagram, use Mermaid.js syntax wrapped in ```mermaid ... ```.
                    - Use 'graph TD' (Top-Down) or 'graph LR' (Left-Right).
                    - CRITICAL: Enclose node labels in double quotes. Example: id{{"Label"}}

                    Context:
                    {context}
                    """

                prompt = ChatPromptTemplate.from_messages(
                    [
                        ("system", system_prompt),
                        MessagesPlaceholder(variable_name="chat_history"),
                        ("human", "{question}"),
                    ]
                )

                # Construct LCEL Chain
                # Type annotation added for mypy strictness
                chain: Runnable = (
                    {
                        "context": itemgetter("question") | retriever | format_docs,
                        "question": itemgetter("question"),
                        "chat_history": itemgetter("chat_history"),
                    }
                    | prompt
                    | llm
                    | StrOutputParser()
                )

                # Invoke Chain
                response = chain.invoke(
                    {"question": input_text, "chat_history": chat_history_objects}
                )

                # 3. Render Response
                placeholder.markdown(response)

                # 4. Check for Mermaid diagrams in response
                mermaid_blocks = re.findall(r"```mermaid\n(.*?)\n```", response, re.DOTALL)
                for block in mermaid_blocks:
                    st.caption("📊 Architecture Diagram:")
                    render_mermaid(block)

                # 5. Save assistant response to history
                st.session_state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                placeholder.error(f"Error: {e}")


if __name__ == "__main__":
    main()
