"""
Pytest integration tests for Order endpoints (/api/v1/orders).
"""
import pytest

@pytest.mark.asyncio
async def test_orders_requires_auth(client):
    response = await client.get("/api/v1/orders")
    assert response.status_code == 401
