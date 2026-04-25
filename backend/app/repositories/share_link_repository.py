from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.recipe import Recipe
from app.models.share_link import ShareLink


class ShareLinkRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _recipe_eager_options(self) -> list:
        return [
            selectinload(Recipe.tags),
            selectinload(Recipe.ingredients),
            selectinload(Recipe.steps),
            selectinload(Recipe.images),
        ]

    async def create(self, share_link: ShareLink) -> ShareLink:
        self._session.add(share_link)
        await self._session.flush()
        await self._session.refresh(share_link)
        return share_link

    async def get_by_token(self, token: str) -> ShareLink | None:
        result = await self._session.execute(
            select(ShareLink)
            .options(selectinload(ShareLink.recipe).options(*self._recipe_eager_options()))
            .where(ShareLink.token == token)
        )
        return result.scalar_one_or_none()

    async def list_by_recipe(self, recipe_id: str) -> list[ShareLink]:
        result = await self._session.execute(
            select(ShareLink)
            .where(ShareLink.recipe_id == recipe_id)
            .order_by(ShareLink.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete(self, share_link_id: str) -> bool:
        share_link = await self._session.get(ShareLink, share_link_id)
        if share_link:
            await self._session.delete(share_link)
            await self._session.flush()
            return True
        return False
