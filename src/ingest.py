"""
Ingestion Module for Infrastructure RAG Assistant.

This script scans a specified directory for Terraform (.tf) files,
redacts potential secrets, splits them into chunks, generates vector
embeddings using a local HuggingFace model, and persists them into
a ChromaDB vector store.
"""

import os
import re
import sys
from typing import List

# Third-party imports
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Constants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Note: Ensure the folder name matches your filesystem (terraform-sample vs terraform_sample)
DATA_PATH = os.path.join(BASE_DIR, "data", "terraform_sample")
DB_PATH = os.path.join(BASE_DIR, "vector_db")
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def redact_secrets(text: str) -> str:
    """
    Sanitizes the text by redacting potential secrets.
    It looks for patterns like 'password = "value"' or 'secret_key = "value"'.

    Args:
        text (str): The raw Terraform code.

    Returns:
        str: The sanitized text with secrets replaced by [REDACTED].
    """
    # Regex to find assignments to variables that look like secrets
    # Captures:
    # Group 1: The variable name (e.g., password, secret_key, token)
    # Group 2: The value inside quotes
    pattern = (
        r'(?i)(\b(?:password|secret|key|token|access_key|secret_key)\b\s*=\s*)"([^"]+)"'
    )

    # Replace the value (Group 2) with [REDACTED]
    redacted_text = re.sub(pattern, r'\1"[REDACTED]"', text)
    return redacted_text


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
                    loaded_docs = loader.load()

                    # Apply Security Redaction to each document
                    for doc in loaded_docs:
                        original_content = doc.page_content
                        doc.page_content = redact_secrets(original_content)

                        # Check if modification occurred
                        if doc.page_content != original_content:
                            print(f"     🔒 Secrets redacted in {file}")

                    documents.extend(loaded_docs)
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
        Chroma.from_documents(
            documents=chunks, embedding=embeddings, persist_directory=DB_PATH
        )
        print(f"✅ Success! Embeddings saved to {DB_PATH}")

    except Exception as e:
        print(f"❌ Critical Error during embedding generation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()