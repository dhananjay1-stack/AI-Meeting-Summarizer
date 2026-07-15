"""
Integration test — full end-to-end flow:
register → login → create meeting → get meeting → search → stats → delete
"""

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app


@pytest.mark.asyncio
class TestFullFlow:
    """End-to-end integration test for the complete meeting lifecycle."""

    async def test_full_user_flow(self, client: AsyncClient):
        """
        Test the complete user flow from registration to meeting deletion.
        This validates all major API endpoints work together correctly.
        """
        # ── Step 1: Register ──────────────────────────────────
        reg_res = await client.post("/api/auth/register", json={
            "email": "integration@test.com",
            "username": "integrationuser",
            "password": "IntTest123!",
        })
        assert reg_res.status_code == 201
        user = reg_res.json()
        assert user["email"] == "integration@test.com"
        assert user["username"] == "integrationuser"

        # ── Step 2: Login ─────────────────────────────────────
        login_res = await client.post("/api/auth/login", json={
            "email": "integration@test.com",
            "password": "IntTest123!",
        })
        assert login_res.status_code == 200
        tokens = login_res.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens

        access_token = tokens["access_token"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}

        # ── Step 3: Get current user ──────────────────────────
        me_res = await client.get("/api/auth/me", headers=auth_headers)
        assert me_res.status_code == 200
        assert me_res.json()["email"] == "integration@test.com"

        # ── Step 4: Get settings ──────────────────────────────
        settings_res = await client.get("/api/settings/", headers=auth_headers)
        assert settings_res.status_code == 200

        # ── Step 5: Update settings ───────────────────────────
        update_settings_res = await client.patch(
            "/api/settings/",
            json={"theme": "light", "default_ai_provider": "ollama"},
            headers=auth_headers,
        )
        assert update_settings_res.status_code == 200

        # ── Step 6: Check initial stats ───────────────────────
        stats_res = await client.get("/api/meetings/stats", headers=auth_headers)
        assert stats_res.status_code == 200
        stats = stats_res.json()
        assert stats["total_meetings"] == 0

        # ── Step 7: Create meeting ────────────────────────────
        create_res = await client.post(
            "/api/meetings/",
            json={
                "title": "Integration Test Meeting",
                "description": "Testing the full flow",
                "participant_count": 5,
            },
            headers=auth_headers,
        )
        assert create_res.status_code == 201
        meeting = create_res.json()
        meeting_id = meeting["id"]
        assert meeting["title"] == "Integration Test Meeting"
        assert meeting["status"] == "uploaded"

        # ── Step 8: Create a second meeting ───────────────────
        create_res2 = await client.post(
            "/api/meetings/",
            json={"title": "Second Meeting", "description": "Another test"},
            headers=auth_headers,
        )
        assert create_res2.status_code == 201

        # ── Step 9: List meetings ─────────────────────────────
        list_res = await client.get(
            "/api/meetings/?page=1&page_size=10",
            headers=auth_headers,
        )
        assert list_res.status_code == 200
        list_data = list_res.json()
        assert list_data["total"] == 2
        assert len(list_data["meetings"]) == 2

        # ── Step 10: Get single meeting ───────────────────────
        get_res = await client.get(
            f"/api/meetings/{meeting_id}",
            headers=auth_headers,
        )
        assert get_res.status_code == 200
        detail = get_res.json()
        assert detail["meeting"]["id"] == meeting_id
        assert detail["transcript"] is None  # Not yet processed
        assert detail["summary"] is None

        # ── Step 11: Update meeting ───────────────────────────
        update_res = await client.patch(
            f"/api/meetings/{meeting_id}",
            json={"title": "Updated Integration Meeting", "participant_count": 10},
            headers=auth_headers,
        )
        assert update_res.status_code == 200
        assert update_res.json()["title"] == "Updated Integration Meeting"

        # ── Step 12: Search meetings ──────────────────────────
        search_res = await client.get(
            "/api/meetings/search?query=Integration",
            headers=auth_headers,
        )
        assert search_res.status_code == 200
        assert search_res.json()["total"] >= 1

        # ── Step 13: Check updated stats ──────────────────────
        stats_res2 = await client.get("/api/meetings/stats", headers=auth_headers)
        assert stats_res2.status_code == 200
        assert stats_res2.json()["total_meetings"] == 2

        # ── Step 14: Delete first meeting ─────────────────────
        delete_res = await client.delete(
            f"/api/meetings/{meeting_id}",
            headers=auth_headers,
        )
        assert delete_res.status_code == 200

        # ── Step 15: Verify deletion ──────────────────────────
        get_deleted_res = await client.get(
            f"/api/meetings/{meeting_id}",
            headers=auth_headers,
        )
        assert get_deleted_res.status_code == 404

        # ── Step 16: Verify stats after deletion ──────────────
        stats_res3 = await client.get("/api/meetings/stats", headers=auth_headers)
        assert stats_res3.json()["total_meetings"] == 1

        # ── Step 17: Refresh token ────────────────────────────
        refresh_res = await client.post("/api/auth/refresh", json={
            "refresh_token": tokens["refresh_token"],
        })
        assert refresh_res.status_code == 200
        new_tokens = refresh_res.json()
        assert "access_token" in new_tokens

    async def test_unauthorized_access_blocked(self, client: AsyncClient):
        """Verify that unauthenticated requests are rejected."""
        endpoints = [
            ("GET", "/api/meetings/"),
            ("POST", "/api/meetings/"),
            ("GET", "/api/meetings/stats"),
            ("GET", "/api/settings/"),
            ("GET", "/api/auth/me"),
        ]
        for method, path in endpoints:
            if method == "GET":
                res = await client.get(path)
            else:
                res = await client.post(path, json={"title": "test"})
            assert res.status_code in (401, 403), f"{method} {path} should be protected"

    async def test_cross_user_isolation(self, client: AsyncClient):
        """Verify that users cannot access each other's meetings."""
        # Register user A
        await client.post("/api/auth/register", json={
            "email": "userA@test.com", "username": "userA", "password": "PassWord1!",
        })
        login_a = await client.post("/api/auth/login", json={
            "email": "userA@test.com", "password": "PassWord1!",
        })
        headers_a = {"Authorization": f"Bearer {login_a.json()['access_token']}"}

        # Register user B
        await client.post("/api/auth/register", json={
            "email": "userB@test.com", "username": "userB", "password": "PassWord1!",
        })
        login_b = await client.post("/api/auth/login", json={
            "email": "userB@test.com", "password": "PassWord1!",
        })
        headers_b = {"Authorization": f"Bearer {login_b.json()['access_token']}"}

        # User A creates a meeting
        create_res = await client.post(
            "/api/meetings/",
            json={"title": "A's Private Meeting"},
            headers=headers_a,
        )
        meeting_id = create_res.json()["id"]

        # User B should NOT see A's meeting
        list_b = await client.get("/api/meetings/", headers=headers_b)
        assert list_b.json()["total"] == 0

        get_b = await client.get(f"/api/meetings/{meeting_id}", headers=headers_b)
        assert get_b.status_code == 404
