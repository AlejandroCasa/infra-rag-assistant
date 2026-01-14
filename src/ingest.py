"""
Ingestion Module for Infrastructure RAG Assistant.

This script ingests Terraform files from either a local directory or a
remote GitHub repository. It performs the following steps:
1. Checks for a GITHUB_REPO_URL environment variable.
2. If present, clones the repository to a temporary path.
3. If not, uses the local 'data/' directory.
4. Redacts secrets (passwords/keys) from the code.
5. Generates embeddings and saves them to ChromaDB.
"""

import os
import re
import shutil
import sys
from typing import List, Optional

# Third-party imports
from git import Repo  # type: ignore
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_DATA_PATH = os.path.join(BASE_DIR, "data", "terraform_sample")
DB_PATH = os.path.join(BASE_DIR, "vector_db")
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Git Configuration
GITHUB_REPO_URL = os.getenv("GITHUB_REPO_URL")  # Example: https://github.com/hashicorp/terraform-provider-aws
CLONE_PATH = os.path.join(BASE_DIR, "data", "cloned_repo")


def redact_secrets(text: str) -> str:
    """
    Sanitizes the text by redacting potential secrets.
    It looks for patterns like 'password = "value"' or 'secret_key = "value"'.

    Args:
        text (str): The raw Terraform code.

    Returns:
        str: The sanitized text with secrets replaced by [REDACTED].
    """
    pattern = (
        r'(?i)(\b(?:password|secret|key|token|access_key|secret_key)\b\s*=\s*)"([^"]+)"'
    )
    redacted_text = re.sub(pattern, r'\1"[REDACTED]"', text)
    return redacted_text


def clone_repository(repo_url: str, target_path: str) -> bool:
    """
    Clones a GitHub repository to a local path.
    If the path exists, it cleans it up first to ensure a fresh clone.

    Args:
        repo_url (str): The URL of the git repository.
        target_path (str): The local directory to clone into.

    Returns:
        bool: True if successful, False otherwise.
    """
    print(f"🌍 Detected GITHUB_REPO_URL: {repo_url}")
    print(f"    Target Path: {target_path}")

    # Clean up existing directory if it exists
    if os.path.exists(target_path):
        print("    🗑️ Cleaning up existing clone directory...")
        # On Windows, git files can be read-only, causing permission errors with rmtree
        # We handle this by using a custom error handler or simply try/except (simplified here)
        try:
            def on_rm_error(func, path, exc_info):
                os.chmod(path, 0o777)
                func(path)
            shutil.rmtree(target_path, onerror=on_rm_error)
        except Exception as e:
            print(f"❌ Error cleaning directory: {e}")
            return False

    try:
        print("    📥 Cloning repository (this may take a while)...")
        Repo.clone_from(repo_url, target_path)
        print("    ✅ Clone successful!")
        return True
    except Exception as e:
        print(f"❌ Critical Error cloning repository: {e}")
        return False


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
        # Filter out .git directory to speed up scanning
        if ".git" in root:
            continue

        for file in files:
            if file.endswith(".tf"):
                file_path = os.path.join(root, file)
                # print(f"   - Loading: {file}") # Verbose logging reduced
                try:
                    loader = TextLoader(file_path, encoding="utf-8")
                    loaded_docs = loader.load()

                    # Apply Security Redaction to each document
                    for doc in loaded_docs:
                        original_content = doc.page_content
                        doc.page_content = redact_secrets(original_content)
                        # Add metadata about source for future use
                        doc.metadata["source"] = file_path

                    documents.extend(loaded_docs)
                except Exception as e:
                    print(f"⚠️ Warning: Could not load {file}. Error: {e}")

    return documents


def main() -> None:
    """
    Main execution flow for the ingestion process.
    """
    print("🚀 Starting Ingestion Process...")

    target_directory = LOCAL_DATA_PATH

    # 1. Determine Data Source (Git vs Local)
    if GITHUB_REPO_URL:
        if clone_repository(GITHUB_REPO_URL, CLONE_PATH):
            target_directory = CLONE_PATH
        else:
            print("❌ Failed to clone. Exiting.")
            sys.exit(1)
    else:
        print("🏠 No GITHUB_REPO_URL found. Using local sample data.")

    # 2. Load Documents
    docs = load_terraform_files(target_directory)
    if not docs:
        print("⚠️ No documents found. Exiting.")
        sys.exit(0)

    # 3. Split Documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=100, separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(docs)
    print(f"🧩 Split {len(docs)} documents into {len(chunks)} chunks.")

    # 4. Generate Embeddings & Store
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