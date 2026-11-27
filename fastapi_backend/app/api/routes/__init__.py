from fastapi import APIRouter

from app.api.routes import global_data, nexus
from app.mesa.api import router as mesa_router


def get_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(global_data.router, prefix="/api")
    router.include_router(nexus.router, prefix="/api")
    router.include_router(mesa_router, prefix="/api")
    return router
