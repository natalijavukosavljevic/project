"""Image schemas."""
from pydantic import BaseModel


class LogoOut(BaseModel):
    """Model representing document details."""

    image_id: int
    image_name: str

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
