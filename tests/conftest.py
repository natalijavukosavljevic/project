"""Module contains shared fixtures for testing FastAPI applications with
SQLAlchemy and async capabilities.
The fixtures provide setup and teardown logic for the test database,
test application, and various test objects.
"""  # noqa: D205
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.security import get_hashed_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.project import Document, Image, Project, User


@pytest_asyncio.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Start a test database session."""
    #db_url = "postgresql+asyncpg://postgres:password@localhost:5433/test_db"
    db_url = "postgresql+asyncpg://postgres:16041346.D@localhost/test_db"
    engine = create_async_engine(db_url, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session = async_sessionmaker(engine, expire_on_commit=False)()
    yield session
    await session.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
def test_app(db_session: AsyncSession) -> FastAPI:
    """Create a test app with overridden dependencies."""
    app.dependency_overrides[get_db] = lambda: db_session
    return app


@pytest_asyncio.fixture()
async def async_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create an http client."""
    async with AsyncClient(
        app=test_app, base_url="http://localhost",
    ) as client:
        yield client


@pytest_asyncio.fixture()
async def create_user_fixture(db_session: AsyncSession) -> tuple:
    """Create a test user."""
    user, password = await create_user(
        db_session, email="test@example.com", password="password", # noqa: S106
    )
    return user, password


@pytest_asyncio.fixture()
async def create_objects(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> tuple:
    """Create necessary objects."""
    user, password = await create_user(
        db_session, email="test1@example.com", password="password", # noqa: S106
    )
    access_token = await get_access_token(async_client, user.email, password)
    image = await create_image(db_session)
    project = await create_project(
        db_session, user.user_id, logo_id=image.image_id,
    )
    document = await create_document(db_session, project.project_id)
    return user, project, image, password, access_token, document


async def create_user(db_session: AsyncSession, email: str, password: str,
                      ) -> None:
    """Create a test user."""
    async_session_maker = async_sessionmaker(
        db_session.bind, expire_on_commit=False,
    )
    session = async_session_maker()

    try:
        user = User(email=email, hashed_password=get_hashed_password(password))
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user, password
    finally:
        await session.close()


async def create_project(
    db_session: AsyncSession, user_id: int, logo_id: int = None,  # noqa: RUF013
) -> None:
    """Create a test project associated with a user."""
    async_session_maker = async_sessionmaker(
        db_session.bind, expire_on_commit=False,
    )
    session = async_session_maker()

    try:
        project = Project(
            name="Test Project",
            description="A test project",
            owner_id=user_id,
            logo_id=logo_id,
        )
        session.add(project)
        await session.commit()
        await session.refresh(project)
        return project
    finally:
        await session.close()


async def get_access_token(
    async_client: AsyncClient, username: str, password: str,
) -> str:
    """Retrieve access token by logging in with username and password."""
    login_data = {"username": username, "password": password}
    response = await async_client.post("/api/v1/login", data=login_data)
    assert response.status_code == 200  # noqa: S101, PLR2004
    return response.json()["access_token"]


async def create_document(db_session: AsyncSession, project_id: int) -> None:
    """Create a test document associated with a project."""
    async_session_maker = async_sessionmaker(
        db_session.bind, expire_on_commit=False,
    )
    session = async_session_maker()

    try:
        document = Document(
            document_name="Test Document",
            s3_key="test_s3_key",
            project_id=project_id,
        )
        session.add(document)
        await session.commit()
        await session.refresh(document)
        return document
    finally:
        await session.close()


async def create_image(db_session: AsyncSession) -> Image:
    """Create a test image associated with a project."""
    async_session_maker = async_sessionmaker(
        db_session.bind, expire_on_commit=False,
    )
    session = async_session_maker()

    try:
        image = Image(
            image_name="Test Image",
            s3_key="test_image_s3_key",
        )
        session.add(image)
        await session.commit()
        await session.refresh(image)
        return image
    finally:
        await session.close()
