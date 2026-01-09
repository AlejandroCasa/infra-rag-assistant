"""
Unit tests for the data ingestion and security redaction logic.
"""

from src.ingest import redact_secrets


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
    # Verify the keys are gone but the structure remains
    sanitized = redact_secrets(raw_tf)
    assert '"AKIAIOSFODNN7EXAMPLE"' not in sanitized
    assert '"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"' not in sanitized
    assert 'access_key = "[REDACTED]"' in sanitized
    assert 'secret_key = "[REDACTED]"' in sanitized


def test_ignore_safe_values() -> None:
    """
    Test that non-secret values are NOT redacted.
    """
    raw_tf = 'bucket = "my-public-bucket"'
    # Should remain unchanged
    assert redact_secrets(raw_tf) == raw_tf
