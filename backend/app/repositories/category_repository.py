from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    pass


class SqlAlchemyCategoryRepository(CategoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, id: str) -> Category | None:
        return await self._session.get(Category, id)

    async def get_all(self) -> list[Category]:
        result = await self._session.execute(
            select(Category).order_by(Category.name)
        )
        return list(result.scalars().all())

    async def create(self, entity: Category) -> Category:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def update(self, entity: Category) -> Category:
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def delete(self, id: str) -> bool:
        category = await self.get_by_id(id)
        if category:
            await self._session.delete(category)
            await self._session.flush()
            return True
        return False
