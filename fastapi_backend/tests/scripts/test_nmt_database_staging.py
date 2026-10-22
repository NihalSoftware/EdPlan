"""Real PostgreSQL tests, only against an explicitly identified disposable local cluster."""

from __future__ import annotations

import json
import os
import unittest
import uuid
from pathlib import Path

import asyncpg

from scripts.nmt_catalog.database_staging import apply_staging, protected_fingerprints
from scripts.nmt_catalog.normalize import canonical_hash, normalize

NMT_ID = uuid.UUID("82e747e1-7543-43b4-88e1-983fe859a082")
NNMC_ID = uuid.UUID("ec4d6722-705e-4c34-aaef-f25f95ebfa19")
FIXTURES = Path(__file__).parent / "fixtures" / "nmt"


class DatabaseStagingTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        dsn, expected_directory = os.getenv("NMT_TEST_DATABASE_URL"), os.getenv("NMT_TEST_PGDATA")
        if not dsn or not expected_directory:
            self.skipTest("Explicit disposable PostgreSQL test cluster not configured")
        self.connection = await asyncpg.connect(dsn, timeout=5)
        directory = await self.connection.fetchval("SHOW data_directory")
        if Path(directory).resolve() != Path(expected_directory).resolve():
            await self.connection.close()
            self.fail("Refusing test DDL against an unidentified database cluster")
        self.schema = "nmt_test_" + uuid.uuid4().hex
        await self.connection.execute(f'CREATE SCHEMA "{self.schema}"')
        await self.connection.execute(f'SET search_path TO "{self.schema}"')
        await self.connection.execute("""
            CREATE TABLE universities (
                university_id uuid PRIMARY KEY, university_name varchar(255) NOT NULL,
                city varchar(120) NOT NULL,state varchar(120) NOT NULL, website varchar(255)
            );
            CREATE TABLE catalog_departments (
                department_id uuid PRIMARY KEY,
                university_id uuid NOT NULL REFERENCES universities(university_id),
                official_source_id varchar(120) NOT NULL,department_name varchar(255) NOT NULL,
                official_source_url varchar(1000) NOT NULL,source_retrieved_at timestamptz NOT NULL,
                officially_active boolean,active_evidence_url varchar(1000),
                UNIQUE(university_id,official_source_id)
            );
            CREATE TABLE catalog_import_runs (
                import_run_id uuid PRIMARY KEY,
                university_id uuid NOT NULL REFERENCES universities(university_id),
                catalog_name varchar(255) NOT NULL,source_root_url varchar(1000) NOT NULL,
                mode varchar(20) NOT NULL CHECK(mode IN ('apply','dry_run')),
                status varchar(20) NOT NULL
                    CHECK(status IN ('running','planned','completed','failed')),
                retrieved_at timestamptz, started_at timestamptz NOT NULL,
                completed_at timestamptz,summary_json jsonb NOT NULL,error_json jsonb NOT NULL
            );
            CREATE TABLE catalog_change_audit (
                audit_id uuid PRIMARY KEY,
                import_run_id uuid NOT NULL REFERENCES catalog_import_runs(import_run_id),
                table_name varchar(120) NOT NULL,record_id uuid,
                action varchar(20) NOT NULL CHECK(action IN
                    ('insert','update','review','not_found','no_change')),
                old_values jsonb NOT NULL,proposed_new_values jsonb NOT NULL,
                source_url varchar(1000) NOT NULL,match_method varchar(120) NOT NULL,
                confidence_level varchar(20) NOT NULL
                    CHECK(confidence_level IN ('high','medium','low')),
                notes text,created_at timestamptz NOT NULL,applied_at timestamptz
            );
        """)
        from scripts.nmt_catalog.database_staging import PROTECTED_TABLES

        for table in PROTECTED_TABLES:
            await self.connection.execute(
                f'CREATE TABLE "{table}" (id uuid PRIMARY KEY,payload jsonb)'
            )
            await self.connection.execute(
                f'INSERT INTO "{table}" VALUES ($1,$2::jsonb)',
                uuid.uuid4(),
                json.dumps({"institution": "NNMC", "sentinel": "do not change"}),
            )
        await self.connection.executemany(
            "INSERT INTO universities VALUES ($1,$2,$3,$4,$5)",
            [
                (
                    NMT_ID,
                    "New Mexico Institute of Mining and Technology",
                    "Socorro",
                    "New Mexico",
                    "https://www.nmt.edu",
                ),
                (
                    NNMC_ID,
                    "Northern New Mexico College",
                    "Española",
                    "New Mexico",
                    "https://nnmc.edu",
                ),
            ],
        )
        records = []
        for code in ("BS-BIOLOGY", "BIOL2110L"):
            fixture = json.loads((FIXTURES / f"{code}.json").read_text(encoding="utf-8"))
            records.append(
                normalize(fixture["kind"], fixture["record"], fixture["source"], "2026-2027")
            )
        self.source = records[0]["source"]
        self.stage = {
            "catalog_year": "2026-2027",
            "institution": {"official_name": "New Mexico Institute of Mining and Technology"},
            "departments": [
                {"code": "BIOL", "name": "Biology"},
                {"code": "CHEM", "name": "Chemistry"},
            ],
            "programs": [records[0]],
            "courses": [records[1]],
        }
        self.stage["stage_hash"] = canonical_hash(self.stage)

    async def asyncTearDown(self):
        if hasattr(self, "connection") and not self.connection.is_closed():
            if hasattr(self, "schema"):
                # Only the exact randomly generated schema created by this test is removed.
                await self.connection.execute(f'DROP SCHEMA "{self.schema}" CASCADE')
            await self.connection.close()

    async def test_atomic_insertion_replay_isolation_and_review_only(self):
        before = await protected_fingerprints(self.connection)
        first = await apply_staging(self.connection, self.stage, self.source, NMT_ID)
        self.assertEqual(first["departments_inserted_this_run"], 2)
        self.assertEqual(first["review_records_inserted_this_run"], 2)
        self.assertEqual(before, await protected_fingerprints(self.connection))
        self.assertEqual(
            await self.connection.fetchval("SELECT count(*) FROM catalog_departments"), 2
        )
        self.assertEqual(
            await self.connection.fetchval("SELECT count(*) FROM catalog_change_audit"), 4
        )
        self.assertEqual(
            await self.connection.fetchval(
                "SELECT count(*) FROM catalog_change_audit "
                "WHERE action='review' AND applied_at IS NULL"
            ),
            2,
        )
        second = await apply_staging(self.connection, self.stage, self.source, NMT_ID)
        self.assertTrue(second["already_applied"])
        self.assertEqual(second["departments_inserted_this_run"], 0)
        self.assertEqual(
            await self.connection.fetchval("SELECT count(*) FROM catalog_import_runs"), 1
        )
        self.assertEqual(
            await self.connection.fetchval("SELECT count(*) FROM catalog_change_audit"), 4
        )
        self.assertEqual(before, await protected_fingerprints(self.connection))

    async def test_batch_failure_rolls_back_departments_and_audit(self):
        self.stage["departments"][1]["name"] = "X" * 256
        with self.assertRaises(asyncpg.StringDataRightTruncationError):
            await apply_staging(self.connection, self.stage, self.source, NMT_ID)
        for table in ("catalog_import_runs", "catalog_change_audit", "catalog_departments"):
            self.assertEqual(await self.connection.fetchval(f'SELECT count(*) FROM "{table}"'), 0)

    async def test_existing_conflicting_department_is_reviewed_never_overwritten(self):
        await self.connection.execute(
            "INSERT INTO catalog_departments (department_id,university_id,official_source_id,"
            "department_name,official_source_url,source_retrieved_at) VALUES "
            "($1,$2,'BIOL','Preserved existing name','https://catalog.nmt.edu/departments',now())",
            uuid.uuid4(),
            NMT_ID,
        )
        result = await apply_staging(self.connection, self.stage, self.source, NMT_ID)
        self.assertEqual(result["summary"]["departments_awaiting_review"], 1)
        self.assertEqual(
            await self.connection.fetchval(
                "SELECT department_name FROM catalog_departments WHERE official_source_id='BIOL'"
            ),
            "Preserved existing name",
        )

    async def test_wrong_institution_refused_before_any_write(self):
        with self.assertRaises(ValueError):
            await apply_staging(self.connection, self.stage, self.source, NNMC_ID)
        self.assertEqual(
            await self.connection.fetchval("SELECT count(*) FROM catalog_import_runs"), 0
        )

    async def test_full_reviewed_cached_payload(self):
        folder = os.getenv("NMT_FULL_STAGE_FOLDER")
        if not folder:
            self.skipTest("Full local staging artifact not requested")
        from scripts.nmt_catalog.database_staging import validated_stage

        stage_file = Path(folder) / "staged-catalog.json"
        expected_hash = json.loads(stage_file.read_text(encoding="utf-8"))["stage_hash"]
        stage, source = validated_stage(Path(folder), expected_hash)
        before = await protected_fingerprints(self.connection)
        first = await apply_staging(self.connection, stage, source, NMT_ID)
        self.assertEqual(first["departments_inserted_this_run"], len(stage["departments"]))
        self.assertEqual(
            first["review_records_inserted_this_run"],
            len(stage["programs"]) + len(stage["courses"]),
        )
        second = await apply_staging(self.connection, stage, source, NMT_ID)
        self.assertTrue(second["already_applied"])
        self.assertEqual(before, await protected_fingerprints(self.connection))
