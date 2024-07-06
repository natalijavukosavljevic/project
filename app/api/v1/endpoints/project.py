"""Project endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request, Response, UploadFile
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: TCH002

from app.crud.project import (
    delete_logo,
    delete_project,
    download_logo,
    get_documents,
    get_project,
    invite,
    update_project,
    upload_documents,
    upload_logo,
)
from app.crud.user import get_authenticated_user
from app.db.session import get_db
from app.models.project import Project  # noqa: TCH001
from app.schemas.document import DocumentName
from app.schemas.image import LogoOut
from app.schemas.project import (
    DocumentOut,
    ProjectBaseUpdate,
    ProjectOut,
    ResponseMessage,
)

router = APIRouter()
auth_header1 = APIKeyHeader(name="Authorization", scheme_name="Bearer")





@router.get("/{project_id}/info", response_model=ProjectOut)
async def read_project(
    project_id: int,
    request: Request,
    header_value1: str = Depends(auth_header1),  # noqa: ARG001
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> Project:
    """Retrieve a specific project by ID.

    Args:
    ----
    project_id (int): The ID of the project to retrieve.
    request (Request): The incoming request.
    header_value1 (str, optional): Header value for authentication.
    Defaults to Depends(auth_header1).
    db (AsyncSession, optional): AsyncSession dependency for
    database operations.
    Defaults to Depends(get_db).

    Returns:
    -------
    Project: The project identified by project_id.

    """
    user_obj = await get_authenticated_user(request, db)
    return await get_project(db, project_id, user_obj)


@router.put("/{project_id}/info", response_model=ProjectBaseUpdate)
async def update_existing_project(
    project_id: int,
    project_data: ProjectBaseUpdate,
    request: Request,
    header_value1: str = Depends(auth_header1),  # noqa: ARG001
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> ProjectBaseUpdate:
    """Update an existing project.

    Args:
    ----
    project_id (int): The ID of the project to update.
    project_data (ProjectBaseUpdate): Data to update the project.
    request (Request): The incoming request.
    header_value1 (str, optional): Header value for authentication.
    Defaults to Depends(auth_header1).
    db (AsyncSession, optional): AsyncSession dependency
    for database operations.
    Defaults to Depends(get_db).

    Returns:
    -------
    ProjectBaseUpdate: The updated project data.

    """
    user_obj = await get_authenticated_user(request, db)
    return await update_project(db, project_id, user_obj, project_data)


@router.delete("/{project_id}", response_model=ResponseMessage)
async def delete_existing_project(
    project_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    header_value1: str = Depends(auth_header1),  # noqa: ARG001
) -> dict[str, str]:
    """Delete an existing project.

    Args:
    ----
    project_id (int): The ID of the project to delete.
    request (Request): The incoming request.
    db (AsyncSession, optional): AsyncSession dependency
    for database operations.
    Defaults to Depends(get_db).
    header_value1 (str, optional): Header value for authentication.
    Defaults to Depends(auth_header1).

    Returns:
    -------
    dict[str, str]: A message confirming the deletion.

    """
    user_obj = await get_authenticated_user(request, db)
    return await delete_project(db, project_id, user_obj)


@router.post(
    "/{project_id}/invite",
    summary="Grant access to the project",
    response_model=ResponseMessage,
)
async def invite_user_to_project(
    project_id: int,
    request: Request,
    header_value1: str = Depends(auth_header1),  # noqa: ARG001
    db: AsyncSession = Depends(get_db),  # noqa: B008
    user_email: str = Query(..., description="Email of the user to invite"),
) -> dict[str, str]:
    """Invite a user to access a project.

    Args:
    ----
    project_id (int): The ID of the project to invite the user to.
    request (Request): The incoming request.
    header_value1 (str, optional): Header value for authentication.
      Defaults to Depends(auth_header1).
    db (AsyncSession, optional): AsyncSession dependency
    for database operations. Defaults to Depends(get_db).
    user_email (str): Email of the user to invite.

    Returns:
    -------
    dict[str, str]: A message confirming the invitation.

    """
    user_obj = await get_authenticated_user(request, db)
    return await invite(db, user_email, user_obj, project_id)


@router.post(
    "/{project_id}/documents", response_model=list[DocumentName],
)
async def upload_project_documents(
    project_id: int,
    request: Request,
    files: list[UploadFile],
    header_value1: str = Depends(auth_header1),  # noqa: ARG001
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> list[DocumentName]:
    """Upload documents to a project.

    Args:
    ----
    project_id (int): The ID of the project to upload documents to.
    request (Request): The incoming request.
    files (list[UploadFile]): List of uploaded files.
    header_value1 (str, optional): Header value for authentication.
    Defaults to Depends(auth_header1).
    db (AsyncSession, optional): AsyncSession dependency
    for database operations. Defaults to Depends(get_db).

    Returns:
    -------
    list[DocumentOut]: List of uploaded documents with details.

    """
    user_obj = await get_authenticated_user(request, db)
    return await upload_documents(db, files, user_obj, project_id)


@router.get(
    "/{project_id}/documents", response_model=list[DocumentOut],
)
async def get_project_documents(
    project_id: int,
    request: Request,
    header_value1: str = Depends(auth_header1),  # noqa: ARG001
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> list[DocumentOut]:
    """Retrieve documents associated with a project.

    Args:
    ----
    project_id (int): The ID of the project to retrieve documents from.
    request (Request): The incoming request.
    header_value1 (str, optional): Header value for authentication.
    Defaults to Depends(auth_header1).
    db (AsyncSession, optional): AsyncSession dependency
    for database operations. Defaults to Depends(get_db).

    Returns:
    -------
    list[DocumentOut]: List of documents associated with the project.

    """
    user_obj = await get_authenticated_user(request, db)
    return await get_documents(db, project_id ,user_obj)










@router.get("/{project_id}/logo")
async def get_project_logo(
    project_id: int,
    request: Request,
    header_value1: str = Depends(auth_header1),  # noqa: ARG001
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> Response:
    """Download the logo of a project.

    Args:
    ----
    project_id (int): The ID of the project whose logo to download.
    request (Request): The incoming request.
    header_value1 (str, optional): Header value for authentication.
      Defaults to Depends(auth_header1).
    db (AsyncSession, optional): AsyncSession dependency
    for database operations. Defaults to Depends(get_db).

    Returns:
    -------
    Response: The logo file response.

    """
    user_obj = await get_authenticated_user(request, db)
    return await download_logo(project_id, db, user_obj)


@router.put("/{project_id}/logo", response_model=LogoOut)
async def upload_project_logo(
    project_id: int,
    request: Request,
    file: UploadFile,
    header_value1: str = Depends(auth_header1),  # noqa: ARG001
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> LogoOut:
    """Upload a logo for a project.

    Args:
    ----
    project_id (int): The ID of the project to upload the logo to.
    request (Request): The incoming request.
    file (UploadFile): The logo file to upload.
    header_value1 (str, optional): Header value for authentication.
    Defaults to Depends(auth_header1).
    db (AsyncSession, optional): AsyncSession dependency
    for database operations. Defaults to Depends(get_db).

    Returns:
    -------
    LogoOut: Details of the uploaded logo.

    """
    user_obj = await get_authenticated_user(request, db)
    return await upload_logo(project_id, file, user_obj, db)


@router.delete("/{project_id}/logo", response_model=ResponseMessage)
async def delete_project_logo(
    project_id: int,
    request: Request,
    header_value1: str = Depends(auth_header1),  # noqa: ARG001
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> dict[str, str]:
    """Delete the logo of a project.

    Args:
    ----
    project_id (int): The ID of the project whose logo to delete.
    request (Request): The incoming request.
    header_value1 (str, optional): Header value for authentication.
    Defaults to Depends(auth_header1).
    db (AsyncSession, optional): AsyncSession dependency
    for database operations.
    Defaults to Depends(get_db).

    Returns:
    -------
    dict[str, str]: A message confirming the deletion.

    """
    user_obj = await get_authenticated_user(request, db)
    return await delete_logo(project_id, db, user_obj)
