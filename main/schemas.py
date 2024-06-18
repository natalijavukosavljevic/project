"""Schemas."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ProjectBase(BaseModel):
    """Base model for creating a project."""

    name: str
    description: str

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


class ProjectBaseUpdate(BaseModel):
    """Schema for updating a project."""

    name: Optional[str] = None  # noqa: UP007
    description: Optional[str] = None # noqa: UP007
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


class ProjectOut(BaseModel):
    """Model representing project details."""

    project_id: int
    name: str
    description: str
    owner_id: int
    logo_id: Optional[int]  # noqa: UP007


class DocumentOut(BaseModel):
    """Model representing document details."""

    document_id: int
    document_name: str
    content: Optional[str]  # Assuming content is optional  # noqa: UP007


class ProjectOutWithDocuments(BaseModel):
    """Model representing project details along with associated documents."""

    project_id: int
    owner_id: int
    name: str
    description: str
    logo_id: Optional[int]  # Assuming logo_id is optional  # noqa: UP007
    documents: list[DocumentOut] = []  # List of associated documents

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


class TokenSchema(BaseModel):
    """Schema for JWT tokens."""

    access_token: str


class TokenPayload(BaseModel):
    """Payload of JWT token."""

    sub: str = None
    exp: int = None


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



