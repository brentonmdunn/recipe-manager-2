from fastapi import HTTPException, status

from app.models.share_link import ShareLink
from app.repositories.recipe_repository import SqlAlchemyRecipeRepository
from app.repositories.share_link_repository import ShareLinkRepository
from app.schemas.recipe import RecipeResponse
from app.schemas.share_link import ShareLinkResponse


class ShareLinkService:
    def __init__(
        self,
        share_link_repo: ShareLinkRepository,
        recipe_repo: SqlAlchemyRecipeRepository,
    ) -> None:
        self._share_link_repo = share_link_repo
        self._recipe_repo = recipe_repo

    async def create_share_link(self, recipe_id: str) -> ShareLinkResponse:
        recipe = await self._recipe_repo.get_by_id(recipe_id)
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found",
            )
        share_link = ShareLink(recipe_id=recipe_id)
        share_link = await self._share_link_repo.create(share_link)
        return ShareLinkResponse.model_validate(share_link)

    async def list_share_links(self, recipe_id: str) -> list[ShareLinkResponse]:
        links = await self._share_link_repo.list_by_recipe(recipe_id)
        return [ShareLinkResponse.model_validate(link) for link in links]

    async def delete_share_link(self, share_link_id: str) -> None:
        deleted = await self._share_link_repo.delete(share_link_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Share link not found",
            )

    async def get_recipe_by_token(self, token: str) -> RecipeResponse:
        share_link = await self._share_link_repo.get_by_token(token)
        if not share_link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shared recipe not found",
            )
        return RecipeResponse.model_validate(share_link.recipe)
