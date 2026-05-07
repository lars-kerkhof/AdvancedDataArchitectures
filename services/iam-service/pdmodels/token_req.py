from pydantic import BaseModel


class TokenReq(BaseModel):
    """Payload for the /validate endpoint."""
    token: str
