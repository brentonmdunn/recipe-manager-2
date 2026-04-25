import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={"username": "admin", "password": "testpassword123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "admin"
    assert data["is_admin"] is True


@pytest.mark.asyncio
async def test_register_twice_fails(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"username": "admin", "password": "testpassword123"},
    )
    response = await client.post(
        "/api/v1/auth/register",
        json={"username": "admin2", "password": "testpassword123"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"username": "admin", "password": "testpassword123"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "testpassword123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"username": "admin", "password": "testpassword123"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "admin"


@pytest.mark.asyncio
async def test_me_no_auth(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
