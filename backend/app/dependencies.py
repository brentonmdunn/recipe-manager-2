from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.user import User
from app.repositories.recipe_repository import SqlAlchemyRecipeRepository
from app.repositories.share_link_repository import ShareLinkRepository
from app.repositories.tag_repository import SqlAlchemyTagRepository
from app.repositories.user_repository import SqlAlchemyUserRepository
from app.services.auth_service import AuthService
from app.services.image_service import ImageService
from app.services.recipe_service import RecipeService
from app.services.scraper_service import ScraperService
from app.services.share_link_service import ShareLinkService


async def get_user_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(session)


async def get_recipe_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SqlAlchemyRecipeRepository:
    return SqlAlchemyRecipeRepository(session)


async def get_tag_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SqlAlchemyTagRepository:
    return SqlAlchemyTagRepository(session)


async def get_auth_service(
    user_repo: Annotated[SqlAlchemyUserRepository, Depends(get_user_repo)],
) -> AuthService:
    return AuthService(user_repo)


async def get_recipe_service(
    recipe_repo: Annotated[SqlAlchemyRecipeRepository, Depends(get_recipe_repo)],
    tag_repo: Annotated[SqlAlchemyTagRepository, Depends(get_tag_repo)],
) -> RecipeService:
    return RecipeService(recipe_repo, tag_repo)


async def get_scraper_service(
    recipe_repo: Annotated[SqlAlchemyRecipeRepository, Depends(get_recipe_repo)],
) -> ScraperService:
    return ScraperService(recipe_repo)


async def get_image_service(
    recipe_repo: Annotated[SqlAlchemyRecipeRepository, Depends(get_recipe_repo)],
) -> ImageService:
    return ImageService(recipe_repo)


async def get_share_link_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ShareLinkRepository:
    return ShareLinkRepository(session)


async def get_share_link_service(
    share_link_repo: Annotated[ShareLinkRepository, Depends(get_share_link_repo)],
    recipe_repo: Annotated[SqlAlchemyRecipeRepository, Depends(get_recipe_repo)],
) -> ShareLinkService:
    return ShareLinkService(share_link_repo, recipe_repo)


async def get_current_user(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    authorization: str = Header(None),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )
    token = authorization.removeprefix("Bearer ")
    return await auth_service.get_current_user(token)


async def get_optional_user(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    authorization: str = Header(None),
) -> User | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.removeprefix("Bearer ")
    try:
        return await auth_service.get_current_user(token)
    except HTTPException:
        return None


# Type aliases for cleaner route signatures
SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
RecipeServiceDep = Annotated[RecipeService, Depends(get_recipe_service)]
ScraperServiceDep = Annotated[ScraperService, Depends(get_scraper_service)]
ImageServiceDep = Annotated[ImageService, Depends(get_image_service)]
ShareLinkServiceDep = Annotated[ShareLinkService, Depends(get_share_link_service)]
TagRepoDep = Annotated[SqlAlchemyTagRepository, Depends(get_tag_repo)]
