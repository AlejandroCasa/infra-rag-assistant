"""
Unit tests for the data ingestion, security redaction, and git logic.
"""

from unittest.mock import MagicMock, patch

from src.ingest import clone_repository, redact_secrets


def test_redact_password() -> None:
    """
    Test that a standard password assignment is redacted.
    """
    raw_tf = 'password = "SuperSecretPassword123!"'
    expected = 'password = "[REDACTED]"'
    assert redact_secrets(raw_tf) == expected


def test_redact_aws_keys() -> None:
    """
    Test that AWS keys are redacted.
    """
    raw_tf = """
    provider "aws" {
      access_key = "AKIAIOSFODNN7EXAMPLE"
      secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    }
    """
    sanitized = redact_secrets(raw_tf)
    assert '"AKIAIOSFODNN7EXAMPLE"' not in sanitized
    assert 'access_key = "[REDACTED]"' in sanitized


def test_ignore_safe_values() -> None:
    """
    Test that non-secret values are NOT redacted.
    """
    raw_tf = 'bucket = "my-public-bucket"'
    assert redact_secrets(raw_tf) == raw_tf


@patch("src.ingest.Repo.clone_from")
@patch("src.ingest.shutil.rmtree")
@patch("src.ingest.os.path.exists")
def test_clone_repository_success(
    mock_exists: MagicMock, mock_rmtree: MagicMock, mock_clone: MagicMock
) -> None:
    """
    Test the clone_repository function using mocks to avoid actual network calls.
    """
    # Setup mocks
    # Case 1: Target directory does not exist, so we clone directly
    mock_exists.return_value = False

    repo_url = "[https://github.com/mock/repo.git](https://github.com/mock/repo.git)"
    target_path = "/tmp/mock_repo"

    result = clone_repository(repo_url, target_path)

    # Assertions
    assert result is True
    # Verify clone was called with correct arguments
    mock_clone.assert_called_once_with(repo_url, target_path)
    # Verify cleanup was NOT called (since path didn't exist)
    mock_rmtree.assert_not_called()


@patch("src.ingest.Repo.clone_from")
def test_clone_repository_failure(mock_clone: MagicMock) -> None:
    """
    Test that the function returns False if cloning fails.
    """
    # Setup mock to raise an exception
    mock_clone.side_effect = Exception("Git error")

    result = clone_repository("[http://bad.url](http://bad.url)", "/tmp/bad")

    assert result is False