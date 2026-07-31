"""
Shared pytest fixtures.

Provides:
- async_client: HTTPX AsyncClient against the FastAPI app
- db_session: In-memory test database session (SQLite for unit tests)
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
async def async_client() -> AsyncClient:
    """HTTPX async client wired to the FastAPI test app."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client
