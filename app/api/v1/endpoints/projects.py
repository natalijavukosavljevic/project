"""Project endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: TCH002

from app.crud.project import (
    create_project,
    get_projects,
)
from app.crud.user import get_authenticated_user
from app.db.session import get_db
from app.models.project import Project  # noqa: TCH001
from app.schemas.project import (
    ProjectBase,
    ProjectOut,
    ProjectOutWithDocuments,
)

router = APIRouter()
auth_header1 = APIKeyHeader(name="Authorization", scheme_name="Bearer")


@router.get("/", response_model=list[ProjectOutWithDocuments])
async def read_projects(
    request: Request,
    header_value1: str = Depends(auth_header1),  # noqa: ARG001
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> list[ProjectOutWithDocuments]:
    """Retrieve all projects with associated documents.

    Args:
    ----
    request (Request): The incoming request.
    header_value1 (str, optional): Header value for authentication.
    Defaults to Depends(auth_header1).
    db (AsyncSession, optional): AsyncSession dependency for database
    operations.
    Defaults to Depends(get_db).

    Returns:
    -------
    list[ProjectOutWithDocuments]: A list of projects
    with associated documents.

    """
    user_obj = await get_authenticated_user(request, db)
    return await get_projects(db, user_obj)


@router.post("/", response_model=ProjectOut)
async def write_project(
    project: ProjectBase,
    request: Request,
    header_value1: str = Depends(auth_header1),  # noqa: ARG001
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> Project:
    """Create a new project.

    Args:
    ----
    project (ProjectBase): Data to create a new project.
    request (Request): The incoming request.
    header_value1 (str, optional): Header value for authentication.
    Defaults to Depends(auth_header1).
    db (AsyncSession, optional): AsyncSession dependency for
    database operations.
    Defaults to Depends(get_db).

    Returns:
    -------
    Project: The newly created project.

    """
    user_obj = await get_authenticated_user(request, db)
    return await create_project(db, project, user_obj)
