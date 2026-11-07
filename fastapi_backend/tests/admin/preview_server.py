"""Isolated browser QA server. Never connects to or seeds the configured database.

Run from fastapi_backend: python tests/admin/preview_server.py
Then run Vite on port 5180 with VITE_API_BASE_URL=http://localhost:8011/api.
Disposable synthetic account: preview-admin@example.com / Local-preview-only-2026
"""
import asyncio
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_analytics import database

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.admin.api import router
from app.admin import api as analytics_api
from app.db.session import get_db
from app.security.auth import hash_password
from app.student.domains.auth.api.auth import router as auth_router


def create_preview():
    folder = tempfile.TemporaryDirectory(prefix="edplan-analytics-qa-")
    fixture = database.__wrapped__(Path(folder.name))
    sessions = next(fixture)
    async def prepare():
        async with sessions() as db:
            await db.execute(text("UPDATE users SET password_hash=:password, email='preview-admin@example.com' WHERE id=11"),
                             {"password": hash_password("Local-preview-only-2026")})
            await db.commit()
    asyncio.run(prepare())
    app = FastAPI(title="EdPlan isolated synthetic-data QA server")
    app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5180"],
                       allow_headers=["*"], allow_methods=["*"])
    app.include_router(router, prefix="/api")
    app.include_router(auth_router, prefix="/api")
    async def session():
        async with sessions() as db:
            yield db
    app.dependency_overrides[get_db] = session
    original_report = analytics_api.build_dashboard
    async def synthetic_report(*args, **kwargs):
        report = await original_report(*args, **kwargs)
        report.population = "ISOLATED TEST DATA — synthetic QA cohort"
        report.coverage = "Synthetic test records only; this is not a live report. " + report.coverage
        return report
    analytics_api.build_dashboard = synthetic_report
    # All reporting is explicitly marked synthetic in this isolated test server.
    @app.middleware("http")
    async def mark_test_data(request, call_next):
        response = await call_next(request)
        response.headers["X-EdPlan-Test-Data"] = "synthetic-isolated-database"
        return response
    return app, fixture, folder


if __name__ == "__main__":
    import uvicorn
    app, fixture, folder = create_preview()
    try:
        uvicorn.run(app, host="127.0.0.1", port=8011)
    finally:
        try:
            next(fixture)
        except StopIteration:
            pass
        folder.cleanup()
