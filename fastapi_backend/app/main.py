from contextlib import asynccontextmanager
import logging
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.api.routes import get_api_router
from app.core.config import settings
from app.db.session import engine

from app.api.chat import router as chat_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        await engine.dispose()


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
        version="1.0.0",
    )

    @app.get("/")
    async def root():
        return {
            "success": True,
            "message": "EduPlan API is running",
            "data": {"name": settings.app_name, "version": "1.0.0"},
        }

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        request_id = uuid.uuid4().hex
        logger.exception("Unhandled error request_id=%s path=%s", request_id, request.url.path)
        payload = {
            "success": False,
            "message": "Internal server error",
            "request_id": request_id,
        }
        if settings.debug:
            payload["detail"] = str(exc)
        return JSONResponse(status_code=500, content=payload)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.cors_origins] or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(get_api_router())
    app.include_router(chat_router, prefix="/api", tags=["Chat Assistant"])
    return app


app = create_application()
