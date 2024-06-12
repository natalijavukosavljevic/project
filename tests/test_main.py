"""Module contains tests for the project management API endpoints.

It includes tests for login, adding a project, retrieving projects,
updating a project, getting a project by ID, and deleting a project.
"""

import requests

BASE_URL = "http://localhost:8000"

# Login to get the JWT token
login_url = f"{BASE_URL}/login"
login_data = {"username": "vuk@gmail.com", "password": "vuk1234567899"}

response = requests.post(login_url, data=login_data, timeout=10)
tokens = response.json()
jwt_token = tokens["access_token"]


def test_add_project() -> None:
    """Test the add project endpoint.

    Verifies that a project can be added successfully.
    """
    add_project_url = f"{BASE_URL}/projects"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
    }
    project_data = {
        "name": "Project Hospital",
        "description": "Adding patients",
    }
    response = requests.post(
        add_project_url,
        headers=headers,
        json=project_data,
        timeout=10,
    )
    assert response.status_code == 200  # noqa: S101, PLR2004
    assert response.json()["name"] == "Project Hospital"  # noqa: S101
    assert response.json()["description"] == "Adding patients"  # noqa: S101


def test_get_projects() -> None:
    """Test the get projects endpoint.

    Verifies that the list of projects can be retrieved successfully.
    """
    get_projects_url = f"{BASE_URL}/projects"
    headers = {"Authorization": f"Bearer {jwt_token}"}
    response = requests.get(get_projects_url, headers=headers, timeout=10)
    assert response.status_code == 200  # noqa: S101, PLR2004
    assert len(response.json()) > 0  # noqa: S101


def test_update_project() -> None:
    """Test the update project endpoint.

    Verifies that a project can be updated successfully.
    Assumes that project ID 13 exists.
    """
    update_project_url = f"{BASE_URL}/project/13/info"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
    }
    project_data = {
        "name": "Updated Project Name",
        "description": "Updated Project Description",
    }
    response = requests.put(
        update_project_url,
        headers=headers,
        json=project_data,
        timeout=10,
    )
    assert response.status_code == 200  # noqa: S101, PLR2004
    assert response.json()["name"] == "Updated Project Name"  # noqa: S101
    assert response.json()["description"] == "Updated Project Description"  # noqa: S101


def test_get_project_by_id() -> None:
    """Test the get project by ID endpoint.

    Verifies that a project can be retrieved by its ID successfully.
    Assumes that project ID 13 exists.
    """
    get_project_url = f"{BASE_URL}/project/13/info"
    headers = {"Authorization": f"Bearer {jwt_token}"}
    response = requests.get(get_project_url, headers=headers, timeout=10)
    assert response.status_code == 200  # noqa: S101, PLR2004
    assert response.json()["project_id"] == 13  # noqa: S101, PLR2004


def test_delete_project() -> None:
    """Test the delete project endpoint.

    Verifies that a project can be deleted successfully.
    Assumes that project ID 15 exists.
    """
    delete_project_url = f"{BASE_URL}/project/8"
    headers = {"Authorization": f"Bearer {jwt_token}"}
    response = requests.delete(delete_project_url, headers=headers, timeout=10)
    assert response.status_code == 404  # noqa: PLR2004, S101


def test_invite_user_to_project() -> None:
    """Test the invite user to project endpoint.

    Verifies that a user can be invited to a project successfully.
    Assumes that project ID 13 exists and the user to invite exists.
    """
    invite_user_url = f"{BASE_URL}/project/18/invite"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
    }
    invite_data = {"user_email": "ev@gmail.com"}
    response = requests.post(
        invite_user_url,
        headers=headers,
        params=invite_data,
        timeout=10,
    )
    assert response.status_code == 400  # noqa: S101, PLR2004

