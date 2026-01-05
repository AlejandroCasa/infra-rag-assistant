"""
Ingestion Module for Infrastructure RAG Assistant.

This script scans a specified directory for Terraform (.tf) files,
splits them into chunks, generates vector embeddings using a local
HuggingFace model, and persists them into a ChromaDB vector store.
"""

import os
import sys
from typing import List

# Third-party imports
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Constants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "terraform-sample")
DB_PATH = os.path.join(BASE_DIR, "vector_db")
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_terraform_files(directory: str) -> List[Document]:
    """
    Recursively scans a directory and loads all .tf files.

    Args:
        directory (str): The path to the directory containing Terraform files.

    Returns:
        List[Document]: A list of LangChain Document objects containing the file content.
    """
    documents = []
    print(f"📂 Scanning directory: {directory}")

    if not os.path.exists(directory):
        print(f"❌ Error: Directory not found: {directory}")
        return []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".tf"):
                file_path = os.path.join(root, file)
                print(f"   - Loading: {file}")
                try:
                    loader = TextLoader(file_path, encoding="utf-8")
                    documents.extend(loader.load())
                except Exception as e:
                    print(f"⚠️ Warning: Could not load {file}. Error: {e}")

    return documents


def main():
    """
    Main execution flow for the ingestion process.
    """
    print("🚀 Starting Ingestion Process...")

    # 1. Load Documents
    docs = load_terraform_files(DATA_PATH)
    if not docs:
        print("⚠️ No documents found. Exiting.")
        sys.exit(0)

    # 2. Split Documents
    # We use a large chunk size because Terraform logic spans multiple lines.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=100, separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(docs)
    print(f"🧩 Split {len(docs)} documents into {len(chunks)} chunks.")

    # 3. Generate Embeddings & Store
    print(f"🧠 Generating Embeddings locally using {EMBEDDING_MODEL_NAME}...")

    try:
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

        # Create or update the vector store
        Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=DB_PATH)
        print(f"✅ Success! Embeddings saved to {DB_PATH}")

    except Exception as e:
        print(f"❌ Critical Error during embedding generation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
