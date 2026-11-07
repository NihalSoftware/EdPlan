"""Security and metric math against a disposable SQLite database, never production data."""
import asyncio
import os
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

for key, value in {
    "DATABASE_URL": "postgresql+asyncpg://test:test@localhost/test",
    "JWT_SECRET": "analytics-test-only-not-a-deployment-secret",
    "COLLEGE_SCORECARD_API_KEY": "test", "DEFAULT_ADMIN_EMAIL": "admin@example.test",
    "DEFAULT_ADMIN_PASSWORD": "test-only",
}.items():
    os.environ.setdefault(key, value)

from app.admin.analytics import Filters, build_dashboard, require_management
from app.admin.api import router, csv_safe
from app.db.session import get_db
from app.models.user import UserRole
from app.security.auth import create_access_token
from app.student.domains.auth.schemas.auth import RegisterRequest
from app.student.domains.auth.api.auth import router as auth_router

NOW = datetime(2026, 11, 3, 12, tzinfo=timezone.utc)
ADMIN = SimpleNamespace(role=UserRole.ADMIN, is_active=True, is_deactivated=False)


@pytest.fixture
def database(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'report.db'}")
    sessions = async_sessionmaker(engine)

    async def seed():
        async with engine.begin() as c:
            for ddl in [
                "CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT, password_hash TEXT, first_name TEXT, last_name TEXT, phone_number TEXT, role TEXT, is_active BOOLEAN, is_deactivated BOOLEAN, created_at DATETIME, updated_at DATETIME, last_login_at DATETIME)",
                "CREATE TABLE education_plans (id INTEGER PRIMARY KEY, user_id INTEGER, university_name TEXT, program_name TEXT, degree TEXT, created_at DATETIME, updated_at DATETIME, payload JSON)",
                "CREATE TABLE ed_plans (plan_id TEXT PRIMARY KEY, user_id INTEGER, university_id TEXT, program_id TEXT, plan_name TEXT, description TEXT, is_active BOOLEAN, legacy_education_plan_id INTEGER, created_at DATETIME, updated_at DATETIME)",
                "CREATE TABLE programs (program_id TEXT PRIMARY KEY, university_id TEXT, program_name TEXT, degree TEXT)",
                "CREATE TABLE universities (university_id TEXT PRIMARY KEY, university_name TEXT)",
            ]:
                await c.execute(text(ddl))
            for i in range(1, 13):
                await c.execute(text("INSERT INTO users (id,email,password_hash,role,is_active,is_deactivated,created_at,updated_at) VALUES (:i,:email,'hash',:role,1,:inactive,:now,:now)"),
                    {"i": i, "email": f"user{i}@example.test", "role": "admin" if i == 11 else "customer", "inactive": i == 12, "now": NOW})
            for i, student in enumerate([1, 1, 2, 3, 4, 5], 1):
                await c.execute(text("INSERT INTO education_plans VALUES (:id,:uid,'University of New Mexico-Main Campus','Biology','Bachelors',:d,:d,'{}')"), {"id": i, "uid": student, "d": NOW - timedelta(days=1)})
            for i in range(6, 11):
                await c.execute(text("INSERT INTO education_plans VALUES (:id,:uid,'University of New Mexico','Biology','Bachelors',:d,:d,'{}')"), {"id": i+1, "uid": i, "d": NOW - timedelta(days=40)})
            for i in [11, 12]:
                await c.execute(text("INSERT INTO education_plans VALUES (:id,:uid,'Private label','Private program',NULL,:d,:d,'{}')"), {"id": i+2, "uid": i, "d": NOW-timedelta(days=1)})
            await c.execute(text("INSERT INTO universities VALUES ('u','University of New Mexico')"))
            await c.execute(text("INSERT INTO programs VALUES ('p','u','Biology','Bachelors')"))
            for plan, link, active in [('linked', 1, 1), ('deactivated', 2, 0), ('standalone', None, 1)]:
                await c.execute(text("INSERT INTO ed_plans VALUES (:id,:uid,'u','p','Plan',NULL,:active,:link,:d,:d)"),
                    {"id": plan, "uid": 5 if link is None else 1, "active": active, "link": link, "d": NOW-timedelta(days=1)})
    asyncio.run(seed())
    yield sessions
    asyncio.run(engine.dispose())


def report(sessions, filters=Filters()):
    async def run():
        async with sessions() as db:
            return await build_dashboard(db, ADMIN, filters, NOW)
    return asyncio.run(run())


def test_distinct_students_deduplication_and_exclusions(database):
    data = report(database)
    metrics = {m.id: m for m in data.metrics}
    assert metrics["students"].value == 10
    assert metrics["planning_students"].value == 5
    assert metrics["plans"].value == 6
    assert metrics["average"].value == 1.2
    assert metrics["plans"].delta == 20
    assert len(data.institutions) == 1
    assert data.institutions[0].label == "university of new mexico"
    assert sum(x["plans"] for x in data.trend) == 6
    assert len(data.trend) == 30
    assert all(m.value is None for m in data.metrics if m.pillar != "Engagement")
    assert "example.test" not in data.model_dump_json()
    assert "payload" not in data.model_dump_json()


