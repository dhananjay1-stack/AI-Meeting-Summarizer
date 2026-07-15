"""
Meeting CRUD and search tests.
"""

import pytest
from httpx import AsyncClient


class TestMeetingCRUD:
    """Test meeting create, read, update, delete."""

    @pytest.mark.asyncio
    async def test_create_meeting(self, auth_client: AsyncClient):
        res = await auth_client.post("/api/meetings/", json={
            "title": "Sprint Planning",
            "description": "Weekly sprint planning meeting",
        })
        assert res.status_code == 201
        data = res.json()
        assert data["title"] == "Sprint Planning"
        assert data["status"] == "uploaded"

    @pytest.mark.asyncio
    async def test_list_meetings(self, auth_client: AsyncClient):
        # Create 3 meetings
        for i in range(3):
            await auth_client.post("/api/meetings/", json={"title": f"Meeting {i}"})

        res = await auth_client.get("/api/meetings/")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 3
        assert len(data["meetings"]) == 3

    @pytest.mark.asyncio
    async def test_get_meeting(self, auth_client: AsyncClient):
        create_res = await auth_client.post("/api/meetings/", json={"title": "Test"})
        meeting_id = create_res.json()["id"]

        res = await auth_client.get(f"/api/meetings/{meeting_id}")
        assert res.status_code == 200
        assert res.json()["meeting"]["title"] == "Test"

    @pytest.mark.asyncio
    async def test_update_meeting(self, auth_client: AsyncClient):
        create_res = await auth_client.post("/api/meetings/", json={"title": "Old Title"})
        meeting_id = create_res.json()["id"]

        res = await auth_client.patch(f"/api/meetings/{meeting_id}", json={"title": "New Title"})
        assert res.status_code == 200
        assert res.json()["title"] == "New Title"

    @pytest.mark.asyncio
    async def test_delete_meeting(self, auth_client: AsyncClient):
        create_res = await auth_client.post("/api/meetings/", json={"title": "Delete Me"})
        meeting_id = create_res.json()["id"]

        res = await auth_client.delete(f"/api/meetings/{meeting_id}")
        assert res.status_code == 200

        get_res = await auth_client.get(f"/api/meetings/{meeting_id}")
        assert get_res.status_code == 404

    @pytest.mark.asyncio
    async def test_get_nonexistent_meeting(self, auth_client: AsyncClient):
        res = await auth_client.get("/api/meetings/nonexistent-id")
        assert res.status_code == 404


class TestMeetingSearch:
    """Test meeting search functionality."""

    @pytest.mark.asyncio
    async def test_search_by_title(self, auth_client: AsyncClient):
        await auth_client.post("/api/meetings/", json={"title": "Alpha Sprint"})
        await auth_client.post("/api/meetings/", json={"title": "Beta Review"})
        await auth_client.post("/api/meetings/", json={"title": "Alpha Retro"})

        res = await auth_client.get("/api/meetings/search", params={"query": "Alpha"})
        assert res.status_code == 200
        assert res.json()["total"] == 2


class TestMeetingStats:
    """Test meeting statistics."""

    @pytest.mark.asyncio
    async def test_get_stats(self, auth_client: AsyncClient):
        await auth_client.post("/api/meetings/", json={"title": "Meeting 1"})
        await auth_client.post("/api/meetings/", json={"title": "Meeting 2"})

        res = await auth_client.get("/api/meetings/stats")
        assert res.status_code == 200
        assert res.json()["total_meetings"] == 2
