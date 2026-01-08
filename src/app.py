"""
Frontend Application for Infrastructure RAG Assistant.
Architecture: Pure LCEL + Mermaid.js Visualization Support.
"""

import os
import time
import re
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

# --- IMPORTS MODERNOS ---
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# --- Configuración ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "vector_db")
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

st.set_page_config(page_title="InfraOps Guardian", page_icon="🛡️", layout="wide")

# --- NUEVO: Motor de Renderizado Visual ---
def render_mermaid(code: str):
    """Renders Mermaid.js diagrams using a lightweight HTML wrapper."""
    html_code = f"""
    <script type="module">
      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
      mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});
    </script>
    <div class="mermaid">
    {code}
    </div>
    """
    # Renderizamos el HTML con un iframe de altura suficiente
    components.html(html_code, height=500, scrolling=True)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def init_rag_pipeline():
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    if not os.path.exists(DB_PATH):
        st.error(f"❌ DB not found at {DB_PATH}.")
        return None

    vector_db = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings
    )
    retriever = vector_db.as_retriever(search_kwargs={"k": 4}) # Aumentamos contexto a 4

    if not GOOGLE_API_KEY:
        st.error("❌ GOOGLE_API_KEY missing.")
        return None

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0,
    )

    # --- NUEVO: Prompt actualizado para pedir diagramas ---
    template = """You are a Senior Cloud Architect.
    Answer the question based ONLY on the following context.
    
    IMPORTANT: If the user asks for a diagram, visualization, or flow:
    1. Use Mermaid.js syntax.
    2. Wrap the code strictly in ```mermaid ... ``` blocks.
    3. Use 'graph TD' (Top-Down) or 'graph LR' (Left-Right).
    4. CRITICAL: Enclose ALL node labels in double quotes to avoid syntax errors. 
       Example: id["Node Label (with details)"] or id{{"Decision"}}
    
    Context:
    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain

def main():
    st.title("🛡️ InfraOps Guardian (Visual Edition)")
    st.caption("Now with Mermaid.js diagram support")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Si el mensaje guardado tiene mermaid, lo intentamos renderizar (simple)
            st.markdown(message["content"])

    if input_text := st.chat_input("Ask about your infrastructure..."):
        st.session_state.messages.append({"role": "user", "content": input_text})
        with st.chat_message("user"):
            st.markdown(input_text)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("⚡ *Architecting...*")
            
            try:
                chain = init_rag_pipeline()
                if chain:
                    response = chain.invoke(input_text)
                    
                    # 1. Mostrar texto normal
                    placeholder.markdown(response)
                    
                    # 2. NUEVO: Detectar si hay código Mermaid oculto
                    mermaid_blocks = re.findall(r"```mermaid\n(.*?)\n```", response, re.DOTALL)
                    
                    for block in mermaid_blocks:
                        st.caption("📊 Architecture Diagram:")
                        render_mermaid(block)

                    st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                placeholder.error(f"Error: {e}")

if __name__ == "__main__":
    main()