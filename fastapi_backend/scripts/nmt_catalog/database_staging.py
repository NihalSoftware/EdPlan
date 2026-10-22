"""Insert official departments and REVIEW-ONLY academic evidence into existing audit tables.

Never inserts, updates, deletes, or republishes programs, courses, rules or student plans.
No DDL, schema stamping, or migration is performed against the target database.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

from .normalize import COURSE_CODE, canonical_hash, valid_name
from .sources import ORIGIN, PageParser, PublicCatalogClient, approved_url, decode_nuxt

PROTECTED_TABLES = (
    "programs",
    "courses",
    "course_prerequisites",
    "course_corequisites",
    "education_plans",
    "ed_plans",
    "plan_courses",
    "program_departments",
    "course_departments",
)


def validated_stage(folder: Path, expected_hash: str):
    stage = json.loads((folder / "staged-catalog.json").read_text(encoding="utf-8"))
    stored_hash = stage.pop("stage_hash")
    if canonical_hash(stage) != stored_hash or stored_hash != expected_hash:
        raise ValueError("Staging checksum mismatch; regenerate and review the dry run")
    stage["stage_hash"] = stored_hash
    if stage["catalog_year"] != "2026-2027":
        raise ValueError("Unsupported catalog version")
    if stage["institution"]["official_name"] != "New Mexico Institute of Mining and Technology":
        raise ValueError("Institution mismatch")
    client = PublicCatalogClient(folder / "cache", offline=True)
    try:
        html, index_source = client.fetch(ORIGIN + "/departments")
        decoded = decode_nuxt(PageParser(html).nuxt)
        settings = decoded.get("pinia", {}).get("settings", {})
        if stage["catalog_year"] not in str(settings.get("catalogDisplayName", "")):
            raise ValueError("Department evidence belongs to another catalog")
        official = {d["id"]: d for d in decoded["pinia"]["departments"]["all"]}
        codes = set()
        for department in stage["departments"]:
            code = department["code"]
            if (
                code in codes
                or department["institution"] != "NMT"
                or department["catalog_year"] != stage["catalog_year"]
                or not valid_name(department["name"])
                or code not in official
                or official[code]["name"] != department["name"]
            ):
                raise ValueError("Department identity or official name mismatch")
            codes.add(code)
        if not codes:
            raise ValueError("Empty department inventory")
        identities = set()
        for record in stage["programs"] + stage["courses"]:
            key = (record["kind"], record["external_id"])
            if (
                key in identities
                or record["institution"] != "NMT"
                or record["catalog_year"] != stage["catalog_year"]
                or not valid_name(record["title"])
                or not record["code"]
            ):
                raise ValueError("Academic staging identity mismatch")
            identities.add(key)
            if record["kind"] == "course" and not COURSE_CODE.fullmatch(record["code"]):
                raise ValueError("Invalid official course code")
            _, source = client.fetch(approved_url(record["source"]["url"]))
            if source["sha256"] != record["source"]["sha256"]:
                raise ValueError("Academic source checksum mismatch")
        return stage, index_source
    finally:
        client.close()


async def protected_fingerprints(connection):
    result = {}
    for table in PROTECTED_TABLES:
        # Table names are fixed constants, never user-controlled identifiers.
        result[table] = await connection.fetchval(
            "SELECT md5(coalesce(string_agg(h,'' ORDER BY h),'')) "
            f'FROM (SELECT md5(to_jsonb(t)::text) h FROM "{table}" t) x'
        )
    return result


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


async def apply_staging(connection, stage, index_source, expected_university_id):
    """One atomic, idempotent append-only operation. Caller owns connection lifetime."""
    university_id = uuid.UUID(str(expected_university_id))
    run_id = uuid.uuid5(university_id, "nmt-review-staging-v1:" + stage["stage_hash"])
    now = datetime.now(UTC)
    retrieved = datetime.fromisoformat(index_source["retrieved_at"])
    async with connection.transaction(isolation="serializable"):
        await connection.execute("SET LOCAL statement_timeout='30s'")
        await connection.execute("SET LOCAL lock_timeout='5s'")
        lock = int.from_bytes(hashlib.sha256(university_id.bytes).digest()[:8], "big", signed=True)
        await connection.execute("SELECT pg_advisory_xact_lock($1)", lock)
        institutions = await connection.fetch(
            "SELECT university_id,university_name,city,state,website FROM universities "
            "WHERE university_id=$1 OR university_name="
            "'New Mexico Institute of Mining and Technology'",
            university_id,
        )
        if len(institutions) != 1 or institutions[0]["university_id"] != university_id:
            raise ValueError("NMT is missing, duplicated, or not the approved institution ID")
        institution = institutions[0]
        if (
            institution["university_name"] != "New Mexico Institute of Mining and Technology"
            or institution["city"] != "Socorro"
            or institution["state"] not in {"New Mexico", "NM"}
            or (institution["website"] or "").rstrip("/")
            not in {"https://www.nmt.edu", "https://nmt.edu"}
        ):
            raise ValueError("NMT institutional identity differs from the reviewed target")
        before = await protected_fingerprints(connection)
        existing_run = await connection.fetchrow(
            "SELECT status,summary_json FROM catalog_import_runs WHERE import_run_id=$1", run_id
        )
        if existing_run:
            summary = json.loads(existing_run["summary_json"])
            expected_audits = (
                len(stage["departments"]) + len(stage["programs"]) + len(stage["courses"])
            )
            actual_audits = await connection.fetchval(
                "SELECT count(*) FROM catalog_change_audit WHERE import_run_id=$1", run_id
            )
            if (
                existing_run["status"] != "completed"
                or summary.get("stage_hash") != stage["stage_hash"]
                or actual_audits != expected_audits
            ):
                raise ValueError(
                    "Existing import ledger is incomplete or conflicts with this stage"
                )
            return {
                "import_run_id": str(run_id),
                "already_applied": True,
                "departments_inserted_this_run": 0,
                "review_records_inserted_this_run": 0,
                "summary": summary,
                "protected_tables_unchanged": True,
            }
        await connection.execute(
            "INSERT INTO catalog_import_runs (import_run_id,university_id,catalog_name,"
            "source_root_url,mode,status,retrieved_at,started_at,summary_json,error_json) "
            "VALUES ($1,$2,$3,$4,'apply','running',$5,$6,$7::jsonb,'{}'::jsonb)",
            run_id,
            university_id,
            "NMT 2026-2027 departments and review-only evidence",
            ORIGIN + "/",
            retrieved,
            now,
            _json({"stage_hash": stage["stage_hash"], "publication_complete": False}),
        )
        inserted, unchanged, department_reviews = 0, 0, 0

        async def audit(
            key,
            table,
            record_id,
            action,
            old,
            proposed,
            source_url,
            method,
            confidence,
            notes,
            applied,
        ):
            await connection.execute(
                "INSERT INTO catalog_change_audit (audit_id,import_run_id,table_name,record_id,"
                "action,old_values,proposed_new_values,source_url,match_method,confidence_level,"
                "notes,created_at,applied_at) "
                "VALUES ($1,$2,$3,$4,$5,$6::jsonb,$7::jsonb,$8,$9,$10,$11,$12,$13)",
                uuid.uuid5(run_id, key),
                run_id,
                table,
                record_id,
                action,
                _json(old),
                _json(proposed),
                approved_url(source_url),
                method,
                confidence,
                notes,
                now,
                now if applied else None,
            )

        for department in stage["departments"]:
            code = department["code"]
            proposed = {
                "department_id": uuid.uuid5(university_id, "nmt-official-department:" + code),
                "university_id": university_id,
                "official_source_id": code,
                "department_name": department["name"],
                "official_source_url": index_source["url"],
                "source_retrieved_at": retrieved,
                "officially_active": None,
                "active_evidence_url": None,
            }
            row = await connection.fetchrow(
                "INSERT INTO catalog_departments (department_id,university_id,official_source_id,"
                "department_name,official_source_url,source_retrieved_at) "
                "VALUES ($1,$2,$3,$4,$5,$6) "
                "ON CONFLICT (university_id,official_source_id) DO NOTHING RETURNING *",
                proposed["department_id"],
                university_id,
                code,
                department["name"],
                index_source["url"],
                retrieved,
            )
            if row:
                inserted += 1
                action, old, applied, confidence = "insert", {}, True, "high"
            else:
                row = await connection.fetchrow(
                    "SELECT * FROM catalog_departments "
                    "WHERE university_id=$1 AND official_source_id=$2",
                    university_id,
                    code,
                )
                if not row:
                    raise ValueError("Department upsert did not resolve its scoped identity")
                old = dict(row)
                action = "no_change" if row["department_name"] == department["name"] else "review"
                unchanged += action == "no_change"
                department_reviews += action == "review"
                applied, confidence = False, "high" if action == "no_change" else "low"
            await audit(
                "department:" + code,
                "catalog_departments",
                row["department_id"],
                action,
                old,
                {"row": proposed, "evidence": index_source, "catalog_year": stage["catalog_year"]},
                index_source["url"],
                "institution_scoped_official_department_code",
                confidence,
                "Existing values are never overwritten. Active status remains unknown.",
                applied,
            )
        for record in stage["programs"] + stage["courses"]:
            await audit(
                "review:" + record["kind"] + ":" + record["external_id"],
                "programs" if record["kind"] == "program" else "courses",
                None,
                "review",
                {},
                {
                    "catalog_year": stage["catalog_year"],
                    "institution_id": str(university_id),
                    "stage_hash": stage["stage_hash"],
                    "publication_status": "review_only_not_published",
                    "record": record,
                },
                record["source"]["url"],
                "official_source_evidence_only_legacy_match_unapproved",
                "low",
                "NOT inserted into academic tables. Rules, matches, catalog version and source "
                "conflicts require review. Must not be consumed as a published course/program.",
                False,
            )
        after = await protected_fingerprints(connection)
        if before != after:
            raise ValueError("Protected academic or student tables changed; rolling back")
        summary = {
            "stage_hash": stage["stage_hash"],
            "catalog_year": stage["catalog_year"],
            "publication_scope": "departments_only_academic_records_review_only",
            "publication_complete": False,
            "departments_inserted": inserted,
            "departments_unchanged": unchanged,
            "departments_awaiting_review": department_reviews,
            "program_review_records": len(stage["programs"]),
            "course_review_records": len(stage["courses"]),
            "academic_rows_inserted": 0,
            "academic_rows_updated": 0,
            "protected_tables_unchanged": True,
            "protected_fingerprints": before,
        }
        await connection.execute(
            "UPDATE catalog_import_runs SET status='completed',completed_at=$2,"
            "summary_json=$3::jsonb "
            "WHERE import_run_id=$1",
            run_id,
            datetime.now(UTC),
            _json(summary),
        )
    return {
        "import_run_id": str(run_id),
        "already_applied": False,
        "departments_inserted_this_run": inserted,
        "review_records_inserted_this_run": len(stage["programs"]) + len(stage["courses"]),
        "summary": summary,
        "protected_tables_unchanged": True,
    }
