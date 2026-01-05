"""
Frontend Application for Infrastructure RAG Assistant.
Architecture: Pure LCEL (LangChain Expression Language).
Zero dependency on legacy 'langchain.chains'.
"""

import os
import time
import streamlit as st
from dotenv import load_dotenv

# --- IMPORTS QUE SÍ FUNCIONAN (CORE) ---
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
# Usamos langchain_chroma (que instalamos manualmente)
from langchain_chroma import Chroma 

# --- AQUÍ ESTÁ EL TRUCO: Usamos Core, no Chains ---
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

def format_docs(docs):
    """Helper to join retrieved documents into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)

def init_rag_pipeline():
    # 1. Embeddings & DB
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    
    if not os.path.exists(DB_PATH):
        st.error(f"❌ DB not found at {DB_PATH}.")
        return None

    vector_db = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings
    )
    # Recuperador (Retriever)
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    
    # 2. LLM
    if not GOOGLE_API_KEY:
        st.error("❌ GOOGLE_API_KEY missing.")
        return None
        
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0,
    )

    # 3. Prompt
    template = """You are a Senior Cloud Architect.
    Answer the question based ONLY on the following context:
    {context}

    Question: {question}
    
    If you don't know, say "I cannot find it in the provided code".
    """
    prompt = ChatPromptTemplate.from_template(template)

    # 4. CHAIN MANUAL (Pure LCEL)
    # Esto reemplaza a 'create_retrieval_chain' y elimina la dependencia rota.
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

def main():
    st.title("🛡️ InfraOps Guardian (Pure LCEL)")
    st.caption("Running on Python 3.13 - No Legacy Chains")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if input_text := st.chat_input("Ask about your infrastructure..."):
        st.session_state.messages.append({"role": "user", "content": input_text})
        with st.chat_message("user"):
            st.markdown(input_text)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("⚡ *Processing (Core Logic)...*")
            
            try:
                chain = init_rag_pipeline()
                if chain:
                    start = time.time()
                    # Invocación directa
                    response = chain.invoke(input_text)
                    end = time.time()
                    
                    full_resp = f"{response}\n\n*(Latency: {end - start:.2f}s)*"
                    
                    placeholder.markdown(full_resp)
                    st.session_state.messages.append({"role": "assistant", "content": full_resp})
            except Exception as e:
                placeholder.error(f"Error: {e}")

if __name__ == "__main__":
    main()