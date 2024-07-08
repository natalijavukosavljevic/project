"""module contains tests for project-related endpoints.
These tests cover functionalities such as adding and retrieving projects.
"""  # noqa: D205

import pytest
from httpx import AsyncClient

BASE_URL = "/api/v1/projects/"


@pytest.mark.asyncio()
async def test_add_project(async_client: AsyncClient, create_objects) -> None:  # noqa: ANN001
    """Test adding a new project.

    Args:
    ----
        async_client (AsyncClient): The HTTP client for making API requests.
        create_objects (tuple): Fixture that provides user, project, image,
        password, access token, and document.

    """
    user, project, image, password, access_token, document = create_objects

    project_data = {
        "name": "Test Project",
        "description": "Test Project Description",
    }
    headers = {}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    response = await async_client.post(
        BASE_URL,
        json=project_data,
        headers=headers,
    )

    assert response.status_code == 200  # noqa: S101, PLR2004
    assert response.json()["name"] == "Test Project"  # noqa: S101


@pytest.mark.asyncio()
async def test_get_projects(async_client: AsyncClient, create_objects) -> None:  # noqa: ANN001
    """Test retrieving a list of projects.

    Args:
    ----
        async_client (AsyncClient): The HTTP client for making API requests.
        create_objects (tuple): Fixture that provides user, project, image,
        password, access token, and document.

    """
    user, project, image, password, access_token, document = create_objects

    response = await async_client.get(
        BASE_URL,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200  # noqa: S101, PLR2004
    assert isinstance(response.json(), list)  # noqa: S101
