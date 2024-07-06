"""Main module for the FastAPI application.

This module sets up the FastAPI application, includes API routers, sets up
database tables on startup, and adds JWT authentication middleware to protect
specific routes.

Attributes
----------
app : FastAPI
    The FastAPI application instance.

"""

from __future__ import annotations

from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.jwt import ALGORITHM, JWT_SECRET_KEY
from app.db.base import Base
from app.db.session import engine
from app.middleware.auth import JWTAuthMiddleware

app = FastAPI()

app.include_router(api_router, prefix="/api/v1")



@app.get("/")
async def root() -> dict[str, str]:
    """Get dict (JSON) for root path."""
    return {"API": "Projects"}


@app.on_event("startup")
async def on_startup() -> None:
    """Perform actions on application startup.

    This function ensures that all database tables defined in SQLAlchemy's
    Base.metadata are created when the application starts up.

    Returns
    -------
    None

    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.add_middleware(
    JWTAuthMiddleware,
    secret_key=JWT_SECRET_KEY,
    algorithm=ALGORITHM,
    protected_routes=[
        "/api/v1/projects/",
        "/api/v1/project/",
        "/api/v1/document/",
    ],
)
