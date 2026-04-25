from abc import ABC, abstractmethod


class BaseRepository[T](ABC):
    @abstractmethod
    async def get_by_id(self, id: str) -> T | None: ...

    @abstractmethod
    async def get_all(self) -> list[T]: ...

    @abstractmethod
    async def create(self, entity: T) -> T: ...

    @abstractmethod
    async def update(self, entity: T) -> T: ...

    @abstractmethod
    async def delete(self, id: str) -> bool: ...
