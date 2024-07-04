"""Document schemas."""


from pydantic import BaseModel


class DocumentOut(BaseModel):
    """Model representing document details."""

    document_id : int
    document_name: str

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


class DocumentName(BaseModel):
    """Model representing document details."""

    document_name: str

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
