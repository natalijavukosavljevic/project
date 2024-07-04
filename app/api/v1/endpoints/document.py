"""Document endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response, UploadFile
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: TCH002

from app.crud.document import (
    delete_document,
    download_document,
    update_document,
)
from app.crud.user import get_authenticated_user
from app.db.session import get_db
from app.schemas.project import (
    DocumentOut,
    ResponseMessage,
)

router = APIRouter()
auth_header1 = APIKeyHeader(name="Authorization", scheme_name="Bearer")


@router.get("/{document_id}/download")
async def download_project_documents(
    document_id: int,
    request: Request,
    header_value1: str = Depends(auth_header1),  # noqa: ARG001
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> Response:
    """Download a document associated with a project.

    Args:
    ----
    document_id (int): The ID of the document to download.
    request (Request): The incoming request.
    header_value1 (str, optional): Header value for authentication.
    Defaults to Depends(auth_header1).
    db (AsyncSession, optional): AsyncSession dependency
    for database operations. Defaults to Depends(get_db).

    Returns:
    -------
    Response: The file response for download.

    """
    # Retrieve authenticated user
    user_obj = await get_authenticated_user(request, db)
    return await download_document(document_id, user_obj, db)


@router.put("/{document_id}", response_model=DocumentOut)
async def update_project_documents(
    document_id: int,
    request: Request,
    file: UploadFile,
    header_value1: str = Depends(auth_header1),  # noqa: ARG001
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> DocumentOut:
    """Update a document associated with a project.

    Args:
    ----
    document_id (int): The ID of the document to update.
    request (Request): The incoming request.
    file (UploadFile): The updated file.
    header_value1 (str, optional): Header value for authentication.
    Defaults to Depends(auth_header1).
    db (AsyncSession, optional): AsyncSession dependency
    for database operations. Defaults to Depends(get_db).

    Returns:
    -------
    DocumentOut: The updated document details.

    """
    user_obj = await get_authenticated_user(request, db)
    return await update_document(document_id, file, db, user_obj)



@router.delete("/{document_id}", response_model=ResponseMessage)
async def delete_project_documents(
    document_id: int,
    request: Request,
    header_value1: str = Depends(auth_header1),  # noqa: ARG001
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> dict[str, str]:
    """Delete a document associated with a project.

    Args:
    ----
    document_id (int): The ID of the document to delete.
    request (Request): The incoming request.
    header_value1 (str, optional): Header value for authentication.
    Defaults to Depends(auth_header1).
    db (AsyncSession, optional): AsyncSession dependency
    for database operations.Defaults to Depends(get_db).

    Returns:
    -------
    dict[str, str]: A message confirming the deletion.

    """
    user_obj = await get_authenticated_user(request, db)
    return await delete_document(document_id, db, user_obj)

