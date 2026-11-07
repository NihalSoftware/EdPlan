from fastapi import APIRouter

from app.api.routes import global_data
from app.admin.api import router as analytics_router


def get_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(global_data.router, prefix="/api")
    router.include_router(analytics_router, prefix="/api")
    return router
