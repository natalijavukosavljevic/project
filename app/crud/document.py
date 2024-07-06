"""CRUD operations for document."""

from __future__ import annotations

from fastapi import HTTPException, Response, UploadFile
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: TCH002
from sqlalchemy.orm import selectinload

from app.core.config import BUCKET_NAME
from app.crud.project import get_documents, is_participant
from app.db.buckets import delete_from_s3, download_from_s3, upload_to_s3
from app.db.session import SessionLocal
from app.models.project import (
    Document,
    Project,
    User,
)
from app.schemas.project import DocumentOut


async def get_document(
    db: AsyncSession,
    document_id: int,
    user_obj: User,
) -> Document:
    """Retrieve document information by document ID.

    Args:
    ----
        db (AsyncSession): The asynchronous database session.
        document_id (int): The ID of the document to retrieve.
        user_obj (User): The authenticated user object.

    Returns:
    -------
        Document: The document object if authorized.

    Raises:
    ------
        HTTPException: If the document is not found or the user
            is not authorized.

    """
    async with db.begin():
        # Retrieve the document by document_id
        document = await db.execute(
            select(Document)
            .where(Document.document_id == document_id)
            .options(selectinload(Document.project)),
        )
        document = document.scalars().first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        project = document.project
        if user_obj.user_id == project.owner_id or await is_participant(
            user_obj.user_id,
            project.project_id,
            db,
        ):
            return document

        raise HTTPException(
            status_code=403,
            detail="User is not authorized for this document's project",
        )


async def update_document(
    document_id: int,
    file: UploadFile,
    db: AsyncSession,
    user_obj: User,
) -> DocumentOut:
    """Update document by document ID with a new file.

    Args:
    ----
        document_id (int): The ID of the document to update.
        file (UploadFile): The new file to upload.
        db (AsyncSession): The asynchronous database session.
        user_obj (User): The authenticated user object.

    Returns:
    -------
        DocumentOut: The updated document details.

    Raises:
    ------
        HTTPException: If the document is not found or there's an issue
            uploading the file to S3.

    """
    document = await get_document(db, document_id, user_obj)

    s3_key = await upload_to_s3(
        file,
        BUCKET_NAME,
        s3_key=document.s3_key,
    )
    if not s3_key:
        raise HTTPException(
            status_code=500,
            detail="Failed to upload to S3",
        )
    document.s3_key = s3_key
    return DocumentOut(
        document_id=document.document_id,
        document_name=document.document_name,
    )


async def delete_document(
    document_id: int,
    db: AsyncSession,
    user_obj: User,
) -> dict[str, str]:
    """Delete document by document ID.

    Args:
    ----
        document_id (int): The ID of the document to delete.
        db (AsyncSession): The asynchronous database session.
        user_obj (User): The authenticated user object.

    Returns:
    -------
        dict[str, str]: A success message upon successful deletion.

    Raises:
    ------
        HTTPException: If the document is not found or there's an issue
            deleting from S3.

    """
    document = await get_document(db, document_id, user_obj)
    success = await delete_from_s3(BUCKET_NAME, document.s3_key)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete from S3",
        )
    async with db.begin():
        await db.delete(document)
    return {"message": "Document deleted successfully"}


async def download_document(
    document_id: int,
    user_obj: User,
    db: AsyncSession,
) -> Response:
    """Download document content by document ID.

    Args:
    ----
        document_id (int): The ID of the document to download.
        user_obj (User): The authenticated user object.
        db (AsyncSession): The asynchronous database session.

    Returns:
    -------
        Response: A response object containing the document content.

    Raises:
        HTTPException: If the document is not found or there's an issue
            downloading from S3.

    """  # noqa: D407
    document = await get_document(db, document_id, user_obj)

    # Download document content from S3
    document_content = await download_from_s3(
        BUCKET_NAME,
        document.s3_key,
    )
    if document_content is None:
        raise HTTPException(
            status_code=500,
            detail="Failed to download document from S3",
        )

    return Response(
        content=document_content,
        headers={
            "Content-Disposition": (
                f"attachment;filename={document.document_name}"
            ),
            "Content-Type": "application/octet-stream",
        },
    )


async def delete_documents_from_s3(target: Project) -> None:
    """Event listener to delete documents associated with a Project from S3
    after deletion of the Project.

    Args:
    ----
        mapper: SQLAlchemy mapper.
        connection: SQLAlchemy connection object.
        target: The instance of Project being deleted.

    Returns:
    -------
        None

    Raises:
    ------
        Any exceptions raised by get_documents or delete_from_s3 functions.

    """  # noqa: D205
    async with SessionLocal() as session:
        documents = await get_documents(
            db=session, project_id=target.project_id,
        )
        for document in documents:
            await delete_from_s3(BUCKET_NAME, document.s3_key)


event.listen(Project, "after_delete", delete_documents_from_s3)
