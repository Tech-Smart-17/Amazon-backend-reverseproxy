"""
Pytest integration tests for Search endpoints (/api/v1/search).
"""
import pytest

@pytest.mark.asyncio
async def test_search_products(client):
    response = await client.get("/api/v1/search?q=laptop")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
