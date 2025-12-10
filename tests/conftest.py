import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
async def ac():
    """Асинхронный клиент для тестов """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client