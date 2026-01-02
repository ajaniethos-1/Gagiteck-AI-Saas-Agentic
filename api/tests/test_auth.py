"""Tests for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestAuthEndpoints:
    """Tests for authentication endpoints."""

    def test_signup_success(self):
        """POST /v1/auth/signup should create a new user."""
        response = client.post(
            "/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "testpassword123",
                "name": "Test User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"
        assert "id" in data
        assert "password" not in data

    def test_signup_duplicate_email(self):
        """POST /v1/auth/signup with duplicate email should fail."""
        # First signup
        client.post(
            "/v1/auth/signup",
            json={
                "email": "duplicate@example.com",
                "password": "testpassword123",
                "name": "Test User",
            },
        )
        # Second signup with same email
        response = client.post(
            "/v1/auth/signup",
            json={
                "email": "duplicate@example.com",
                "password": "testpassword456",
                "name": "Another User",
            },
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_signup_invalid_email(self):
        """POST /v1/auth/signup with invalid email should fail."""
        response = client.post(
            "/v1/auth/signup",
            json={
                "email": "invalid-email",
                "password": "testpassword123",
                "name": "Test User",
            },
        )
        assert response.status_code == 422

    def test_signup_short_password(self):
        """POST /v1/auth/signup with short password should fail."""
        response = client.post(
            "/v1/auth/signup",
            json={
                "email": "shortpass@example.com",
                "password": "short",
                "name": "Test User",
            },
        )
        assert response.status_code == 422

    def test_login_success(self):
        """POST /v1/auth/login should return JWT token."""
        # Create user first
        client.post(
            "/v1/auth/signup",
            json={
                "email": "login@example.com",
                "password": "testpassword123",
                "name": "Login User",
            },
        )
        # Login
        response = client.post(
            "/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "testpassword123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    def test_login_wrong_password(self):
        """POST /v1/auth/login with wrong password should fail."""
        # Create user first
        client.post(
            "/v1/auth/signup",
            json={
                "email": "wrongpass@example.com",
                "password": "testpassword123",
                "name": "Wrong Pass User",
            },
        )
        # Login with wrong password
        response = client.post(
            "/v1/auth/login",
            json={
                "email": "wrongpass@example.com",
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self):
        """POST /v1/auth/login for non-existent user should fail."""
        response = client.post(
            "/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "testpassword123",
            },
        )
        assert response.status_code == 401

    def test_get_me_authenticated(self):
        """GET /v1/auth/me should return current user."""
        # Create and login user
        client.post(
            "/v1/auth/signup",
            json={
                "email": "me@example.com",
                "password": "testpassword123",
                "name": "Me User",
            },
        )
        login_response = client.post(
            "/v1/auth/login",
            json={
                "email": "me@example.com",
                "password": "testpassword123",
            },
        )
        token = login_response.json()["access_token"]

        # Get current user
        response = client.get(
            "/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "me@example.com"
        assert data["name"] == "Me User"

    def test_get_me_unauthenticated(self):
        """GET /v1/auth/me without token should fail."""
        response = client.get("/v1/auth/me")
        assert response.status_code == 403

    def test_create_api_key(self):
        """POST /v1/auth/api-keys should create an API key."""
        # Create and login user
        client.post(
            "/v1/auth/signup",
            json={
                "email": "apikey@example.com",
                "password": "testpassword123",
                "name": "API Key User",
            },
        )
        login_response = client.post(
            "/v1/auth/login",
            json={
                "email": "apikey@example.com",
                "password": "testpassword123",
            },
        )
        token = login_response.json()["access_token"]

        # Create API key
        response = client.post(
            "/v1/auth/api-keys",
            json={"name": "Test API Key"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test API Key"
        assert data["key"].startswith("ggt_")
        assert "id" in data
