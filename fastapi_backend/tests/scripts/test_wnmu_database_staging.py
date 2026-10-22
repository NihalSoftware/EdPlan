"""Real PostgreSQL rollback/replay tests using the guarded disposable NMT test cluster."""

import copy
import unittest
import uuid

import asyncpg

from scripts.nmt_catalog.database_staging import protected_fingerprints
from scripts.wnmu_catalog import UNIVERSITY_ID, apply_review_stage, build_stage
from tests.scripts import test_nmt_database_staging as disposable


class WnmuDatabaseTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await disposable.DatabaseStagingTests.asyncSetUp(self)
        await self.connection.execute(
            "INSERT INTO universities VALUES ($1,$2,$3,$4,$5)",
            UNIVERSITY_ID,
            "Western New Mexico University",
            "Silver City",
            "New Mexico",
            "https://wnmu.edu",
        )
        self.stage = build_stage()

    async def asyncTearDown(self):
        await disposable.DatabaseStagingTests.asyncTearDown(self)

    async def test_full_atomic_apply_and_replay(self):
        before = await protected_fingerprints(self.connection)
        report = await apply_review_stage(self.connection, self.stage, self.stage["stage_hash"])
        assert report["departments_inserted_this_run"] == 12
        assert report["review_records_inserted_this_run"] == 234
        assert before == await protected_fingerprints(self.connection)
        assert await self.connection.fetchval("SELECT count(*) FROM catalog_departments") == 12
        assert await self.connection.fetchval("SELECT count(*) FROM catalog_change_audit") == 246
        assert (
            await self.connection.fetchval(
                "SELECT count(*) FROM catalog_change_audit WHERE action='review' "
                "AND applied_at IS NULL"
            )
            == 234
        )
        repeat = await apply_review_stage(self.connection, self.stage, self.stage["stage_hash"])
        assert repeat["already_applied"]
        assert repeat["departments_inserted_this_run"] == 0
        assert repeat["review_records_inserted_this_run"] == 0
        assert await self.connection.fetchval("SELECT count(*) FROM catalog_change_audit") == 246

    async def test_wnmu_wrong_hash_and_institution_rejected(self):
        with self.assertRaises(ValueError):
            await apply_review_stage(self.connection, self.stage, "wrong")
        tampered = copy.deepcopy(self.stage)
        tampered["institution_id"] = str(uuid.uuid4())
        with self.assertRaises(ValueError):
            await apply_review_stage(self.connection, tampered, tampered["stage_hash"])
        assert await self.connection.fetchval("SELECT count(*) FROM catalog_import_runs") == 0

    async def test_wnmu_rollback_on_late_database_failure(self):
        await self.connection.execute(
            "ALTER TABLE catalog_change_audit ADD CONSTRAINT injected_failure "
            "CHECK (table_name <> 'programs')"
        )
        with self.assertRaises(asyncpg.CheckViolationError):
            await apply_review_stage(self.connection, self.stage, self.stage["stage_hash"])
        assert await self.connection.fetchval("SELECT count(*) FROM catalog_departments") == 0
        assert await self.connection.fetchval("SELECT count(*) FROM catalog_import_runs") == 0
        assert await self.connection.fetchval("SELECT count(*) FROM catalog_change_audit") == 0

    async def test_wnmu_preserves_department_name_conflict(self):
        department = self.stage["departments"][0]
        await self.connection.execute(
            "INSERT INTO catalog_departments (department_id,university_id,official_source_id,"
            "department_name,official_source_url,source_retrieved_at) "
            "VALUES ($1,$2,$3,$4,$5,now())",
            uuid.uuid4(),
            UNIVERSITY_ID,
            department["official_source_id"],
            "Existing name to preserve",
            department["official_source_url"],
        )
        report = await apply_review_stage(self.connection, self.stage, self.stage["stage_hash"])
        assert report["departments_inserted_this_run"] == 11
        assert report["summary"]["departments_awaiting_review"] == 1
        assert (
            await self.connection.fetchval(
                "SELECT department_name FROM catalog_departments WHERE official_source_id=$1",
                department["official_source_id"],
            )
            == "Existing name to preserve"
        )
