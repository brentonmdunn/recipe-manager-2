from fastapi import APIRouter
from slugify import slugify

from app.dependencies import CategoryRepoDep, CurrentUser, SessionDep
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryResponse])
async def list_categories(
    category_repo: CategoryRepoDep,
) -> list[CategoryResponse]:
    categories = await category_repo.get_all()
    return [CategoryResponse.model_validate(c) for c in categories]


@router.post("", response_model=CategoryResponse, status_code=201)
async def create_category(
    data: CategoryCreate,
    category_repo: CategoryRepoDep,
    current_user: CurrentUser,
    session: SessionDep,
) -> CategoryResponse:
    category = Category(name=data.name, slug=slugify(data.name))
    category = await category_repo.create(category)
    await session.commit()
    return CategoryResponse.model_validate(category)


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: str,
    category_repo: CategoryRepoDep,
    current_user: CurrentUser,
    session: SessionDep,
) -> None:
    await category_repo.delete(category_id)
    await session.commit()
