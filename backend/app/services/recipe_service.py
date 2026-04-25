from fastapi import HTTPException, status
from slugify import slugify

from app.models.ingredient import Ingredient
from app.models.recipe import Recipe
from app.models.recipe_step import RecipeStep
from app.repositories.recipe_repository import SqlAlchemyRecipeRepository
from app.repositories.tag_repository import SqlAlchemyTagRepository
from app.schemas.recipe import (
    PaginatedResponse,
    RecipeCreate,
    RecipeListResponse,
    RecipeResponse,
    RecipeUpdate,
)
from app.utils.pagination import calculate_pages


class RecipeService:
    def __init__(
        self,
        recipe_repo: SqlAlchemyRecipeRepository,
        tag_repo: SqlAlchemyTagRepository,
    ) -> None:
        self._recipe_repo = recipe_repo
        self._tag_repo = tag_repo

    async def _generate_unique_slug(
        self, title: str, exclude_id: str | None = None
    ) -> str:
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        while await self._recipe_repo.slug_exists(slug, exclude_id):
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    def _build_list_response(self, recipe: Recipe) -> RecipeListResponse:
        primary_image = next(
            (img for img in recipe.images if img.is_primary),
            recipe.images[0] if recipe.images else None,
        )
        return RecipeListResponse.model_validate(
            {
                **{
                    c.key: getattr(recipe, c.key)
                    for c in recipe.__table__.columns
                },
                "tags": recipe.tags,
                "primary_image": primary_image,
            }
        )

    async def create_recipe(
        self, data: RecipeCreate, user_id: str
    ) -> RecipeResponse:
        slug = await self._generate_unique_slug(data.title)

        recipe = Recipe(
            title=data.title,
            slug=slug,
            description=data.description,
            prep_time_minutes=data.prep_time_minutes,
            cook_time_minutes=data.cook_time_minutes,
            total_time_minutes=data.total_time_minutes,
            servings=data.servings,
            servings_unit=data.servings_unit,
            source_url=data.source_url,
            nutrition_info=data.nutrition_info,
            is_public=data.is_public,
            user_id=user_id,
        )

        recipe.ingredients = [
            Ingredient(**ing.model_dump(), recipe_id="temp") for ing in data.ingredients
        ]
        recipe.steps = [
            RecipeStep(**step.model_dump(), recipe_id="temp") for step in data.steps
        ]

        recipe = await self._recipe_repo.create(recipe)

        if data.tag_ids:
            tags = await self._tag_repo.get_by_ids(data.tag_ids)
            await self._recipe_repo.add_tags(recipe, tags)

        recipe = await self._recipe_repo.get_by_id(recipe.id)
        return RecipeResponse.model_validate(recipe)

    async def get_recipe_by_slug(
        self, slug: str, public_only: bool = False
    ) -> RecipeResponse:
        recipe = await self._recipe_repo.get_by_slug(slug)
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found",
            )
        if public_only and not recipe.is_public:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found",
            )
        return RecipeResponse.model_validate(recipe)

    async def list_recipes(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
        search: str | None = None,
        tag_ids: list[str] | None = None,
        is_favorite: bool | None = None,
        min_rating: int | None = None,
        max_cook_time: int | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        public_only: bool = False,
    ) -> PaginatedResponse:
        recipes, total = await self._recipe_repo.list_recipes(
            page=page,
            per_page=per_page,
            search=search,
            tag_ids=tag_ids,
            is_favorite=is_favorite,
            min_rating=min_rating,
            max_cook_time=max_cook_time,
            sort_by=sort_by,
            sort_order=sort_order,
            public_only=public_only,
        )

        items = [self._build_list_response(r) for r in recipes]

        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            pages=calculate_pages(total, per_page),
        )

    async def update_recipe(
        self, recipe_id: str, data: RecipeUpdate
    ) -> RecipeResponse:
        recipe = await self._recipe_repo.get_by_id(recipe_id)
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found",
            )

        update_data = data.model_dump(exclude_unset=True)

        if "title" in update_data and "slug" not in update_data:
            update_data["slug"] = await self._generate_unique_slug(
                update_data["title"], exclude_id=recipe_id
            )
        elif "slug" in update_data:
            if await self._recipe_repo.slug_exists(
                update_data["slug"], exclude_id=recipe_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Slug already in use",
                )

        tag_ids = update_data.pop("tag_ids", None)
        ingredients_data = update_data.pop("ingredients", None)
        steps_data = update_data.pop("steps", None)

        for key, value in update_data.items():
            setattr(recipe, key, value)

        if tag_ids is not None:
            tags = await self._tag_repo.get_by_ids(tag_ids)
            await self._recipe_repo.add_tags(recipe, tags)

        if ingredients_data is not None:
            ingredients = [
                Ingredient(**ing.model_dump()) for ing in ingredients_data
            ]
            await self._recipe_repo.set_ingredients(recipe, ingredients)

        if steps_data is not None:
            steps = [RecipeStep(**step.model_dump()) for step in steps_data]
            await self._recipe_repo.set_steps(recipe, steps)

        recipe = await self._recipe_repo.update(recipe)
        return RecipeResponse.model_validate(recipe)

    async def delete_recipe(self, recipe_id: str) -> None:
        deleted = await self._recipe_repo.delete(recipe_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found",
            )

    async def toggle_favorite(self, recipe_id: str) -> RecipeResponse:
        recipe = await self._recipe_repo.get_by_id(recipe_id)
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found",
            )
        recipe.is_favorite = not recipe.is_favorite
        recipe = await self._recipe_repo.update(recipe)
        return RecipeResponse.model_validate(recipe)

    async def set_rating(self, recipe_id: str, rating: int | None) -> RecipeResponse:
        if rating is not None and not 1 <= rating <= 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5",
            )
        recipe = await self._recipe_repo.get_by_id(recipe_id)
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found",
            )
        recipe.rating = rating
        recipe = await self._recipe_repo.update(recipe)
        return RecipeResponse.model_validate(recipe)
