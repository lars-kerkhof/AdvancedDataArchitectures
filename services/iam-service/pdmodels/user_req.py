from enum import Enum

from pydantic import BaseModel, Field


class RoleEnum(str, Enum):
    participant = "participant"
    staff = "staff"
    organizer = "organizer"


class UserReq(BaseModel):
    """Payload for user registration."""
    username: str = Field(min_length=3, max_length=64)
    email: str
    password: str = Field(min_length=8, description="Plain-text password; will be hashed before storage")
    role: RoleEnum = RoleEnum.participant
    full_name: str | None = None
