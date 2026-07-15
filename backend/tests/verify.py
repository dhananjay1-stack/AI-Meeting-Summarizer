"""
Automated self-verification script.

Run standalone:
    python -m backend.tests.verify

Hits all API endpoints against a running server and reports pass/fail.
"""

import asyncio
import sys
import httpx


BASE_URL = "http://127.0.0.1:8000"

PASS = "✅"
FAIL = "❌"
SKIP = "⏭️ "

results: list[tuple[str, str, str]] = []


def report(test_name: str, passed: bool, detail: str = ""):
    status = PASS if passed else FAIL
    results.append((status, test_name, detail))
    print(f"  {status} {test_name}" + (f"  ({detail})" if detail else ""))


async def run_verification():
    print("=" * 60)
    print("  AI Meeting Summarizer — Automated Verification")
    print("=" * 60)
    print()

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:

        # ── 1. Health check ──────────────────────────────────
        print("▶ Health & Docs")
        try:
            r = await client.get("/api/health")
            data = r.json()
            report("GET /api/health", r.status_code == 200 and data["status"] == "healthy",
                   f"{r.status_code} → {data.get('status')}")
        except Exception as e:
            report("GET /api/health", False, str(e))

        # ── 2. Swagger docs ──────────────────────────────────
        try:
            r = await client.get("/api/docs")
            report("GET /api/docs (Swagger)", r.status_code == 200, f"{r.status_code}")
        except Exception as e:
            report("GET /api/docs", False, str(e))

        # ── 3. OpenAPI schema ────────────────────────────────
        try:
            r = await client.get("/api/openapi.json")
            data = r.json()
            report("GET /api/openapi.json", r.status_code == 200 and "paths" in data,
                   f"{len(data.get('paths', {}))} paths")
        except Exception as e:
            report("GET /api/openapi.json", False, str(e))

        # ── 4. Register ──────────────────────────────────────
        print("\n▶ Authentication")
        import secrets
        test_email = f"verify_{secrets.token_hex(4)}@test.com"
        test_user = f"verify_{secrets.token_hex(4)}"
        test_pass = "VerifyTest1!"

        try:
            r = await client.post("/api/auth/register", json={
                "email": test_email,
                "username": test_user,
                "password": test_pass,
            })
            report("POST /api/auth/register", r.status_code == 201,
                   f"{r.status_code} → {r.json().get('username', 'error')}")
        except Exception as e:
            report("POST /api/auth/register", False, str(e))

        # ── 5. Login ─────────────────────────────────────────
        access_token = None
        try:
            r = await client.post("/api/auth/login", json={
                "email": test_email,
                "password": test_pass,
            })
            data = r.json()
            access_token = data.get("access_token")
            report("POST /api/auth/login", r.status_code == 200 and access_token is not None,
                   f"{r.status_code}")
        except Exception as e:
            report("POST /api/auth/login", False, str(e))

        if not access_token:
            print("\n⚠️  Cannot continue without auth token. Aborting.\n")
            return

        auth = {"Authorization": f"Bearer {access_token}"}

        # ── 6. Get current user ──────────────────────────────
        try:
            r = await client.get("/api/auth/me", headers=auth)
            report("GET /api/auth/me", r.status_code == 200 and r.json()["email"] == test_email,
                   f"{r.status_code}")
        except Exception as e:
            report("GET /api/auth/me", False, str(e))

        # ── 7. Settings ──────────────────────────────────────
        print("\n▶ Settings")
        try:
            r = await client.get("/api/settings/", headers=auth)
            report("GET /api/settings/", r.status_code == 200, f"{r.status_code}")
        except Exception as e:
            report("GET /api/settings/", False, str(e))

        try:
            r = await client.patch("/api/settings/", json={"theme": "dark"}, headers=auth)
            report("PATCH /api/settings/", r.status_code == 200, f"{r.status_code}")
        except Exception as e:
            report("PATCH /api/settings/", False, str(e))

        # ── 8. Meetings CRUD ─────────────────────────────────
        print("\n▶ Meetings CRUD")
        meeting_id = None
        try:
            r = await client.post("/api/meetings/", json={
                "title": "Verify Meeting",
                "description": "Automated verification test",
                "participant_count": 3,
            }, headers=auth)
            data = r.json()
            meeting_id = data.get("id")
            report("POST /api/meetings/ (create)", r.status_code == 201 and meeting_id is not None,
                   f"{r.status_code} → id={meeting_id[:8] if meeting_id else 'N/A'}...")
        except Exception as e:
            report("POST /api/meetings/", False, str(e))

        try:
            r = await client.get("/api/meetings/", headers=auth)
            data = r.json()
            report("GET /api/meetings/ (list)", r.status_code == 200 and data["total"] >= 1,
                   f"{r.status_code} → {data['total']} meetings")
        except Exception as e:
            report("GET /api/meetings/ (list)", False, str(e))

        if meeting_id:
            try:
                r = await client.get(f"/api/meetings/{meeting_id}", headers=auth)
                report("GET /api/meetings/{id} (detail)",
                       r.status_code == 200 and r.json()["meeting"]["id"] == meeting_id,
                       f"{r.status_code}")
            except Exception as e:
                report("GET /api/meetings/{id}", False, str(e))

            try:
                r = await client.patch(f"/api/meetings/{meeting_id}",
                                       json={"title": "Updated Verify Meeting"}, headers=auth)
                report("PATCH /api/meetings/{id} (update)",
                       r.status_code == 200 and r.json()["title"] == "Updated Verify Meeting",
                       f"{r.status_code}")
            except Exception as e:
                report("PATCH /api/meetings/{id}", False, str(e))

        # ── 9. Search ────────────────────────────────────────
        try:
            r = await client.get("/api/meetings/search?query=Verify", headers=auth)
            report("GET /api/meetings/search", r.status_code == 200,
                   f"{r.status_code} → {r.json()['total']} results")
        except Exception as e:
            report("GET /api/meetings/search", False, str(e))

        # ── 10. Stats ────────────────────────────────────────
        try:
            r = await client.get("/api/meetings/stats", headers=auth)
            report("GET /api/meetings/stats", r.status_code == 200,
                   f"{r.status_code} → {r.json()['total_meetings']} total")
        except Exception as e:
            report("GET /api/meetings/stats", False, str(e))

        # ── 11. Delete ───────────────────────────────────────
        if meeting_id:
            try:
                r = await client.delete(f"/api/meetings/{meeting_id}", headers=auth)
                report("DELETE /api/meetings/{id}", r.status_code == 200, f"{r.status_code}")
            except Exception as e:
                report("DELETE /api/meetings/{id}", False, str(e))

        # ── 12. Auth guard ───────────────────────────────────
        print("\n▶ Security")
        try:
            r = await client.get("/api/meetings/")
            report("Unauthenticated request blocked", r.status_code in (401, 403),
                   f"{r.status_code}")
        except Exception as e:
            report("Auth guard", False, str(e))

        try:
            r = await client.get("/api/meetings/", headers={"Authorization": "Bearer invalid"})
            report("Invalid token rejected", r.status_code in (401, 403),
                   f"{r.status_code}")
        except Exception as e:
            report("Invalid token", False, str(e))

    # ── Summary ──────────────────────────────────────────
    print("\n" + "=" * 60)
    passed = sum(1 for r in results if r[0] == PASS)
    failed = sum(1 for r in results if r[0] == FAIL)
    total = len(results)
    print(f"  Results: {passed}/{total} passed, {failed} failed")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_verification())
