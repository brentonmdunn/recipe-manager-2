from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag
from app.repositories.base import BaseRepository


class TagRepository(BaseRepository[Tag]):
    pass


class SqlAlchemyTagRepository(TagRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, id: str) -> Tag | None:
        return await self._session.get(Tag, id)

    async def get_all(self) -> list[Tag]:
        result = await self._session.execute(select(Tag).order_by(Tag.name))
        return list(result.scalars().all())

    async def get_by_ids(self, ids: list[str]) -> list[Tag]:
        if not ids:
            return []
        result = await self._session.execute(select(Tag).where(Tag.id.in_(ids)))
        return list(result.scalars().all())

    async def create(self, entity: Tag) -> Tag:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def update(self, entity: Tag) -> Tag:
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def delete(self, id: str) -> bool:
        tag = await self.get_by_id(id)
        if tag:
            await self._session.delete(tag)
            await self._session.flush()
            return True
        return False
