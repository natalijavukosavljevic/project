"""Token schemas."""
from pydantic import BaseModel


class TokenSchema(BaseModel):
    """Schema for JWT tokens."""

    access_token: str


class TokenPayload(BaseModel):
    """Payload of JWT token."""

    sub: str = None
    exp: int = None
