from fastapi import APIRouter

from app.api.routes import global_data, nexus


def get_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(global_data.router, prefix="/api")
    router.include_router(nexus.router, prefix="/api")
    return router
