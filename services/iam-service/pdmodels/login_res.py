from pydantic import BaseModel

from pdmodels.user_req import RoleEnum


class LoginRes(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until expiry
    user_id: str
    username: str
    role: RoleEnum
