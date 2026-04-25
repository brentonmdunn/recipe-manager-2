from datetime import datetime

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: str
    username: str
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}
