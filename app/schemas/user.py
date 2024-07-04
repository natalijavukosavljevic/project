"""User schemas."""

from pydantic import BaseModel


class UserAuth(BaseModel):
    """Model for user authentication."""

    email: str
    password: str
    repeat_password: str

    class Config:
        """Configuration for Pydantic model to support ORM mode.

        Attributes
        ----------
        orm_mode : bool
            If set to True, enables Pydantic to work with ORM models
            (e.g., SQLAlchemy models), allowing automatic conversion
            from ORM instances to Pydantic models.

        """

        orm_mode = True


class UserOut(BaseModel):
    """Model representing user details."""

    user_id: int
    email: str
