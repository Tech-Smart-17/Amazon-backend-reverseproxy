"""
Pytest integration tests for Product catalog endpoints (/api/v1/products).
"""
import pytest

@pytest.mark.asyncio
async def test_list_products_empty(client):
    response = await client.get("/api/v1/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
