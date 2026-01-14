"""
Unit tests for the core application logic and environment configuration.
"""

import os
import re
import textwrap
from typing import Dict, List

import pytest
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage

from src.app import format_chat_history, format_docs

# Load env vars for the test session
load_dotenv()

# Define the expected path for the vector database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "vector_db")


def test_environment_variables() -> None:
    """
    Test that critical environment variables are set.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    assert api_key is not None, "GOOGLE_API_KEY should be set in the .env file"


def test_mermaid_regex_detection() -> None:
    """
    Test the logic used to detect Mermaid.js blocks in the LLM response.
    """
    mock_response = textwrap.dedent(
        """
    Here is the architecture diagram:
    ```mermaid
    graph TD
    A[Client] --> B[Load Balancer]
    ```
    Hope this helps!
    """
    )

    mermaid_blocks = re.findall(r"```mermaid\n(.*?)\n```", mock_response, re.DOTALL)

    assert len(mermaid_blocks) == 1, "Should detect exactly one mermaid block"
    assert "graph TD" in mermaid_blocks[0], "The block content should be extracted correctly"
    assert "```" not in mermaid_blocks[0], "Captured content should not contain backticks"


def test_format_docs_with_citations() -> None:
    """
    Test that the document formatter correctly prepends source metadata.
    """
    # Create mock documents with metadata
    docs = [
        Document(page_content="resource A", metadata={"source": "/tmp/main.tf"}),
        Document(page_content="resource B", metadata={"source": "/tmp/variables.tf"}),
    ]

    formatted_output = format_docs(docs)

    # Assertions
    assert "--- SOURCE FILE: main.tf ---" in formatted_output
    assert "--- SOURCE FILE: variables.tf ---" in formatted_output
    assert "resource A" in formatted_output


def test_format_chat_history() -> None:
    """
    Test the conversion from Streamlit session state to LangChain messages.
    """
    # Mock Streamlit session state structure
    streamlit_history: List[Dict[str, str]] = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"},
    ]

    langchain_history = format_chat_history(streamlit_history)

    # Assertions
    assert len(langchain_history) == 2
    assert isinstance(langchain_history[0], HumanMessage)
    assert langchain_history[0].content == "Hello"
    assert isinstance(langchain_history[1], AIMessage)
    assert langchain_history[1].content == "Hi there"

@pytest.mark.skipif(
    os.getenv("CI") is not None,
    reason="Skipping DB existence check in CI environment (no ingestion run)",
)
def test_vector_db_existence() -> None:
    """
    Test that the Vector DB directory exists (implies ingestion ran).
    """
    assert os.path.exists(DB_PATH), f"Vector DB should exist at {DB_PATH}. Did you run ingest.py?"
