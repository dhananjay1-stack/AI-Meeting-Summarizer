"""
Authentication tests — registration, login, token refresh, password policy.
"""

import pytest
from httpx import AsyncClient


class TestRegistration:
    """Test user registration endpoint."""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        res = await client.post("/api/auth/register", json={
            "email": "user1@example.com",
            "username": "user1",
            "password": "StrongPass1!",
        })
        assert res.status_code == 201
        data = res.json()
        assert data["email"] == "user1@example.com"
        assert data["username"] == "user1"
        assert data["role"] == "user"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient):
        await client.post("/api/auth/register", json={
            "email": "dup@example.com",
            "username": "user_a",
            "password": "StrongPass1!",
        })
        res = await client.post("/api/auth/register", json={
            "email": "dup@example.com",
            "username": "user_b",
            "password": "StrongPass1!",
        })
        assert res.status_code == 409

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        res = await client.post("/api/auth/register", json={
            "email": "weak@example.com",
            "username": "weakuser",
            "password": "short",
        })
        assert res.status_code == 422

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        res = await client.post("/api/auth/register", json={
            "email": "not-an-email",
            "username": "user2",
            "password": "StrongPass1!",
        })
        assert res.status_code == 422


class TestLogin:
    """Test login endpoint."""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient):
        await client.post("/api/auth/register", json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "StrongPass1!",
        })
        res = await client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": "StrongPass1!",
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient):
        await client.post("/api/auth/register", json={
            "email": "wrong@example.com",
            "username": "wronguser",
            "password": "StrongPass1!",
        })
        res = await client.post("/api/auth/login", json={
            "email": "wrong@example.com",
            "password": "WrongPassword1!",
        })
        assert res.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        res = await client.post("/api/auth/login", json={
            "email": "noexist@example.com",
            "password": "StrongPass1!",
        })
        assert res.status_code == 401


class TestTokenRefresh:
    """Test token refresh endpoint."""

    @pytest.mark.asyncio
    async def test_refresh_success(self, client: AsyncClient):
        await client.post("/api/auth/register", json={
            "email": "refresh@example.com",
            "username": "refreshuser",
            "password": "StrongPass1!",
        })
        login_res = await client.post("/api/auth/login", json={
            "email": "refresh@example.com",
            "password": "StrongPass1!",
        })
        refresh_token = login_res.json()["refresh_token"]

        res = await client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token,
        })
        assert res.status_code == 200
        assert "access_token" in res.json()

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, client: AsyncClient):
        res = await client.post("/api/auth/refresh", json={
            "refresh_token": "invalid.token.here",
        })
        assert res.status_code == 401


class TestGetMe:
    """Test user profile endpoint."""

    @pytest.mark.asyncio
    async def test_get_me_authenticated(self, auth_client: AsyncClient):
        res = await auth_client.get("/api/auth/me")
        assert res.status_code == 200
        assert res.json()["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_me_unauthenticated(self, client: AsyncClient):
        res = await client.get("/api/auth/me")
        assert res.status_code == 403  # No bearer token
