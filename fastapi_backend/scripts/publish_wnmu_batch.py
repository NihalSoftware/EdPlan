"""Apply the approved nullable-hours correction and a source-verified WNMU roster batch.

No guessed contact hours, semester placements, prerequisites, deactivations or deletes.
This publishes the course roster, not a verified prerequisite graph or automatic plan.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import uuid
from datetime import UTC, datetime
from pathlib import Path

import asyncpg
from dotenv import dotenv_values
from sqlalchemy.engine import make_url

from scripts.nmt_catalog.baseline import save_json
from scripts.nmt_catalog.normalize import canonical_hash
from scripts.wnmu_catalog import INDEX, UNIVERSITY_ID, approved_source, as_json, build_stage

FIXTURE = Path(__file__).parents[1] / "tests/scripts/fixtures/wnmu/pharmacy-technician.json"
OUTPUT = Path("artifacts/wnmu/catalog-8/pharmacy-technician")


def prepare_batch(path=FIXTURE):
    raw = path.read_bytes()
    source = json.loads(raw)
    index = build_stage()
    matches = [
        p for p in index["programs"] if p["official_source_id"] == source["official_source_id"]
    ]
    if (
        len(matches) != 1
        or source["catalog_year"] != index["catalog_year"]
        or source["source_url"] != matches[0]["official_source_url"]
        or source["official_name"] != matches[0]["official_name"]
        or source["department_source_id"] != matches[0]["academic_unit_source_id"]
        or source["requirements_structure"]
        != "all_listed_courses_required_no_alternatives_in_program_page"
        or source["degree"] != "Certificate"
    ):
        raise ValueError("Program identity or requirements differ from reviewed source")
    approved_source(source["source_url"])
    retrieved = datetime.fromisoformat(source["retrieved_at"])
    if retrieved.tzinfo is None:
        raise ValueError("Timezone-aware source observation required")
    codes, identities, total, supporting, core = set(), set(), 0, 0, 0
    for course in source["courses"]:
        if (
            not re.fullmatch(r"[A-Z]+ [0-9]+[A-Z]?", course["code"])
            or not re.fullmatch(r"[0-9]+", course["coid"])
            or not course["name"].strip()
            or course["code"] in codes
            or course["coid"] in identities
            or type(course["credits"]) is not int
            or course["credits"] <= 0
        ):
            raise ValueError("Invalid or duplicate official course")
        codes.add(course["code"])
        identities.add(course["coid"])
        total += course["credits"]
        if course["section"] == "Supporting Coursework (13 credit hours)":
            supporting += course["credits"]
        elif course["section"] == "Pharmacy Technician Core Requirements":
            core += course["credits"]
        else:
            raise ValueError("Unreviewed curriculum section")
    if (
        len(codes) != 16
        or total != source["total_credit_hours"]
        or total != 46
        or supporting != source["supporting_credit_hours"]
        or supporting != 13
        or core != source["core_credit_hours"]
        or core != 33
    ):
        raise ValueError("Course roster does not reconcile with official credit totals")
    evidence = {
        "url": source["source_url"],
        "retrieved_at": retrieved.isoformat(),
        "snapshot_sha256": hashlib.sha256(raw).hexdigest(),
        "capture_method": source["capture_method"],
        "index_snapshot_sha256": index["source"]["snapshot_sha256"],
    }
    program_id = uuid.uuid5(UNIVERSITY_ID, "wnmu:" + source["official_source_id"])
    program = {
        "program_id": str(program_id),
        "university_id": str(UNIVERSITY_ID),
        "program_name": source["official_name"],
        "degree": source["degree"],
        "total_credit_hours": total,
        "official_source_id": source["official_source_id"],
        "official_source_url": source["source_url"],
        "metadata_json": {
            "catalog_year": source["catalog_year"],
            "source": evidence,
            "curriculum_roster_complete": True,
            "course_rules_verified": False,
            "automated_semester_plan_verified": False,
            "import_scope": "verified_program_roster_only",
            "supporting_credit_hours": supporting,
            "core_credit_hours": core,
        },
    }
    courses = []
    for sequence, course in enumerate(source["courses"], 1):
        identity = "catoid=8:coid=" + course["coid"]
        courses.append(
            {
                "course_id": str(uuid.uuid5(program_id, identity)),
                "program_id": str(program_id),
                "course_code": course["code"],
                "course_name": course["name"],
                "credits": course["credits"],
                "lecture_hours": None,
                "lab_hours": None,
                "recommended_year": None,
                "recommended_semester": None,
                "description": course.get("description"),
                "source_sequence": sequence,
                "official_source_id": identity,
                "official_source_url": source["source_url"],
                "metadata_json": {
                    "catalog_year": source["catalog_year"],
                    "source": evidence,
                    "requirement_section": course["section"],
                    "level_of_study": course.get("level_of_study"),
                    "contact_hours_status": "not_published_in_captured_source",
                    "prerequisite": None,
                    "corequisite": None,
                    "course_rules_status": "not_fully_retrieved",
                    "department_ownership_status": "not_verified",
                    "is_elective": False,
                },
            }
        )
    batch = {
        "program": program,
        "courses": courses,
        "source": evidence,
        "department_source_id": source["department_source_id"],
        "schema_change": "courses_lecture_and_lab_hours_nullable_without_default_v1",
    }
    batch["batch_hash"] = canonical_hash(batch)
    return batch


async def protected_state(connection, batch):
    """Exclude only deterministic new row IDs; fingerprint all existing academic/student rows."""
    pid = uuid.UUID(batch["program"]["program_id"])
    ids = [uuid.UUID(c["course_id"]) for c in batch["courses"]]
    queries = {
        "programs": ("SELECT * FROM programs WHERE program_id<>$1", [pid]),
        "courses": ("SELECT * FROM courses WHERE NOT(course_id=ANY($1::uuid[]))", [ids]),
        "program_departments": ("SELECT * FROM program_departments WHERE program_id<>$1", [pid]),
    }
    for table in (
        "universities",
        "catalog_departments",
        "course_departments",
        "course_prerequisites",
        "course_corequisites",
        "education_plans",
        "ed_plans",
        "plan_courses",
    ):
        queries[table] = (f'SELECT * FROM "{table}"', [])
    result = {}
    for table, (query, params) in queries.items():
        result[table] = await connection.fetchval(
            "SELECT md5(coalesce(string_agg(h,'' ORDER BY h),'')) "
            f"FROM (SELECT md5(to_jsonb(t)::text) h FROM ({query}) t) x",
            *params,
        )
    return result


async def verify_batch(connection, batch):
    pid = uuid.UUID(batch["program"]["program_id"])
    row = await connection.fetchrow("SELECT * FROM programs WHERE program_id=$1", pid)
    if not row:
        raise ValueError("Published program is missing")
    expected = batch["program"]
    for key in (
        "program_id",
        "university_id",
        "program_name",
        "degree",
        "total_credit_hours",
        "official_source_id",
        "official_source_url",
    ):
        current = (
            str(row[key]) if key.endswith("_id") and isinstance(row[key], uuid.UUID) else row[key]
        )
        if current != expected[key]:
            raise ValueError("Published program conflicts with source")
    if json.loads(row["metadata_json"]) != expected["metadata_json"]:
        raise ValueError("Published program provenance differs")
    retrieved = datetime.fromisoformat(batch["source"]["retrieved_at"])
    if row["source_retrieved_at"] != retrieved:
        raise ValueError("Published program retrieval timestamp differs")
    rows = await connection.fetch("SELECT * FROM courses WHERE program_id=$1", pid)
    if len(rows) != len(batch["courses"]):
        raise ValueError("Published course roster incomplete or has extra records")
    actual = {str(r["course_id"]): r for r in rows}
    for expected in batch["courses"]:
        row = actual.get(expected["course_id"])
        if row is None:
            raise ValueError("Published course identity mismatch")
        if row["source_retrieved_at"] != retrieved:
            raise ValueError("Published course retrieval timestamp differs")
        for key, value in expected.items():
            current = row[key]
            if key == "metadata_json":
                current = json.loads(current)
            if key in {"course_id", "program_id"}:
                current = str(current)
            if current != value:
                raise ValueError("Published course field conflicts with source: " + key)
    relations = await connection.fetch(
        "SELECT d.university_id,d.official_source_id,pd.official_source_url,pd.source_retrieved_at "
        "FROM program_departments pd JOIN catalog_departments d USING(department_id) "
        "WHERE pd.program_id=$1",
        pid,
    )
    if len(relations) != 1 or dict(relations[0]) != {
        "university_id": UNIVERSITY_ID,
        "official_source_id": batch["department_source_id"],
        "official_source_url": INDEX + "#ent301",
        "source_retrieved_at": retrieved,
    }:
        raise ValueError("Program/department relationship differs from source")
    return {
        "programs": 1,
        "courses": len(rows),
        "course_credits": sum(int(r["credits"]) for r in rows),
        "unknown_contact_hours_preserved": all(
            r["lecture_hours"] is None and r["lab_hours"] is None for r in rows
        ),
    }


async def apply_batch(connection, batch, expected_hash):
    if (
        batch["batch_hash"] != expected_hash
        or canonical_hash({k: v for k, v in batch.items() if k != "batch_hash"}) != expected_hash
    ):
        raise ValueError("Reviewed batch checksum required")
    pid = uuid.UUID(batch["program"]["program_id"])
    run_id = uuid.uuid5(pid, "roster-publication-v1:" + expected_hash)
    retrieved = datetime.fromisoformat(batch["source"]["retrieved_at"])
    async with connection.transaction(isolation="serializable"):
        await connection.execute("SET LOCAL statement_timeout='30s'")
        await connection.execute("SET LOCAL lock_timeout='5s'")
        await connection.execute(
            "SELECT pg_advisory_xact_lock($1)",
            int.from_bytes(UNIVERSITY_ID.bytes[:8], "big", signed=True),
        )
        university = await connection.fetchrow(
            "SELECT university_name,city,state,website FROM universities WHERE university_id=$1",
            UNIVERSITY_ID,
        )
        if not university or dict(university) != {
            "university_name": "Western New Mexico University",
            "city": "Silver City",
            "state": "New Mexico",
            "website": "https://wnmu.edu",
        }:
            raise ValueError("WNMU target differs from reviewed identity")
        department = await connection.fetchrow(
            "SELECT * FROM catalog_departments WHERE university_id=$1 AND official_source_id=$2",
            UNIVERSITY_ID,
            batch["department_source_id"],
        )
        if not department or department["department_name"] != (
            "Department of Community & Workforce Development"
        ):
            raise ValueError("Verified parent department is missing or conflicting")
        schema = [
            dict(r)
            for r in await connection.fetch(
                "SELECT column_name,data_type,is_nullable,column_default "
                "FROM information_schema.columns "
                "WHERE table_schema=current_schema() AND table_name='courses' "
                "AND column_name IN ('lecture_hours','lab_hours') ORDER BY column_name"
            )
        ]
        if len(schema) != 2 or any(
            r["data_type"] != "numeric" or r["column_default"] not in ("0", None) for r in schema
        ):
            raise ValueError("Unexpected course contact-hours schema; no DDL performed")
        previous = await connection.fetchrow(
            "SELECT status,summary_json FROM catalog_import_runs WHERE import_run_id=$1", run_id
        )
        if previous:
            audit_count = await connection.fetchval(
                "SELECT count(*) FROM catalog_change_audit WHERE import_run_id=$1", run_id
            )
            summary = json.loads(previous["summary_json"])
            if (
                previous["status"] != "completed"
                or summary.get("batch_hash") != expected_hash
                or audit_count != 19
                or any(r["is_nullable"] != "YES" or r["column_default"] is not None for r in schema)
            ):
                raise ValueError("Previous batch/schema is incomplete")
            verification = await verify_batch(connection, batch)
            return {
                "import_run_id": str(run_id),
                "already_applied": True,
                "programs_inserted": 0,
                "courses_inserted": 0,
                "verification": verification,
            }
        conflicts = await connection.fetchval(
            "SELECT count(*) FROM programs WHERE university_id=$1 AND "
            "(program_id=$2 OR official_source_id=$3 OR official_source_url=$4 "
            "OR program_name=$5)",
            UNIVERSITY_ID,
            pid,
            batch["program"]["official_source_id"],
            batch["program"]["official_source_url"],
            batch["program"]["program_name"],
        )
        if conflicts:
            raise ValueError(
                "Existing program requires reviewed matching; no overwrite or duplicate"
            )
        before = await protected_state(connection, batch)
        await connection.execute(
            "INSERT INTO catalog_import_runs (import_run_id,university_id,catalog_name,"
            "source_root_url,mode,status,retrieved_at,started_at,summary_json,error_json) "
            "VALUES ($1,$2,$3,$4,'apply','running',$5,$6,'{}'::jsonb,'{}'::jsonb)",
            run_id,
            UNIVERSITY_ID,
            "WNMU Pharmacy Technician verified roster; nullable hours",
            batch["source"]["url"],
            retrieved,
            datetime.now(UTC),
        )
        audits = []

        def audit(key, table, record_id, action, old, new, method):
            audits.append(
                (
                    uuid.uuid5(run_id, key),
                    run_id,
                    table,
                    record_id,
                    action,
                    as_json(old),
                    as_json(new),
                    batch["source"]["url"],
                    method,
                    "high",
                    "User-approved nullable hours. Roster fields verified; "
                    "prerequisite graph and semester placements NOT certified.",
                    datetime.now(UTC),
                    datetime.now(UTC),
                )
            )

        # Existing row values are untouched. No migration stamp/reset or type conversion.
        await connection.execute(
            "ALTER TABLE courses "
            "ALTER COLUMN lecture_hours DROP NOT NULL, "
            "ALTER COLUMN lecture_hours DROP DEFAULT, "
            "ALTER COLUMN lab_hours DROP NOT NULL, "
            "ALTER COLUMN lab_hours DROP DEFAULT"
        )
        audit(
            "schema:nullable-contact-hours",
            "courses",
            None,
            "update",
            schema,
            {
                "lecture_hours": {"nullable": True, "default": None},
                "lab_hours": {"nullable": True, "default": None},
            },
            "user_approved_exact_column_schema_change",
        )
        program = batch["program"]
        await connection.execute(
            "INSERT INTO programs (program_id,university_id,program_name,degree,total_credit_hours,"
            "metadata_json,official_source_id,official_source_url,source_retrieved_at) "
            "VALUES ($1,$2,$3,$4,$5,$6::jsonb,$7,$8,$9)",
            pid,
            UNIVERSITY_ID,
            program["program_name"],
            program["degree"],
            program["total_credit_hours"],
            as_json(program["metadata_json"]),
            program["official_source_id"],
            program["official_source_url"],
            retrieved,
        )
        audit("program", "programs", pid, "insert", {}, program, "scoped_official_program_id")
        values = []
        for course in batch["courses"]:
            cid = uuid.UUID(course["course_id"])
            values.append(
                (
                    cid,
                    pid,
                    course["course_code"],
                    course["course_name"],
                    course["credits"],
                    course["description"],
                    as_json(course["metadata_json"]),
                    course["source_sequence"],
                    course["official_source_id"],
                    course["official_source_url"],
                    retrieved,
                )
            )
            audit(
                "course:" + course["official_source_id"],
                "courses",
                cid,
                "insert",
                {},
                course,
                "scoped_official_course_id_and_exact_code",
            )
        await connection.executemany(
            "INSERT INTO courses (course_id,program_id,course_code,course_name,credits,"
            "lecture_hours,lab_hours,recommended_year,recommended_semester,description,"
            "metadata_json,source_sequence,official_source_id,official_source_url,"
            "source_retrieved_at) "
            "VALUES ($1,$2,$3,$4,$5,NULL,NULL,NULL,NULL,$6,$7::jsonb,$8,$9,$10,$11)",
            values,
        )
        relation_id = uuid.uuid5(pid, "department:" + batch["department_source_id"])
        await connection.execute(
            "INSERT INTO program_departments (id,program_id,department_id,official_source_url,"
            "source_retrieved_at) VALUES ($1,$2,$3,$4,$5)",
            relation_id,
            pid,
            department["department_id"],
            INDEX + "#ent301",
            retrieved,
        )
        audit(
            "program-department",
            "program_departments",
            relation_id,
            "insert",
            {},
            {
                "program_id": str(pid),
                "department_id": str(department["department_id"]),
                "official_source_url": INDEX + "#ent301",
            },
            "official_index_parent_relationship",
        )
        await connection.executemany(
            "INSERT INTO catalog_change_audit (audit_id,import_run_id,table_name,record_id,action,"
            "old_values,proposed_new_values,source_url,match_method,confidence_level,notes,"
            "created_at,applied_at) VALUES "
            "($1,$2,$3,$4,$5,$6::jsonb,$7::jsonb,$8,$9,$10,$11,$12,$13)",
            audits,
        )
        verification = await verify_batch(connection, batch)
        if before != await protected_state(connection, batch):
            raise ValueError("Existing academic/student data changed; rolling back entire batch")
        summary = {
            "batch_hash": expected_hash,
            "programs_inserted": 1,
            "courses_inserted": 16,
            "program_department_links_inserted": 1,
            "audit_records": len(audits),
            "existing_records_unchanged": True,
            "protected_fingerprints": before,
            "curriculum_roster_complete": True,
            "course_rules_verified": False,
            "semester_placements_verified": False,
            "verification": verification,
        }
        await connection.execute(
            "UPDATE catalog_import_runs SET status='completed',completed_at=$2,"
            "summary_json=$3::jsonb "
            "WHERE import_run_id=$1",
            run_id,
            datetime.now(UTC),
            as_json(summary),
        )
    return {"import_run_id": str(run_id), "already_applied": False, **summary}


async def run(args):
    batch = prepare_batch(args.snapshot)
    save_json(args.output / "prepared-batch.json", batch)
    if not args.apply:
        print(
            as_json(
                {
                    "batch_hash": batch["batch_hash"],
                    "programs": 1,
                    "courses": 16,
                    "credits": 46,
                    "apply": False,
                }
            )
        )
        return
    if args.expected_batch_hash != batch["batch_hash"] or not args.approved_nullable_hours:
        raise ValueError("Reviewed hash and explicit nullable-hours approval required")
    config = {**dotenv_values(".env"), **os.environ}
    url = make_url(config["DATABASE_URL"])
    connection = await asyncpg.connect(
        url.set(drivername="postgresql").render_as_string(hide_password=False), timeout=15
    )
    try:
        await connection.execute("SET search_path TO public")
        report = await apply_batch(connection, batch, args.expected_batch_hash)
    finally:
        await connection.close()
    name = "repeat-report.json" if report["already_applied"] else "apply-report.json"
    save_json(args.output / name, report)
    print(as_json({k: v for k, v in report.items() if k != "protected_fingerprints"}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=FIXTURE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--approved-nullable-hours", action="store_true")
    parser.add_argument("--expected-batch-hash")
    asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    main()
