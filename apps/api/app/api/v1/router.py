from fastapi import APIRouter

from app.api.v1.routes import (
    datasets,
    organizations,
    projects,
    system,
)

api_router = APIRouter()

api_router.include_router(system.router)
api_router.include_router(organizations.router)
api_router.include_router(projects.router)
api_router.include_router(datasets.router)
