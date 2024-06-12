"""Schemas."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Base model for creating a project."""

    name: str
    description: str


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


class TokenSchema(BaseModel):
    """Schema for JWT tokens."""

    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    """Payload of JWT token."""

    sub: str = None
    exp: int = None


class UserAuth(BaseModel):
    """Model for user authentication."""

    email: str = Field(..., description="user email")
    password: str = Field(
        ..., min_length=5, max_length=24, description="user password",
    )


class UserOut(BaseModel):
    """Model representing user details."""

    user_id: int
    email: str



