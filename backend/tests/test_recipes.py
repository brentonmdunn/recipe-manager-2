import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_recipe(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/v1/recipes",
        json={
            "title": "Chocolate Chip Cookies",
            "description": "Classic cookies",
            "prep_time_minutes": 15,
            "cook_time_minutes": 12,
            "servings": 24,
            "ingredients": [
                {"name": "flour", "quantity": 2.25, "unit": "cups", "position": 0},
                {"name": "butter", "quantity": 1, "unit": "cup", "position": 1},
            ],
            "steps": [
                {"step_number": 1, "instruction": "Preheat oven to 375°F"},
                {"step_number": 2, "instruction": "Mix dry ingredients"},
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Chocolate Chip Cookies"
    assert data["slug"] == "chocolate-chip-cookies"
    assert len(data["ingredients"]) == 2
    assert len(data["steps"]) == 2


@pytest.mark.asyncio
async def test_list_recipes_public(client: AsyncClient, auth_headers: dict):
    await client.post(
        "/api/v1/recipes",
        json={"title": "Public Recipe", "is_public": True},
        headers=auth_headers,
    )
    await client.post(
        "/api/v1/recipes",
        json={"title": "Private Recipe", "is_public": False},
        headers=auth_headers,
    )

    response = await client.get("/api/v1/recipes")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Public Recipe"


@pytest.mark.asyncio
async def test_list_recipes_authenticated(client: AsyncClient, auth_headers: dict):
    await client.post(
        "/api/v1/recipes",
        json={"title": "Public Recipe", "is_public": True},
        headers=auth_headers,
    )
    await client.post(
        "/api/v1/recipes",
        json={"title": "Private Recipe", "is_public": False},
        headers=auth_headers,
    )

    response = await client.get("/api/v1/recipes", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_get_recipe_by_slug(client: AsyncClient, auth_headers: dict):
    await client.post(
        "/api/v1/recipes",
        json={"title": "My Great Recipe"},
        headers=auth_headers,
    )

    response = await client.get("/api/v1/recipes/my-great-recipe")
    assert response.status_code == 200
    assert response.json()["title"] == "My Great Recipe"


@pytest.mark.asyncio
async def test_update_recipe(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post(
        "/api/v1/recipes",
        json={"title": "Original Title"},
        headers=auth_headers,
    )
    recipe_id = create_resp.json()["id"]

    response = await client.put(
        f"/api/v1/recipes/{recipe_id}",
        json={"title": "Updated Title"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_update_recipe_with_ingredients_and_steps(
    client: AsyncClient, auth_headers: dict
):
    create_resp = await client.post(
        "/api/v1/recipes",
        json={"title": "Recipe With Items"},
        headers=auth_headers,
    )
    recipe_id = create_resp.json()["id"]

    response = await client.put(
        f"/api/v1/recipes/{recipe_id}",
        json={
            "title": "Recipe With Items",
            "ingredients": [
                {"name": "Flour", "quantity": 2.0, "unit": "cups"},
                {"name": "Sugar", "quantity": 1.0, "unit": "cup"},
            ],
            "steps": [
                {"step_number": 1, "instruction": "Mix dry ingredients."},
                {"step_number": 2, "instruction": "Bake at 350F."},
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert [i["name"] for i in body["ingredients"]] == ["Flour", "Sugar"]
    assert [s["instruction"] for s in body["steps"]] == [
        "Mix dry ingredients.",
        "Bake at 350F.",
    ]


@pytest.mark.asyncio
async def test_delete_recipe(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post(
        "/api/v1/recipes",
        json={"title": "To Delete"},
        headers=auth_headers,
    )
    recipe_id = create_resp.json()["id"]

    response = await client.delete(
        f"/api/v1/recipes/{recipe_id}", headers=auth_headers
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_toggle_favorite(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post(
        "/api/v1/recipes",
        json={"title": "Fav Recipe"},
        headers=auth_headers,
    )
    recipe_id = create_resp.json()["id"]
    assert create_resp.json()["is_favorite"] is False

    response = await client.patch(
        f"/api/v1/recipes/{recipe_id}/favorite", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["is_favorite"] is True


@pytest.mark.asyncio
async def test_set_rating(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post(
        "/api/v1/recipes",
        json={"title": "Rated Recipe"},
        headers=auth_headers,
    )
    recipe_id = create_resp.json()["id"]

    response = await client.patch(
        f"/api/v1/recipes/{recipe_id}/rating?rating=4", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["rating"] == 4


@pytest.mark.asyncio
async def test_create_recipe_no_auth(client: AsyncClient):
    response = await client.post(
        "/api/v1/recipes",
        json={"title": "Unauthorized"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_search_recipes(client: AsyncClient, auth_headers: dict):
    await client.post(
        "/api/v1/recipes",
        json={"title": "Chicken Tikka Masala"},
        headers=auth_headers,
    )
    await client.post(
        "/api/v1/recipes",
        json={"title": "Beef Stew"},
        headers=auth_headers,
    )

    response = await client.get(
        "/api/v1/recipes?search=chicken", headers=auth_headers
    )
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Chicken Tikka Masala"
