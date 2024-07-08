"""These tests cover user authentication functionalities including
user creation and login.
"""  # noqa: D205

import pytest
from httpx import AsyncClient

from tests.conftest import get_access_token

BASE_URL = "/api/v1"

@pytest.mark.asyncio()
async def test_create_user(async_client: AsyncClient) -> None:
    """Test creating a new user via API.

    Args:
    ----
        async_client (AsyncClient): The HTTP client for making API requests.

    """
    user_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "repeat_password": "testpassword",
    }
    response = await async_client.post(f"{BASE_URL}/auth", json=user_data)
    assert response.status_code == 200  # noqa: S101, PLR2004
    assert response.json()["email"] == "test@example.com"  # noqa: S101

@pytest.mark.asyncio()
async def test_login_user(async_client: AsyncClient, create_user_fixture):  # noqa: ANN201, ANN001
    """Test logging in a user and retrieving an access token.

    Args:
    ----
        async_client (AsyncClient): The HTTP client for making API requests.
        create_user_fixture: Fixture that provides a newly 
        created user and password.

    Returns:
    -------
        str: The access token retrieved after successful login.

    """  # noqa: W291
    user, password = create_user_fixture
    access_token = await get_access_token(async_client, user.email, password)
    assert access_token is not None  # noqa: S101
    return access_token

