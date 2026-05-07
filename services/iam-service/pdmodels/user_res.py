from datetime import datetime

from pydantic import BaseModel, ConfigDict

from pdmodels.user_req import RoleEnum


class UserRes(BaseModel):
    """Public user response — never includes password hash."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    email: str
    role: RoleEnum
    full_name: str | None
    created_at: datetime
