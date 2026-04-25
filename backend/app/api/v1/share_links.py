from fastapi import APIRouter

from app.dependencies import CurrentUser, SessionDep, ShareLinkServiceDep
from app.schemas.recipe import RecipeResponse
from app.schemas.share_link import ShareLinkCreate, ShareLinkResponse

router = APIRouter(prefix="/share", tags=["share"])


@router.post("", response_model=ShareLinkResponse, status_code=201)
async def create_share_link(
    data: ShareLinkCreate,
    share_link_service: ShareLinkServiceDep,
    current_user: CurrentUser,
    session: SessionDep,
) -> ShareLinkResponse:
    result = await share_link_service.create_share_link(data.recipe_id)
    await session.commit()
    return result


@router.get("/{recipe_id}", response_model=list[ShareLinkResponse])
async def list_share_links(
    recipe_id: str,
    share_link_service: ShareLinkServiceDep,
    current_user: CurrentUser,
) -> list[ShareLinkResponse]:
    return await share_link_service.list_share_links(recipe_id)


@router.delete("/{share_link_id}", status_code=204)
async def delete_share_link(
    share_link_id: str,
    share_link_service: ShareLinkServiceDep,
    current_user: CurrentUser,
    session: SessionDep,
) -> None:
    await share_link_service.delete_share_link(share_link_id)
    await session.commit()


@router.get("/token/{token}", response_model=RecipeResponse)
async def get_shared_recipe(
    token: str,
    share_link_service: ShareLinkServiceDep,
) -> RecipeResponse:
    return await share_link_service.get_recipe_by_token(token)
