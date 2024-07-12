"""Module contains tests for project document-related endpoints.
These tests cover the functionality of uploading, downloading,
and deleting project documents.
"""  # noqa: D205

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import UploadFile
from httpx import AsyncClient

BASE_URL = "/api/v1/document"


@pytest.mark.asyncio()
async def test_upload_project_document(
    async_client: AsyncClient,
    create_objects,  # noqa: ANN001
) -> int:
    """Test the upload of a document to a project.

    Args:
    ----
        async_client (AsyncClient): The HTTP client for making API requests.
        create_objects (tuple): Fixture that provides user, project, image,
        password, access token, and document.

    Returns:
    -------
        int: The ID of the uploaded document.

    """
    user, project, image, password, access_token, document = create_objects
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "document.pdf"
    mock_file.read = AsyncMock(return_value=b"document_content")
    mock_file.content_type = "application/pdf"

    with patch(
        "app.crud.document.upload_to_s3",
        new=AsyncMock(return_value="mock_s3_key"),
    ):
        response = await async_client.put(
            f"{BASE_URL}/{document.document_id}",
            files={
                "file": (
                    mock_file.filename,
                    await mock_file.read(),
                    mock_file.content_type,
                ),
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200  # noqa: S101, PLR2004
        return response.json()["document_id"]


@pytest.mark.asyncio()
async def test_download_project_document(
    async_client: AsyncClient, create_objects,  # noqa: ANN001
) -> None:
    """Test the download of a document from a project.

    Args:
    ----
        async_client (AsyncClient): The HTTP client for making API requests.
        create_objects (tuple): Fixture that provides user, project, image,
        password, access token, and document.

    """
    user, project, image, password, access_token, document = create_objects

    with patch(
        "app.crud.document.download_from_s3",
        new=AsyncMock(return_value=b"document_content"),
    ):
        response = await async_client.get(
            f"{BASE_URL}/{document.document_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    assert response.status_code == 200  # noqa: S101, PLR2004
    assert response.content == b"document_content"  # noqa: S101


@pytest.mark.asyncio()
async def test_delete_project_document(
    async_client: AsyncClient, create_objects,  # noqa: ANN001
) -> None:
    """Test the deletion of a document from a project.

    Args:
    ----
        async_client (AsyncClient): The HTTP client for making API requests.
        create_objects (tuple): Fixture that provides user, project, image,
        password, access token, and document.

    """
    user, project, image, password, access_token, document = create_objects

    with patch(
        "app.crud.document.delete_from_s3", new=AsyncMock(return_value=True),
    ):
        response = await async_client.delete(
            f"{BASE_URL}/{document.document_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    assert response.status_code == 200  # noqa: S101, PLR2004
    assert response.json() == {"message": "Document deleted successfully"}  # noqa: S101
