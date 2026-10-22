"""A read-only schema inventory. Never imports application startup or prints credentials."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import asyncpg
from dotenv import dotenv_values
from sqlalchemy.engine import make_url

CATALOG_TABLES = (
    "universities",
    "programs",
    "courses",
    "course_prerequisites",
    "course_corequisites",
    "catalog_departments",
    "program_departments",
    "course_departments",
    "catalog_import_runs",
    "catalog_change_audit",
    "education_plans",
    "ed_plans",
    "plan_courses",
    "alembic_version",
)


async def baseline(env_path: Path) -> dict:
    cfg = {**dotenv_values(env_path)}
    import os

    cfg.update(os.environ)
    url = make_url(cfg["DATABASE_URL"])
    dsn = url.set(drivername="postgresql").render_as_string(hide_password=False)
    report = {
        "captured_at": datetime.now(UTC).isoformat(),
        "declared_environment": cfg.get("ENVIRONMENT", "unspecified"),
        "local_host": url.host in {"localhost", "127.0.0.1", "::1"},
        "mode": "read_only",
        "tables": {},
    }
    connection = await asyncpg.connect(dsn, timeout=15)
    try:
        async with connection.transaction(isolation="repeatable_read", readonly=True):
            await connection.execute("SET LOCAL statement_timeout = '30s'")
            report["server_version"] = await connection.fetchval("SHOW server_version")
            names = {
                r["table_name"]
                for r in await connection.fetch(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
                )
            }
            for name in CATALOG_TABLES:
                if name not in names:
                    continue
                report["tables"][name] = {
                    "count": await connection.fetchval(f'SELECT count(*) FROM "{name}"'),
                    "columns": [
                        dict(r)
                        for r in await connection.fetch(
                            "SELECT column_name, data_type, is_nullable "
                            "FROM information_schema.columns "
                            "WHERE table_schema='public' AND table_name=$1 "
                            "ORDER BY ordinal_position",
                            name,
                        )
                    ],
                }
            report["constraints"] = [
                dict(r)
                for r in await connection.fetch(
                    "SELECT conrelid::regclass::text AS table_name, conname, "
                    "pg_get_constraintdef(oid) AS definition FROM pg_constraint "
                    "WHERE connamespace='public'::regnamespace ORDER BY 1,2"
                )
            ]
            report["indexes"] = [
                dict(r)
                for r in await connection.fetch(
                    "SELECT tablename,indexname,indexdef FROM pg_indexes "
                    "WHERE schemaname='public' AND tablename=ANY($1::text[]) ORDER BY 1,2",
                    list(CATALOG_TABLES),
                )
            ]
            report["triggers"] = [
                dict(r)
                for r in await connection.fetch(
                    "SELECT event_object_table,trigger_name FROM information_schema.triggers "
                    "WHERE trigger_schema='public' ORDER BY 1,2"
                )
            ]
            report["database_revision"] = await connection.fetchval(
                "SELECT version_num FROM alembic_version"
            )
            report["institutions"] = [
                dict(r)
                for r in await connection.fetch(
                    "SELECT university_id,university_name,city,state,website FROM universities "
                    "WHERE university_name IN ('Northern New Mexico College', "
                    "'New Mexico Institute of Mining and Technology','New Mexico Tech') "
                    "OR website ~ '^https?://(www[.])?nmt[.]edu/?$' ORDER BY university_name"
                )
            ]
            nmt_ids = [
                r["university_id"]
                for r in report["institutions"]
                if "nmt.edu" in (r["website"] or "")
            ]
            report["existing_nmt_programs"] = [
                dict(r)
                for r in await connection.fetch(
                    "SELECT p.program_id,p.university_id,p.program_name,"
                    "p.degree,p.total_credit_hours, "
                    "to_jsonb(p)->>'official_source_id' AS official_source_id, "
                    "to_jsonb(p)->>'official_source_url' AS official_source_url, "
                    "to_jsonb(p)->'metadata_json' AS metadata_json "
                    "FROM programs p WHERE university_id=ANY($1::uuid[]) "
                    "ORDER BY program_name,degree",
                    nmt_ids,
                )
            ]
            report["integrity"] = {}
            queries = {
                "duplicate_course_code_groups_within_program": (
                    "SELECT count(*) FROM (SELECT program_id,course_code FROM courses "
                    "GROUP BY 1,2 HAVING count(*)>1) d"
                ),
                "orphan_courses": "SELECT count(*) FROM courses c LEFT JOIN programs p "
                "ON c.program_id=p.program_id WHERE p.program_id IS NULL",
                "orphan_programs": "SELECT count(*) FROM programs p LEFT JOIN universities u "
                "ON p.university_id=u.university_id WHERE u.university_id IS NULL",
                "blank_course_titles": "SELECT count(*) FROM courses WHERE "
                "btrim(course_name)='' OR lower(btrim(course_name)) "
                "IN ('undefined','untitled course set')",
                "cross_institution_prerequisite_links": (
                    "SELECT count(*) FROM course_prerequisites r JOIN courses a "
                    "ON a.course_id=r.course_id JOIN courses b "
                    "ON b.course_id=r.prerequisite_course_id "
                    "JOIN programs p ON p.program_id=a.program_id JOIN programs q "
                    "ON q.program_id=b.program_id WHERE p.university_id<>q.university_id"
                ),
            }
            for key, query in queries.items():
                report["integrity"][key] = await connection.fetchval(query)
            # Only aggregate checksums leave the DB; no saved-plan contents or user identities.
            report["protected_fingerprints"] = {}
            for table, order in (
                ("education_plans", "id"),
                ("ed_plans", "plan_id"),
                ("plan_courses", "id"),
            ):
                report["protected_fingerprints"][table] = await connection.fetchval(
                    "SELECT md5(coalesce(string_agg(md5(to_jsonb(t)::text),'' "
                    f"ORDER BY {order}),'')) "
                    f'FROM "{table}" t'
                )
            for table, query in {
                "nnmc_programs": "SELECT p.* FROM programs p JOIN universities u "
                "ON p.university_id=u.university_id "
                "WHERE u.university_name='Northern New Mexico College'",
                "nnmc_courses": "SELECT c.* FROM courses c JOIN programs p "
                "ON c.program_id=p.program_id JOIN universities u "
                "ON p.university_id=u.university_id "
                "WHERE u.university_name='Northern New Mexico College'",
            }.items():
                report["protected_fingerprints"][table] = await connection.fetchval(
                    "SELECT md5(coalesce(string_agg(h,'' ORDER BY h),'')) FROM "
                    f"(SELECT md5(to_jsonb(t)::text) h FROM ({query}) t) x"
                )
    finally:
        await connection.close()
    report["local_migration_revisions"] = sorted(
        p.name.split("_", 1)[0] for p in (env_path.parent / "alembic" / "versions").glob("*.py")
    )
    report["schema_history_aligned"] = (
        report["database_revision"] in report["local_migration_revisions"]
    )
    return report


def save_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
