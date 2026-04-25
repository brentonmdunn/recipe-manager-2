import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_share_link(client: AsyncClient, auth_headers: dict):
    recipe_resp = await client.post(
        "/api/v1/recipes",
        json={"title": "Shareable Recipe"},
        headers=auth_headers,
    )
    recipe_id = recipe_resp.json()["id"]

    response = await client.post(
        "/api/v1/share",
        json={"recipe_id": recipe_id},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["recipe_id"] == recipe_id
    assert "token" in data


@pytest.mark.asyncio
async def test_create_share_link_no_auth(client: AsyncClient, auth_headers: dict):
    recipe_resp = await client.post(
        "/api/v1/recipes",
        json={"title": "Shareable Recipe"},
        headers=auth_headers,
    )
    recipe_id = recipe_resp.json()["id"]

    response = await client.post(
        "/api/v1/share",
        json={"recipe_id": recipe_id},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_share_links(client: AsyncClient, auth_headers: dict):
    recipe_resp = await client.post(
        "/api/v1/recipes",
        json={"title": "Shareable Recipe"},
        headers=auth_headers,
    )
    recipe_id = recipe_resp.json()["id"]

    await client.post(
        "/api/v1/share",
        json={"recipe_id": recipe_id},
        headers=auth_headers,
    )
    await client.post(
        "/api/v1/share",
        json={"recipe_id": recipe_id},
        headers=auth_headers,
    )

    response = await client.get(
        f"/api/v1/share/{recipe_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_get_shared_recipe_by_token(client: AsyncClient, auth_headers: dict):
    recipe_resp = await client.post(
        "/api/v1/recipes",
        json={"title": "Shareable Recipe", "is_public": False},
        headers=auth_headers,
    )
    recipe_id = recipe_resp.json()["id"]

    share_resp = await client.post(
        "/api/v1/share",
        json={"recipe_id": recipe_id},
        headers=auth_headers,
    )
    token = share_resp.json()["token"]

    response = await client.get(f"/api/v1/share/token/{token}")
    assert response.status_code == 200
    assert response.json()["title"] == "Shareable Recipe"


@pytest.mark.asyncio
async def test_get_shared_recipe_invalid_token(client: AsyncClient):
    response = await client.get("/api/v1/share/token/nonexistent-token")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_share_link(client: AsyncClient, auth_headers: dict):
    recipe_resp = await client.post(
        "/api/v1/recipes",
        json={"title": "Shareable Recipe"},
        headers=auth_headers,
    )
    recipe_id = recipe_resp.json()["id"]

    share_resp = await client.post(
        "/api/v1/share",
        json={"recipe_id": recipe_id},
        headers=auth_headers,
    )
    share_link_id = share_resp.json()["id"]
    token = share_resp.json()["token"]

    response = await client.delete(
        f"/api/v1/share/{share_link_id}",
        headers=auth_headers,
    )
    assert response.status_code == 204

    response = await client.get(f"/api/v1/share/token/{token}")
    assert response.status_code == 404
