from fastapi import APIRouter

from app.api.routes import global_data


def get_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(global_data.router, prefix="/api")
    return router
