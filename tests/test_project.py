"""Module contains tests for project-related endpoints.
These tests cover functionalities such as uploading, downloading,
and deleting project documents and logos,
as well as creating, reading, updating, and deleting projects and
inviting users to projects.
"""  # noqa: D205

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import UploadFile
from httpx import AsyncClient

BASE_URL = "/api/v1/project"


@pytest.mark.asyncio()
async def test_delete_project(
    async_client: AsyncClient, create_objects,  # noqa: ANN001
) -> None:
    """Test the deletion of a project.

    Args:
    ----
        async_client (AsyncClient): The HTTP client for making API requests.
        create_objects (tuple): Fixture that provides user, project, image,
        password, access token, and document.

    """
    user, project, image, password, access_token, document = create_objects

    delete_response = await async_client.delete(
        f"{BASE_URL}/{project.project_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert delete_response.status_code == 200  # noqa: S101, PLR2004
    assert delete_response.json() == {  # noqa: S101
        "message": "Project deleted successfully",
    }


@pytest.mark.asyncio()
async def test_read_project(async_client: AsyncClient, create_objects) -> None:  # noqa: ANN001
    """Test reading project details.

    Args:
    ----
        async_client (AsyncClient): The HTTP client for making API requests.
        create_objects (tuple): Fixture that provides user, project, image,
        password, access token, and document.

    """
    user, project, image, password, access_token, document = create_objects

    response = await async_client.get(
        f"{BASE_URL}/{project.project_id}/info",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200  # noqa: S101, PLR2004
    assert "name" in response.json()  # noqa: S101
    assert response.json()["name"] == "Test Project"  # noqa: S101


@pytest.mark.asyncio()
async def test_update_existing_project(
    async_client: AsyncClient,
    create_objects,  # noqa: ANN001
) -> None:
    """Test updating an existing project.

    Args:
    ----
        async_client (AsyncClient): The HTTP client for making API requests.
        create_objects (tuple): Fixture that provides user, project, image,
        password, access token, and document.

    """
    user, project, image, password, access_token, document = create_objects

    updated_project_data = {
        "name": "Updated Project",
        "description": "Updated Project Description",
    }

    response = await async_client.put(
        f"{BASE_URL}/{project.project_id}/info",
        json=updated_project_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200  # noqa: S101, PLR2004
    assert response.json()["name"] == "Updated Project"  # noqa: S101


@pytest.mark.asyncio()
async def test_invite_user_to_project(
    async_client: AsyncClient,
    create_objects,  # noqa: ANN001
    create_user_fixture,  # noqa: ANN001
) -> None:
    """Test inviting a user to a project.

    Args:
    ----
        async_client (AsyncClient): The HTTP client for making API requests.
        create_objects (tuple): Fixture that provides user, project, image,
        password, access token, and document.
        create_user_fixture (tuple): Fixture that provides a user and password.

    """
    user, project, image, password, access_token, document = create_objects
    user, _ = create_user_fixture

    invite_response = await async_client.post(
        f"{BASE_URL}/{project.project_id}/invite",
        params={"user_email": user.email},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert invite_response.status_code == 200  # noqa: S101, PLR2004
    assert invite_response.json() == {  # noqa: S101
        "message": "Participant added to project successfully",
    }


@pytest.mark.asyncio()
async def test_upload_project_documents(
    async_client: AsyncClient,
    create_objects,  # noqa: ANN001
) -> None:
    """Test uploading documents to a project.

    Args:
    ----
        async_client (AsyncClient): The HTTP client for making API requests.
        create_objects (tuple): Fixture that provides user, project, image,
        password, access token, and document.

    """
    user, project, image, password, access_token, document = create_objects

    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test_document.txt"
    mock_file.read = AsyncMock(return_value=b"file_content")
    mock_file.content_type = "text/plain"

    with patch(
        "app.crud.project.upload_to_s3",
        new=AsyncMock(return_value="mock_s3_key"),
    ):
        upload_response = await async_client.post(
            f"{BASE_URL}/{project.project_id}/documents",
            files={
                "files": (
                    mock_file.filename,
                    await mock_file.read(),
                    mock_file.content_type,
                ),
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

    assert upload_response.status_code == 200  # noqa: S101, PLR2004
    assert isinstance(upload_response.json(), list)  # noqa: S101
    assert upload_response.json()[0]["document_name"] == "test_document.txt"  # noqa: S101


@pytest.mark.asyncio()
async def test_get_project_documents(
    async_client: AsyncClient,
    create_objects,  # noqa: ANN001
) -> None:
    """Test retrieving documents for a project.

    Args:
    ----
        async_client (AsyncClient): The HTTP client for making API requests.
        create_objects (tuple): Fixture that provides user, project, image,
        password, access token, and document.

    """
    user, project, image, password, access_token, document = create_objects

    headers = {"Authorization": f"Bearer {access_token}"}
    response = await async_client.get(
        f"{BASE_URL}/{project.project_id}/documents",
        headers=headers,
    )

    assert response.status_code == 200  # noqa: S101, PLR2004
    documents = response.json()
    assert isinstance(documents, list)  # noqa: S101


@pytest.mark.asyncio()
async def test_get_project_logo(
    async_client: AsyncClient,
    create_objects,  # noqa: ANN001
) -> None:
    """Test retrieving the logo for a project.

    Args:
    ----
        async_client (AsyncClient): The HTTP client for making API requests.
        create_objects (tuple): Fixture that provides user, project, image,
        password, access token, and document.

    """
    user, project, image, password, access_token, document = create_objects

    with patch(
        "app.crud.project.download_from_s3",
        new=AsyncMock(return_value=b"logo_content"),
    ):
        get_logo_response = await async_client.get(
            f"{BASE_URL}/{project.project_id}/logo",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    assert get_logo_response.status_code == 200  # noqa: S101, PLR2004
    assert get_logo_response.content == b"logo_content"  # noqa: S101


@pytest.mark.asyncio()
async def test_upload_project_logo(
    async_client: AsyncClient,
    create_objects,  # noqa: ANN001
) -> None:
    """Test uploading a logo to a project.

    Args:
    ----
        async_client (AsyncClient): The HTTP client for making API requests.
        create_objects (tuple): Fixture that provides user, project, image,
        password, access token, and document.

    """
    user, project, image, password, access_token, document = create_objects

    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "logo_image.png"
    mock_file.read = AsyncMock(return_value=b"image_content")
    mock_file.content_type = "image/png"

    with patch(
        "app.crud.project.upload_to_s3",
        new=AsyncMock(return_value="mock_s3_key_6"),
    ):
        upload_response = await async_client.put(
            f"{BASE_URL}/{project.project_id}/logo",
            files={
                "file": (
                    mock_file.filename,
                    await mock_file.read(),
                    mock_file.content_type,
                ),
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

    assert upload_response.status_code == 200  # noqa: S101, PLR2004
    assert upload_response.json()["image_name"] == "logo_image.png"  # noqa: S101


@pytest.mark.asyncio()
async def test_delete_project_logo(
    async_client: AsyncClient, create_objects,  # noqa: ANN001
) -> None:
    """Test deleting a project's logo.

    Args:
    ----
        async_client (AsyncClient): The HTTP client for making API requests.
        create_objects (tuple): Fixture that provides user, project, image,
          password, access token, and document.

    """
    user, project, image, password, access_token, document = create_objects

    with patch(
        "app.crud.project.delete_from_s3", new=AsyncMock(return_value=True),
    ):
        delete_response = await async_client.delete(
            f"{BASE_URL}/{project.project_id}/logo",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    assert delete_response.status_code == 200  # noqa: S101, PLR2004
    assert delete_response.json()["message"] == "Logo deleted successfully"  # noqa: S101
