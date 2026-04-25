from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.category import CategoryResponse
from app.schemas.tag import TagResponse


class IngredientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    quantity: float | None = None
    unit: str | None = Field(default=None, max_length=50)
    notes: str | None = Field(default=None, max_length=255)
    group_name: str | None = Field(default=None, max_length=100)
    position: int = 0


class IngredientResponse(BaseModel):
    id: str
    name: str
    quantity: float | None
    unit: str | None
    notes: str | None
    group_name: str | None
    position: int

    model_config = {"from_attributes": True}


class RecipeStepCreate(BaseModel):
    step_number: int
    instruction: str = Field(min_length=1)


class RecipeStepResponse(BaseModel):
    id: str
    step_number: int
    instruction: str
    image_id: str | None

    model_config = {"from_attributes": True}


class ImageResponse(BaseModel):
    id: str
    file_path: str
    is_primary: bool
    alt_text: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RecipeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    prep_time_minutes: int | None = Field(default=None, ge=0)
    cook_time_minutes: int | None = Field(default=None, ge=0)
    total_time_minutes: int | None = Field(default=None, ge=0)
    servings: int | None = Field(default=None, ge=1)
    servings_unit: str | None = Field(default=None, max_length=50)
    source_url: str | None = Field(default=None, max_length=2048)
    nutrition_info: str | None = None
    is_public: bool = True
    category_id: str | None = None
    tag_ids: list[str] = Field(default_factory=list)
    ingredients: list[IngredientCreate] = Field(default_factory=list)
    steps: list[RecipeStepCreate] = Field(default_factory=list)


class RecipeUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    slug: str | None = Field(default=None, min_length=1, max_length=280)
    description: str | None = None
    prep_time_minutes: int | None = Field(default=None, ge=0)
    cook_time_minutes: int | None = Field(default=None, ge=0)
    total_time_minutes: int | None = Field(default=None, ge=0)
    servings: int | None = Field(default=None, ge=1)
    servings_unit: str | None = Field(default=None, max_length=50)
    source_url: str | None = Field(default=None, max_length=2048)
    nutrition_info: str | None = None
    is_public: bool | None = None
    category_id: str | None = None
    tag_ids: list[str] | None = None
    ingredients: list[IngredientCreate] | None = None
    steps: list[RecipeStepCreate] | None = None


class RecipeResponse(BaseModel):
    id: str
    title: str
    slug: str
    description: str | None
    prep_time_minutes: int | None
    cook_time_minutes: int | None
    total_time_minutes: int | None
    servings: int | None
    servings_unit: str | None
    source_url: str | None
    nutrition_info: str | None
    is_public: bool
    is_favorite: bool
    rating: int | None
    category: CategoryResponse | None
    tags: list[TagResponse]
    ingredients: list[IngredientResponse]
    steps: list[RecipeStepResponse]
    images: list[ImageResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RecipeListResponse(BaseModel):
    id: str
    title: str
    slug: str
    description: str | None
    prep_time_minutes: int | None
    cook_time_minutes: int | None
    total_time_minutes: int | None
    servings: int | None
    is_public: bool
    is_favorite: bool
    rating: int | None
    category: CategoryResponse | None
    tags: list[TagResponse]
    primary_image: ImageResponse | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RecipeImportRequest(BaseModel):
    url: str = Field(max_length=2048)


class PaginatedResponse(BaseModel):
    items: list[RecipeListResponse]
    total: int
    page: int
    per_page: int
    pages: int
