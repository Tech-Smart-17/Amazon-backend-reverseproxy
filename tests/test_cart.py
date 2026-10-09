"""
Pytest integration tests for Shopping Cart endpoints (/api/v1/cart).
"""
import pytest

@pytest.mark.asyncio
async def test_cart_requires_auth(client):
    response = await client.get("/api/v1/cart")
    assert response.status_code == 401
