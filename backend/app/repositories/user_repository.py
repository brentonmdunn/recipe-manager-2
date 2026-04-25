from abc import abstractmethod

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    @abstractmethod
    async def get_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    async def count(self) -> int: ...


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, id: str) -> User | None:
        return await self._session.get(User, id)

    async def get_all(self) -> list[User]:
        result = await self._session.execute(select(User))
        return list(result.scalars().all())

    async def get_by_username(self, username: str) -> User | None:
        result = await self._session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def count(self) -> int:
        result = await self._session.execute(select(func.count(User.id)))
        return result.scalar_one()

    async def create(self, entity: User) -> User:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def update(self, entity: User) -> User:
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def delete(self, id: str) -> bool:
        user = await self.get_by_id(id)
        if user:
            await self._session.delete(user)
            await self._session.flush()
            return True
        return False
