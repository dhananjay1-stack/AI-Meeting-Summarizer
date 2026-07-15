"""
Test fixtures and configuration.
"""

import os

# Set test environment BEFORE importing any app code
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-ci-12345678"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.database.session import get_db
from backend.main import app
from backend.models.base import Base


# ── Disable rate limiting in tests ───────────────────────
from backend.security.rate_limiter import limiter
limiter.enabled = False


# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Create tables before each test and drop after."""
    # Import models to register with Base
    import backend.models.user  # noqa: F401
    import backend.models.meeting  # noqa: F401
    import backend.models.audit  # noqa: F401
    import backend.models.settings  # noqa: F401

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_client(client: AsyncClient) -> AsyncClient:
    """Authenticated test client with a pre-registered user."""
    # Register
    reg_res = await client.post("/api/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPass123!",
    })
    assert reg_res.status_code == 201, f"Registration failed: {reg_res.json()}"

    # Login
    login_res = await client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass123!",
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.json()}"

    token = login_res.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client