def test_period_and_dimension_filters_no_fake_zero_denominator(database):
    all_time = report(database, Filters(period="all"))
    assert next(m.value for m in all_time.metrics if m.id == "plans") == 11
    assert next(m.delta for m in all_time.metrics if m.id == "plans") is None
    empty = report(database, Filters(program="not a real program"))
    assert next(m.value for m in empty.metrics if m.id == "plans") == 0
    average = next(m for m in empty.metrics if m.id == "average")
    assert average.value is None and average.status == "unavailable"
    data = report(database, Filters(period="custom", start=NOW.date()-timedelta(days=1), end=NOW.date()-timedelta(days=1), institution="university of new mexico", degree="bachelors"))
    assert next(m.value for m in data.metrics if m.id == "plans") == 6


def test_small_cohort_and_complementary_panel_suppression(database):
    async def alter():
        async with database() as db:
            await db.execute(text("UPDATE education_plans SET program_name='Rare' WHERE id=3"))
            await db.commit()
    asyncio.run(alter())
    rare = report(database, Filters(program="rare"))
    assert all(m.value is None for m in rare.metrics if m.id != "students")
    assert not rare.programs and not rare.institutions and not rare.trend
    broader = report(database)
    assert broader.programs == []  # Entire partition withheld; not just the rare cell.


def test_date_differencing_does_not_reveal_small_daily_cohorts(database):
    async def alter():
        async with database() as db:
            await db.execute(text("UPDATE education_plans SET created_at=:d WHERE id=3"), {"d": NOW-timedelta(days=2)})
            await db.commit()
    asyncio.run(alter())
    data = report(database)
    assert next(m for m in data.metrics if m.id == "plans").status == "suppressed"
    assert not data.trend


def test_null_labels_and_unrecorded_dates_are_safe(database):
    async def alter():
        async with database() as db:
            await db.execute(text("UPDATE education_plans SET program_name=NULL, degree=NULL, created_at=NULL WHERE id=3"))
            await db.commit()
    asyncio.run(alter())
    data = report(database, Filters(period="all"))
    assert next(m for m in data.metrics if m.id == "plans").status == "suppressed"
    assert data.programs == []


def test_authentication_and_student_authorization(database):
    app = FastAPI()
    app.include_router(router, prefix="/api")
    app.include_router(auth_router, prefix="/api")
    async def db_override():
        async with database() as db:
            yield db
    app.dependency_overrides[get_db] = db_override
    with TestClient(app) as client:
        registration = client.post("/api/users", json={"first_name": "A", "last_name": "B", "email": "a@example.com", "password": "test", "role": "admin"})
        assert registration.status_code == 422
        for path in ["access", "summary", "export"]:
            assert client.get(f"/api/admin/analytics/{path}").status_code == 401
            denied = client.get(f"/api/admin/analytics/{path}", headers={"Authorization": "Bearer " + create_access_token("user1@example.test")})
            assert denied.status_code == 403
            assert "planning_students" not in denied.text
        headers = {"Authorization": "Bearer " + create_access_token("user11@example.test")}
        assert client.get("/api/admin/analytics/access", headers=headers).json()["authorized"] is True
        response = client.get("/api/admin/analytics/summary?period=all", headers=headers)
        assert response.status_code == 200, response.text
        assert response.headers["cache-control"] == "no-store"
        csv = client.get("/api/admin/analytics/export?period=all", headers=headers)
        assert csv.status_code == 200 and "text/csv" in csv.headers["content-type"]
        assert "@example.test" not in csv.text
        assert client.get("/api/admin/analytics/summary?period=custom&start=2026-01-02&end=2026-01-01", headers=headers).status_code == 422


def test_role_cannot_be_self_assigned_and_service_authorization():
    with pytest.raises(ValidationError):
        RegisterRequest(first_name="A", last_name="B", email="a@example.com", password="test", role="admin")
    with pytest.raises(HTTPException) as exc:
        require_management(SimpleNamespace(role=UserRole.CUSTOMER, is_active=True, is_deactivated=False))
    assert exc.value.status_code == 403
    with pytest.raises(HTTPException):
        require_management(SimpleNamespace(role=UserRole.ADMIN, is_active=True, is_deactivated=True))
    assert csv_safe("=HYPERLINK(1)").startswith("'")
    assert csv_safe("Biology") == "Biology"


def test_utc_boundaries_and_bad_ranges():
    start, end = Filters(period="7").bounds(NOW)
    assert end == datetime(2026, 11, 3, tzinfo=timezone.utc)
    assert (end - start).days == 7
    for kwargs in [dict(period="custom"), dict(period="custom", start="2026-01-02", end="2026-01-01"), dict(period="30", start="2026-01-01")]:
        with pytest.raises(ValidationError):
            Filters(**kwargs)
