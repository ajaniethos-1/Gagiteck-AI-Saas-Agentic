"""Tests for the Gagiteck client."""

import pytest
from gagiteck import Client, GagiteckError, AuthenticationError


class TestClient:
    """Tests for the Client class."""

    def test_client_requires_api_key(self):
        """Client should require an API key."""
        with pytest.raises(AuthenticationError):
            Client(api_key=None)

    def test_client_validates_api_key_format(self):
        """Client should validate API key format."""
        with pytest.raises(AuthenticationError):
            Client(api_key="invalid_key")

    def test_client_accepts_valid_api_key(self):
        """Client should accept valid API key format."""
        client = Client(api_key="ggt_test_key_12345")
        assert client.api_key == "ggt_test_key_12345"
        client.close()

    def test_client_default_base_url(self):
        """Client should have default base URL."""
        client = Client(api_key="ggt_test_key")
        assert client.base_url == "https://api.gagiteck.com/v1"
        client.close()

    def test_client_custom_base_url(self):
        """Client should accept custom base URL."""
        client = Client(
            api_key="ggt_test_key",
            base_url="https://custom.api.com/v1",
        )
        assert client.base_url == "https://custom.api.com/v1"
        client.close()

    def test_client_context_manager(self):
        """Client should work as context manager."""
        with Client(api_key="ggt_test_key") as client:
            assert client.api_key == "ggt_test_key"

    def test_client_has_api_resources(self):
        """Client should have API resources."""
        with Client(api_key="ggt_test_key") as client:
            assert hasattr(client, "agents")
            assert hasattr(client, "workflows")
            assert hasattr(client, "executions")
