from fastapi import APIRouter, Query, UploadFile

from app.dependencies import (
    CurrentUser,
    ImageServiceDep,
    OptionalUser,
    RecipeServiceDep,
    ScraperServiceDep,
    SessionDep,
)
from app.schemas.recipe import (
    ImageResponse,
    PaginatedResponse,
    RecipeCreate,
    RecipeImportRequest,
    RecipeResponse,
    RecipeUpdate,
)

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.get("", response_model=PaginatedResponse)
async def list_recipes(
    recipe_service: RecipeServiceDep,
    user: OptionalUser,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str | None = None,
    tag_ids: list[str] | None = Query(None),
    category_id: str | None = None,
    is_favorite: bool | None = None,
    min_rating: int | None = Query(None, ge=1, le=5),
    max_cook_time: int | None = Query(None, ge=0),
    sort_by: str = Query(
        "created_at",
        pattern="^(title|created_at|rating|cook_time_minutes)$",
    ),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
) -> PaginatedResponse:
    return await recipe_service.list_recipes(
        page=page,
        per_page=per_page,
        search=search,
        tag_ids=tag_ids,
        category_id=category_id,
        is_favorite=is_favorite,
        min_rating=min_rating,
        max_cook_time=max_cook_time,
        sort_by=sort_by,
        sort_order=sort_order,
        public_only=user is None,
    )


@router.get("/{slug}", response_model=RecipeResponse)
async def get_recipe(
    slug: str,
    recipe_service: RecipeServiceDep,
    user: OptionalUser,
) -> RecipeResponse:
    return await recipe_service.get_recipe_by_slug(slug, public_only=user is None)


@router.post("", response_model=RecipeResponse, status_code=201)
async def create_recipe(
    data: RecipeCreate,
    recipe_service: RecipeServiceDep,
    current_user: CurrentUser,
    session: SessionDep,
) -> RecipeResponse:
    result = await recipe_service.create_recipe(data, current_user.id)
    await session.commit()
    return result


@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(
    recipe_id: str,
    data: RecipeUpdate,
    recipe_service: RecipeServiceDep,
    current_user: CurrentUser,
    session: SessionDep,
) -> RecipeResponse:
    result = await recipe_service.update_recipe(recipe_id, data)
    await session.commit()
    return result


@router.delete("/{recipe_id}", status_code=204)
async def delete_recipe(
    recipe_id: str,
    recipe_service: RecipeServiceDep,
    current_user: CurrentUser,
    session: SessionDep,
) -> None:
    await recipe_service.delete_recipe(recipe_id)
    await session.commit()


@router.post("/import", response_model=RecipeResponse, status_code=201)
async def import_recipe(
    data: RecipeImportRequest,
    scraper_service: ScraperServiceDep,
    current_user: CurrentUser,
    session: SessionDep,
) -> RecipeResponse:
    recipe = await scraper_service.import_from_url(data.url, current_user.id)
    await session.commit()
    return RecipeResponse.model_validate(recipe)


@router.patch("/{recipe_id}/favorite", response_model=RecipeResponse)
async def toggle_favorite(
    recipe_id: str,
    recipe_service: RecipeServiceDep,
    current_user: CurrentUser,
    session: SessionDep,
) -> RecipeResponse:
    result = await recipe_service.toggle_favorite(recipe_id)
    await session.commit()
    return result


@router.patch("/{recipe_id}/rating", response_model=RecipeResponse)
async def set_rating(
    recipe_id: str,
    rating: int | None = Query(None, ge=1, le=5),
    recipe_service: RecipeServiceDep = None,
    current_user: CurrentUser = None,
    session: SessionDep = None,
) -> RecipeResponse:
    result = await recipe_service.set_rating(recipe_id, rating)
    await session.commit()
    return result


@router.post("/{recipe_id}/images", response_model=ImageResponse, status_code=201)
async def upload_image(
    recipe_id: str,
    file: UploadFile,
    image_service: ImageServiceDep,
    current_user: CurrentUser,
    session: SessionDep,
    is_primary: bool = False,
    alt_text: str | None = None,
) -> ImageResponse:
    result = await image_service.upload_image(recipe_id, file, is_primary, alt_text)
    await session.commit()
    return ImageResponse.model_validate(result)


@router.delete("/images/{image_id}", status_code=204)
async def delete_image(
    image_id: str,
    image_service: ImageServiceDep,
    current_user: CurrentUser,
    session: SessionDep,
) -> None:
    await image_service.delete_image(image_id)
    await session.commit()
