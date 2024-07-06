"""API router for version 1."""

from fastapi import APIRouter

from app.api.v1.endpoints import document, project, projects, user

api_router = APIRouter()
api_router.include_router(user.router, tags=["users"])
api_router.include_router(
    project.router,
    prefix="/project",
    tags=["project"],
)
api_router.include_router(
    projects.router,
    prefix="/projects",
    tags=["projects"],
)
api_router.include_router(
    document.router,
    prefix="/document",
    tags=["document"],
)
