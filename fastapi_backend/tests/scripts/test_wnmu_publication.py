"""Offline source validation and guarded real-PostgreSQL publication tests."""

import copy
import json
import os
import tempfile
import unittest
import uuid
from pathlib import Path

import asyncpg
import pytest
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.student.domains.discovery.repositories.program_repository import ProgramRepository
from app.student.domains.discovery.schemas.program import ProgramDetail
from scripts.publish_wnmu_batch import FIXTURE, apply_batch, prepare_batch, protected_state
from scripts.wnmu_catalog import UNIVERSITY_ID
from tests.scripts import test_nmt_database_staging as disposable


def test_batch_credit_totals_identity_and_unknowns():
    batch = prepare_batch()
    assert batch == prepare_batch()
    assert len(batch["courses"]) == 16
    assert sum(c["credits"] for c in batch["courses"]) == 46
    assert batch["program"]["total_credit_hours"] == 46
    assert all(
        c["lecture_hours"] is None
        and c["lab_hours"] is None
        and c["recommended_year"] is None
        and c["recommended_semester"] is None
        for c in batch["courses"]
    )
    assert batch["program"]["metadata_json"]["course_rules_verified"] is False


def test_course_roster_transfer_matches_browser_observation():
    source = json.loads(FIXTURE.read_text(encoding="utf-8"))
    projection = json.dumps(
        [[c["coid"], c["code"], c["name"], c["credits"], c["section"]] for c in source["courses"]],
        ensure_ascii=False,
        separators=(",", ":"),
    )
    value = 2166136261
    for char in projection:
        value = ((value ^ ord(char)) * 16777619) & 0xFFFFFFFF
    assert len(projection) == 1526
    assert value == 0x8C11E2D9


@pytest.mark.parametrize("tamper", ["duplicate", "credits", "institution_source", "department"])
def test_incomplete_or_conflicting_source_rejected(tamper):
    source = json.loads(FIXTURE.read_text(encoding="utf-8"))
    if tamper == "duplicate":
        source["courses"][1] = copy.deepcopy(source["courses"][0])
    elif tamper == "credits":
        source["courses"][0]["credits"] = 4
    elif tamper == "institution_source":
        source["source_url"] = "https://example.org/"
    else:
        source["department_source_id"] = "catoid=8:ent302"
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "source.json"
        path.write_text(json.dumps(source), encoding="utf-8")
        with pytest.raises(ValueError):
            prepare_batch(path)


class WnmuPublicationDatabaseTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # This fixture verifies SHOW data_directory before any DDL and creates
        # a fresh random schema. No application database can be used accidentally.
        await disposable.DatabaseStagingTests.asyncSetUp(self)
        await self.connection.execute("""
            DROP TABLE program_departments,courses,programs;
            CREATE TABLE programs (
                program_id uuid PRIMARY KEY,university_id uuid NOT NULL REFERENCES universities,
                program_name text NOT NULL,degree text NOT NULL,total_credit_hours int NOT NULL
                    CHECK(total_credit_hours>0),metadata_json jsonb,
                official_source_id text,official_source_url text,source_retrieved_at timestamptz,
                UNIQUE(university_id,program_name,degree)
            );
            CREATE TABLE courses (
                course_id uuid PRIMARY KEY,program_id uuid NOT NULL REFERENCES programs,
                course_code text NOT NULL,course_name text NOT NULL,credits numeric NOT NULL
                    CHECK(credits>=0),lecture_hours numeric NOT NULL DEFAULT 0,
                lab_hours numeric NOT NULL DEFAULT 0,recommended_year int,
                recommended_semester text,description text,metadata_json jsonb,source_sequence int,
                official_source_id text,official_source_url text,source_retrieved_at timestamptz,
                CHECK(lecture_hours>=0 AND lab_hours>=0)
            );
            CREATE TABLE program_departments (
                id uuid PRIMARY KEY,program_id uuid NOT NULL REFERENCES programs,
                department_id uuid NOT NULL REFERENCES catalog_departments,
                official_source_url text NOT NULL,source_retrieved_at timestamptz NOT NULL,
                UNIQUE(program_id,department_id)
            );
        """)
        await self.connection.execute(
            "INSERT INTO universities VALUES ($1,$2,$3,$4,$5)",
            UNIVERSITY_ID,
            "Western New Mexico University",
            "Silver City",
            "New Mexico",
            "https://wnmu.edu",
        )
        await self.connection.execute("ALTER TABLE universities ADD COLUMN college_profile jsonb")
        await self.connection.execute(
            "INSERT INTO catalog_departments VALUES ($1,$2,$3,$4,$5,now(),NULL,NULL)",
            uuid.uuid4(),
            UNIVERSITY_ID,
            "catoid=8:ent301",
            "Department of Community & Workforce Development",
            "https://catalog.wnmu.edu/content.php?catoid=8&navoid=612#ent301",
        )
        self.sentinel_program, self.sentinel_course = uuid.uuid4(), uuid.uuid4()
        await self.connection.execute(
            "INSERT INTO programs (program_id,university_id,program_name,degree,"
            "total_credit_hours) "
            "VALUES ($1,$2,'Existing protected program','Existing degree',120)",
            self.sentinel_program,
            disposable.NNMC_ID,
        )
        await self.connection.execute(
            "INSERT INTO courses (course_id,program_id,course_code,course_name,credits,"
            "lecture_hours,lab_hours) VALUES ($1,$2,'EX 101','Existing protected course',3,3.5,0)",
            self.sentinel_course,
            self.sentinel_program,
        )
        self.batch = prepare_batch()

    async def asyncTearDown(self):
        await disposable.DatabaseStagingTests.asyncTearDown(self)

    async def test_atomic_publication_replay_and_api_serialization(self):
        before = await protected_state(self.connection, self.batch)
        result = await apply_batch(self.connection, self.batch, self.batch["batch_hash"])
        assert result["programs_inserted"] == 1 and result["courses_inserted"] == 16
        assert result["verification"]["unknown_contact_hours_preserved"]
        assert before == await protected_state(self.connection, self.batch)
        assert await self.connection.fetchval("SELECT count(*) FROM catalog_change_audit") == 19
        second = await apply_batch(self.connection, self.batch, self.batch["batch_hash"])
        assert second["already_applied"] and second["courses_inserted"] == 0
        defaults = await self.connection.fetch(
            "SELECT is_nullable,column_default FROM information_schema.columns "
            "WHERE table_schema=current_schema() AND table_name='courses' "
            "AND column_name IN ('lecture_hours','lab_hours')"
        )
        assert all(r["is_nullable"] == "YES" and r["column_default"] is None for r in defaults)
        # Exercise the actual ORM -> repository -> API model path against PostgreSQL.
        url = make_url(os.environ["NMT_TEST_DATABASE_URL"]).set(drivername="postgresql+asyncpg")
        engine = create_async_engine(
            url, connect_args={"server_settings": {"search_path": self.schema}}
        )
        try:
            async with async_sessionmaker(engine)() as session:
                payload = await ProgramRepository().get_program_by_id(
                    session, self.batch["program"]["program_id"]
                )
                response = ProgramDetail.model_validate(payload)
                assert len(response.courses) == 16
                assert all(
                    c.lecture_hours is None and c.lab_hours is None and not c.default_plan_eligible
                    for c in response.courses
                )
                assert response.total_credit_hours == 46
        finally:
            await engine.dispose()

    async def test_late_failure_rolls_back_ddl_data_and_audit(self):
        await self.connection.execute(
            "ALTER TABLE catalog_change_audit ADD CONSTRAINT injected_failure "
            "CHECK(table_name<>'courses' OR action<>'insert')"
        )
        before = await protected_state(self.connection, self.batch)
        with self.assertRaises(asyncpg.CheckViolationError):
            await apply_batch(self.connection, self.batch, self.batch["batch_hash"])
        assert before == await protected_state(self.connection, self.batch)
        assert await self.connection.fetchval("SELECT count(*) FROM programs") == 1
        assert await self.connection.fetchval("SELECT count(*) FROM courses") == 1
        assert await self.connection.fetchval("SELECT count(*) FROM catalog_import_runs") == 0
        assert await self.connection.fetchval("SELECT count(*) FROM catalog_change_audit") == 0
        assert (
            await self.connection.fetchval(
                "SELECT is_nullable FROM information_schema.columns "
                "WHERE table_schema=current_schema() "
                "AND table_name='courses' AND column_name='lecture_hours'"
            )
            == "NO"
        )

    async def test_existing_name_conflict_is_not_overwritten(self):
        await self.connection.execute(
            "INSERT INTO programs (program_id,university_id,program_name,degree,"
            "total_credit_hours) "
            "VALUES ($1,$2,$3,'Certificate',99)",
            uuid.uuid4(),
            UNIVERSITY_ID,
            self.batch["program"]["program_name"],
        )
        with self.assertRaisesRegex(ValueError, "Existing program"):
            await apply_batch(self.connection, self.batch, self.batch["batch_hash"])
        assert await self.connection.fetchval("SELECT count(*) FROM courses") == 1
        assert await self.connection.fetchval("SELECT count(*) FROM catalog_import_runs") == 0

    async def test_tampering_rejected_and_incomplete_replay_not_accepted(self):
        wrong = copy.deepcopy(self.batch)
        wrong["courses"][0]["credits"] = 99
        with self.assertRaisesRegex(ValueError, "checksum"):
            await apply_batch(self.connection, wrong, self.batch["batch_hash"])
        await apply_batch(self.connection, self.batch, self.batch["batch_hash"])
        await self.connection.execute(
            "UPDATE courses SET course_name='Changed value' WHERE course_id=$1",
            uuid.UUID(self.batch["courses"][0]["course_id"]),
        )
        with self.assertRaisesRegex(ValueError, "conflicts"):
            await apply_batch(self.connection, self.batch, self.batch["batch_hash"])
