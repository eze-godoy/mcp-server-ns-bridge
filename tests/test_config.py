"""Tests for configuration management."""

import os
from unittest.mock import patch

from ns_trains_mcp.config import Settings


def test_settings_from_env() -> None:
    """Test loading settings from environment variables."""
    with patch.dict(
        os.environ,
        {
            "NS_API_KEY": "test_key_123",
            "NS_API_BASE_URL": "https://test.api.ns.nl",
            "ENVIRONMENT": "development",
        },
    ):
        settings = Settings()  # type: ignore[call-arg]

        assert settings.ns_api_key == "test_key_123"
        assert settings.ns_api_base_url == "https://test.api.ns.nl"
        assert settings.environment == "development"
        assert settings.is_development is True


def test_settings_defaults() -> None:
    """Test default settings values."""
    with patch.dict(os.environ, {"NS_API_KEY": "test_key"}):
        settings = Settings()  # type: ignore[call-arg]

        assert settings.ns_api_base_url == "https://gateway.apiportal.ns.nl"
        assert settings.environment == "production"
        assert settings.is_development is False


def test_settings_is_development() -> None:
    """Test is_development property."""
    with patch.dict(os.environ, {"NS_API_KEY": "test", "ENVIRONMENT": "production"}):
        settings = Settings()  # type: ignore[call-arg]
        assert settings.is_development is False

    with patch.dict(os.environ, {"NS_API_KEY": "test", "ENVIRONMENT": "development"}):
        settings = Settings()  # type: ignore[call-arg]
        assert settings.is_development is True

    with patch.dict(os.environ, {"NS_API_KEY": "test", "ENVIRONMENT": "DEVELOPMENT"}):
        settings = Settings()  # type: ignore[call-arg]
        assert settings.is_development is True
