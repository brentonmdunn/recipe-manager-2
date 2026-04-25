from datetime import datetime

from pydantic import BaseModel


class ShareLinkCreate(BaseModel):
    recipe_id: str


class ShareLinkResponse(BaseModel):
    id: str
    token: str
    recipe_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
