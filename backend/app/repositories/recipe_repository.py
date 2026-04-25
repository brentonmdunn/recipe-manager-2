from abc import abstractmethod

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.image import Image
from app.models.ingredient import Ingredient
from app.models.recipe import Recipe, recipe_tags
from app.models.recipe_step import RecipeStep
from app.models.tag import Tag
from app.repositories.base import BaseRepository


class RecipeRepository(BaseRepository[Recipe]):
    @abstractmethod
    async def get_by_slug(self, slug: str) -> Recipe | None: ...

    @abstractmethod
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
    ) -> tuple[list[Recipe], int]: ...

    @abstractmethod
    async def slug_exists(self, slug: str, exclude_id: str | None = None) -> bool: ...


class SqlAlchemyRecipeRepository(RecipeRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _eager_options(self) -> list:
        return [
            selectinload(Recipe.tags),
            selectinload(Recipe.ingredients),
            selectinload(Recipe.steps),
            selectinload(Recipe.images),
        ]

    async def get_by_id(self, id: str) -> Recipe | None:
        result = await self._session.execute(
            select(Recipe).options(*self._eager_options()).where(Recipe.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Recipe | None:
        result = await self._session.execute(
            select(Recipe).options(*self._eager_options()).where(Recipe.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Recipe]:
        result = await self._session.execute(
            select(Recipe).options(*self._eager_options())
        )
        return list(result.scalars().all())

    async def slug_exists(self, slug: str, exclude_id: str | None = None) -> bool:
        query = select(func.count(Recipe.id)).where(Recipe.slug == slug)
        if exclude_id:
            query = query.where(Recipe.id != exclude_id)
        result = await self._session.execute(query)
        return result.scalar_one() > 0

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
    ) -> tuple[list[Recipe], int]:
        query = select(Recipe).options(*self._eager_options())
        count_query = select(func.count(Recipe.id))

        if public_only:
            query = query.where(Recipe.is_public.is_(True))
            count_query = count_query.where(Recipe.is_public.is_(True))

        if search:
            search_filter = or_(
                Recipe.title.ilike(f"%{search}%"),
                Recipe.description.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        if tag_ids:
            query = query.join(recipe_tags).where(
                recipe_tags.c.tag_id.in_(tag_ids)
            )
            count_query = count_query.join(recipe_tags).where(
                recipe_tags.c.tag_id.in_(tag_ids)
            )

        if is_favorite is not None:
            query = query.where(Recipe.is_favorite.is_(is_favorite))
            count_query = count_query.where(Recipe.is_favorite.is_(is_favorite))

        if min_rating is not None:
            query = query.where(Recipe.rating >= min_rating)
            count_query = count_query.where(Recipe.rating >= min_rating)

        if max_cook_time is not None:
            query = query.where(Recipe.cook_time_minutes <= max_cook_time)
            count_query = count_query.where(
                Recipe.cook_time_minutes <= max_cook_time
            )

        sort_column = getattr(Recipe, sort_by, Recipe.created_at)
        if sort_order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await self._session.execute(query)
        recipes = list(result.scalars().unique().all())

        return recipes, total

    async def create(self, entity: Recipe) -> Recipe:
        self._session.add(entity)
        await self._session.flush()
        result = await self._session.execute(
            select(Recipe).options(*self._eager_options()).where(Recipe.id == entity.id)
        )
        return result.scalar_one()

    async def update(self, entity: Recipe) -> Recipe:
        await self._session.flush()
        result = await self._session.execute(
            select(Recipe).options(*self._eager_options()).where(Recipe.id == entity.id)
        )
        return result.scalar_one()

    async def delete(self, id: str) -> bool:
        recipe = await self.get_by_id(id)
        if recipe:
            await self._session.delete(recipe)
            await self._session.flush()
            return True
        return False

    async def add_tags(self, recipe: Recipe, tags: list[Tag]) -> Recipe:
        recipe.tags = tags
        await self._session.flush()
        return recipe

    async def set_ingredients(
        self, recipe: Recipe, ingredients: list[Ingredient]
    ) -> None:
        for ing in recipe.ingredients:
            await self._session.delete(ing)
        await self._session.flush()
        for ing in ingredients:
            ing.recipe_id = recipe.id
            self._session.add(ing)
        await self._session.flush()

    async def set_steps(self, recipe: Recipe, steps: list[RecipeStep]) -> None:
        for step in recipe.steps:
            await self._session.delete(step)
        await self._session.flush()
        for step in steps:
            step.recipe_id = recipe.id
            self._session.add(step)
        await self._session.flush()

    async def add_image(self, image: Image) -> Image:
        self._session.add(image)
        await self._session.flush()
        await self._session.refresh(image)
        return image

    async def delete_image(self, image_id: str) -> Image | None:
        image = await self._session.get(Image, image_id)
        if image:
            await self._session.delete(image)
            await self._session.flush()
            return image
        return None
