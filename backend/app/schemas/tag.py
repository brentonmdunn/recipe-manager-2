from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class TagResponse(BaseModel):
    id: str
    name: str
    slug: str

    model_config = {"from_attributes": True}
