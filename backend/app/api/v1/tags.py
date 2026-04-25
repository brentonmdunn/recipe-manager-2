from fastapi import APIRouter
from slugify import slugify

from app.dependencies import CurrentUser, SessionDep, TagRepoDep
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagResponse

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagResponse])
async def list_tags(tag_repo: TagRepoDep) -> list[TagResponse]:
    tags = await tag_repo.get_all()
    return [TagResponse.model_validate(t) for t in tags]


@router.post("", response_model=TagResponse, status_code=201)
async def create_tag(
    data: TagCreate,
    tag_repo: TagRepoDep,
    current_user: CurrentUser,
    session: SessionDep,
) -> TagResponse:
    tag = Tag(name=data.name, slug=slugify(data.name))
    tag = await tag_repo.create(tag)
    await session.commit()
    return TagResponse.model_validate(tag)


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: str,
    tag_repo: TagRepoDep,
    current_user: CurrentUser,
    session: SessionDep,
) -> None:
    await tag_repo.delete(tag_id)
    await session.commit()
