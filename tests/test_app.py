"""
Unit tests for the core application logic and environment configuration.
"""

import os
import re
import textwrap

import pytest
from dotenv import load_dotenv

# Load env vars for the test session
load_dotenv()

# Define the expected path for the vector database
# We use abspath to ensure it works regardless of where pytest is invoked
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "vector_db")


def test_environment_variables() -> None:
    """
    Test that critical environment variables are set.
    """
    # We check if GOOGLE_API_KEY is present in the environment
    api_key = os.getenv("GOOGLE_API_KEY")
    assert api_key is not None, "GOOGLE_API_KEY should be set in the .env file"


def test_mermaid_regex_detection() -> None:
    """
    Test the logic used to detect Mermaid.js blocks in the LLM response.
    """
    # We use textwrap.dedent to remove the indentation of the Python code
    # so the string looks exactly like a raw LLM response (left-aligned).
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

    # Regex pattern to find mermaid blocks (Same as in app.py)
    mermaid_blocks = re.findall(r"```mermaid\n(.*?)\n```", mock_response, re.DOTALL)

    # Assertions
    assert len(mermaid_blocks) == 1, "Should detect exactly one mermaid block"
    assert "graph TD" in mermaid_blocks[0], "The block content should be extracted correctly"
    # Verify we didn't capture the backticks
    assert "```" not in mermaid_blocks[0], "Captured content should not contain backticks"


def test_vector_db_existence() -> None:
    """
    Test that the Vector DB directory exists (implies ingestion ran).
    """
    # Check if the folder exists
    assert os.path.exists(DB_PATH), f"Vector DB should exist at {DB_PATH}. Did you run ingest.py?"
