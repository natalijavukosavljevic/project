"""Database session management."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import DATABASE_URL

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_timeout=30,
    pool_recycle=3600,
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get AsyncSession instance.

    This function creates an AsyncSession instance and yields it for code
    database operations.
    It also ensures that the session is closed properly after its usage.

    Yields
    ------
        AsyncSession: An AsyncSession instance for performing database
        operations.

    """
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
