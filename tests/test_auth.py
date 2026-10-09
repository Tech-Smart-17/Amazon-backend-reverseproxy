"""
Pytest integration tests for Authentication endpoints (/api/v1/auth).
"""
import pytest

@pytest.mark.asyncio
async def test_register_and_login(client):
    # 1. Register User
    reg_payload = {
        "email": "testuser@amazon.com",
        "password": "Password123!",
        "full_name": "Test User",
        "phone_number": "+1234567890"
    }
    response = await client.post("/api/v1/auth/register", json=reg_payload)
    assert response.status_code == 201
    assert response.json()["success"] is True

    # 2. Login User
    login_payload = {
        "email": "testuser@amazon.com",
        "password": "Password123!"
    }
    login_resp = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
