"""FastAPI Application.

This module defines FastAPI application for managing projects and users.

It includes:
- Routes for adding, updating, and deleting projects
- Authentication and authorization routes
- Routes for inviting users to projects
"""

from __future__ import annotations

from typing import Any, List

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.security import OAuth2PasswordRequestForm  # noqa: TCH002
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import selectinload

from main.models import Base, Project, User, participant_project
from main.schemas import (
    ProjectBase,
    ProjectOut,
    ProjectOutWithDocuments,
    TokenSchema,
    UserAuth,
    UserOut,
)
from main.utilis import (
    ALGORITHM,
    JWT_SECRET_KEY,
    JWTAuthMiddleware,
    create_access_token,
    create_refresh_token,
    get_hashed_password,
    verify_password,
)

# SQLALCHEMY
DATABASE_URL = (
    "postgresql+asyncpg://postgres:16041346.D@localhost:5432/db_projects"
)


engine = create_async_engine(DATABASE_URL)  # echo=True
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():  # noqa: ANN201
    """Get AsyncSession instance.

    This function creates an AsyncSession instance and yields it for
    database operations.
    It also ensures that the session is closed properly after its usage.

    Yields
    ------
        AsyncSession: An AsyncSession instance for performing database
        operations.

    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()


# FASTAPI
app = FastAPI()
PROTECTED_ROUTES = [
    "/projects",
    "/project/",
]
app.add_middleware(
    JWTAuthMiddleware,
    secret_key=JWT_SECRET_KEY,
    algorithm=ALGORITHM,
    protected_routes=PROTECTED_ROUTES,
)


@app.get("/")
async def root() -> dict[str, str]:
    """Get dict (JSON) for root path."""
    return {"message": "Hello World"}


async def get_authenticated_user(request: Request, db: AsyncSession) -> User:
    """Get the authenticated user.

    This function retrieves the authenticated user based on the request and
    database session.

    Args:
    ----
        request (Request): The incoming request.
        db (AsyncSession): The asynchronous database session.

    Returns:
    -------
        User: The authenticated user object.

    Raises:
    ------
        HTTPException: If the user is not authenticated or not found.

    """
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    user_email = user.get("sub")
    async with db as session:
        user_db = await session.execute(
            select(User).where(User.email == user_email),
        )
        user_obj = user_db.scalars().first()

        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        return user_obj


@app.post("/projects", response_model=ProjectBase)
async def add_project(
    project: ProjectBase, request: Request, db: AsyncSession = Depends(get_db),  # noqa: B008
) -> Project:
    """Add a new project.

    This endpoint allows adding a new project to the database.

    Args:
    ----
        project (ProjectBase): The project data to be added.
        request (Request): The incoming request.
        db (AsyncSession, optional): The asynchronous database session.
        Defaults to Depends(get_db).

    Returns:
    -------
        ProjectBase: The project data that has been added.

    """
    user_obj = await get_authenticated_user(request, db)
    async with db.begin():

        # Create the project with the owner_id from the user_id
        db_project = Project(
            name=project.name,
            description=project.description,
            owner_id=user_obj.user_id,
        )

        # Add the project to the session
        # Add the project to the session
        db.add(db_project)
        await db.commit()




    return db_project


@app.get("/projects", response_model=List[ProjectOutWithDocuments])
async def get_projects(
    request: Request,
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> list[ProjectOutWithDocuments]:
    """Retrieve projects associated with the authenticated user.

    This function retrieves projects where the authenticated user is either
    the owner or a participant.

    Args:
    ----
        request (Request): The incoming request.
        db (AsyncSession, optional): The asynchronous database session.
            Defaults to Depends(get_db).

    Returns:
    -------
        List[ProjectOutWithDocuments]: A list of project objects
        associated with the authenticated user.

    Raises:
    ------
        HTTPException: If the user is not authenticated.

    """
    user_obj = await get_authenticated_user(request, db)

    async with db.begin():
        # Select projects where the user is the owner
        owner_projects_query = (
            select(Project)
            .options(selectinload(Project.documents))
            .where(Project.owner_id == user_obj.user_id)
        )
        owner_results = await db.execute(owner_projects_query)
        owner_projects = owner_results.scalars().all()

        # Select projects where the user is a participant
        participant_projects_query = (
            select(Project)
            .join(
                participant_project,
                Project.project_id == participant_project.c.project_id,
            )
            .where(participant_project.c.user_id == user_obj.user_id)
            .options(selectinload(Project.documents))
        )
        participant_results = await db.execute(participant_projects_query)
        participant_projects = participant_results.scalars().all()

        # Combine and remove duplicates if any
        user_projects = {project.project_id: project for project in
                         owner_projects +
                         participant_projects}

    return list(user_projects.values())




@app.delete("/project/{project_id}")
async def delete_project(
    project_id: int, request: Request, db: AsyncSession = Depends(get_db),  # noqa: B008
) -> dict[str, str]:
    """Delete a project.

    Deletes the project with the specified project_id if the authenticated
    user is the owner of the project.

    Args:
    ----
        project_id (int): The ID of the project to delete.
        request (Request): The incoming request.
        db (AsyncSession, optional): The asynchronous database session.
        Defaults to Depends(get_db).

    Returns:
    -------
        dict[str, str]: A dictionary with a message indicating the
        deletion status.

    Raises:
    ------
        HTTPException: If the project is not found or the user
        is not authorized.

    """
    user_obj = await get_authenticated_user(request, db)
    async with db.begin():
        db_project = await db.get(Project, project_id)
        if db_project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        if user_obj.user_id == db_project.owner_id:
            await db.delete(db_project)  # Await the deletion operation
            await db.commit()
            return {"message": "Project deleted successfully"}

        raise HTTPException(
            status_code=403, detail="User is not authorized for this project",
        )


async def is_participant(user_id: int, project_id: int,
                         session: AsyncSession) -> bool:
    """Check if a user is a participant in a project.

    Args:
    ----
        user_id (int): The ID of the user to check.
        project_id (int): The ID of the project to check.
        session (AsyncSession): The asynchronous database session.

    Returns:
    -------
        bool: True if the user is a participant in the project,
        False otherwise.

    """
    participant_query = select(participant_project).where(
        participant_project.c.user_id == user_id,
        participant_project.c.project_id == project_id,
    )
    result = await session.execute(participant_query)
    return result.scalar_one_or_none() is not None


@app.put("/project/{project_id}/info", response_model=ProjectBase)
async def update_project(
    project_id: int,
    project_data: ProjectBase,
    request: Request,
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> Project:
    """Update project information.

    Args:
    ----
        project_id (int): The ID of the project to update.
        project_data (ProjectBase): The updated project data.
        request (Request): The request object.
        db (AsyncSession, optional): The asynchronous database session.
            Defaults to Depends(get_db).

    Returns:
    -------
        Project: The updated project object.

    Raises:
    ------
        HTTPException: If the project is not found or the user
        is not authorized.

    """
    user_obj = await get_authenticated_user(request, db)

    # Use db.begin() for transaction handling
    async with db.begin():
        db_project = await db.get(Project, project_id)
        if db_project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        if user_obj.user_id == db_project.owner_id or await is_participant(
            user_obj.user_id, project_id, db,
        ):
            for key, value in project_data.model_dump().items():
                setattr(db_project, key, value)

            await db.commit()  # Commit within the transaction context

            return db_project

        # If user is neither owner nor participant
        raise HTTPException(
            status_code=403, detail="User is not authorized for this project",
        )


@app.get("/project/{project_id}/info", response_model=ProjectOut)
async def get_project(
    project_id: int, request: Request, db: AsyncSession = Depends(get_db),  # noqa: B008
) -> Project:
    """Retrieve project information by project ID.

    Args:
    ----
        project_id (int): The ID of the project to retrieve.
        request (Request): The request object.
        db (AsyncSession, optional): The asynchronous database session.
            Defaults to Depends(get_db).

    Returns:
    -------
        Project: The project object if the user is authorized.

    Raises:
    ------
        HTTPException: If the project is not found or the user
        is not authorized.

    """
    user_obj = await get_authenticated_user(request, db)
    async with db.begin():
        db_project = await db.get(Project, project_id)
        if db_project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        if user_obj.user_id == db_project.owner_id or await is_participant(
            user_obj.user_id, project_id, db,
        ):
            return db_project

        raise HTTPException(
            status_code=403, detail="User is not authorized for this project",
        )



@app.post("/auth", summary="Create new user", response_model=UserOut)
async def create_user(user_data: UserAuth, db: AsyncSession = Depends(get_db),  # noqa: B008
) -> dict[str, Any]:
    """Create a new user.

    Args:
    ----
        user_data (UserAuth): User authentication data including
        email and password.
        db (AsyncSession, optional): The asynchronous database session.
            Defaults to Depends(get_db).

    Returns:
    -------
        dict[str, Any]: A dictionary containing the newly created
        user's ID and email.

    Raises:
    ------
        HTTPException: If a user with the same email already exists.

    """
    # Check if user already exists
    existing_user = await db.execute(
        select(User).where(User.email == user_data.email),
    )
    existing_user = existing_user.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=400, detail="User with this email already exists",
        )

    # Create new user
    hashed_password = get_hashed_password(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
    )
    db.add(new_user)
    await db.commit()

    # Return the newly created user
    return {
        "user_id": new_user.user_id,
        "email": new_user.email,
    }


@app.post(
    "/login",
    summary="Create access and refresh tokens for user",
    response_model=TokenSchema,
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> dict[str, str]:
    """Log in user and generate access and refresh tokens.

    Args:
    ----
        form_data (OAuth2PasswordRequestForm, optional): Form data
        containing the username (email) and password. Defaults to Depends().
        db (AsyncSession, optional): The asynchronous database session.
            Defaults to Depends(get_db).

    Returns:
    -------
        dict[str, str]: A dictionary containing the access_token and
        refresh_token.

    Raises:
    ------
        HTTPException: If the provided email or password is incorrect.

    """
    # Query the user from the database
    result = await db.execute(
        select(User).where(User.email == form_data.username),
    )
    user = result.scalars().first()

    # Check if user exists and password is correct
    if user is None or not verify_password(
        form_data.password, user.hashed_password,
    ):
        raise HTTPException(
            status_code=400, detail="Incorrect email or password",
        )

    # Create tokens
    access_token = create_access_token(user.email)
    refresh_token = create_refresh_token(user.email)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }





@app.post(
    "/project/{project_id}/invite",
    summary="Grant access to the project for a specific user",
)
async def invite_user_to_project(
    project_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    user_email: str = Query(
        ..., description="Email of the user to invite",
    ),  # Moved user_email before request
) -> dict[str, str]:
    # Get user information from JWT token
    """Invite a user to participate in a project.

    Args:
    ----
        project_id (int): The ID of the project to which the
        user will be invited.
        request (Request): The request object containing
        the current user's information.
        db (AsyncSession, optional): The asynchronous database session.
            Defaults to Depends(get_db).
        user_email (str): The email of the user to invite.

    Returns:
    -------
        dict[str, str]: A dictionary containing a success message.

    Raises:
    ------
        HTTPException: If the current user is not authenticated.
        HTTPException: If the project is not found.
        HTTPException: If the current user is not the owner of the project.
        HTTPException: If the invited user does not exist.

    """
    current_user = request.state.user
    if not current_user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    # Retrieve the user_id of the current user based on email
    current_user_email = current_user.get("sub")

    async with db as session:
        # Select project by project_id
        result = await session.execute(
            select(Project).filter(Project.project_id == project_id),
        )
        project = result.scalar()
        temp = await session.execute(
            select(User).filter(User.user_id == project.owner_id),
        )
        owner = temp.scalar()

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Check if the current user is the owner of the project
        if owner.email != current_user_email:
            raise HTTPException(
                status_code=403,
                detail="Only the project owner can invite users",
            )
        # Retrieve the user to be invited by email
        invited_user_obj = await session.execute(
            select(User).filter(User.email == user_email),
        )
        if not invited_user_obj:  # proveri
            raise HTTPException(
                status_code=401, detail="Invited user doesn't exist",
            )

          # Check if the user is already participating in the project
        if await is_participant(invited_user_obj.scalar().user_id,
                                project_id, session):
            raise HTTPException(
                status_code=400,
                detail="User is already participating in the project",
            )

        await session.execute(
            insert(participant_project).values(
                project_id=project_id,
                user_id=invited_user_obj.scalar().user_id,
            ),
        )
        await session.commit()

        return {"message": "Participant added to project successfully"}
