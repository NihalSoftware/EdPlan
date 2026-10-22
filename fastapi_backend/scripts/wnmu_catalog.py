"""Offline, append-only WNMU department import and academic-inventory review staging.

Intentionally NOT an academic publisher: the index has no complete credit/rule data.
No network requests, schema migrations, program/course mutations or deletions.
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
from urllib.parse import parse_qs, urlsplit

import asyncpg
from dotenv import dotenv_values
from sqlalchemy.engine import make_url

from scripts.nmt_catalog.baseline import save_json
from scripts.nmt_catalog.database_staging import protected_fingerprints
from scripts.nmt_catalog.normalize import canonical_hash

UNIVERSITY_ID = uuid.UUID("a98d490e-bd5e-4ba9-973a-e5ea7ad53ed5")
INDEX = "https://catalog.wnmu.edu/content.php?catoid=8&navoid=612"
FIXTURE = Path(__file__).parents[1] / "tests/scripts/fixtures/wnmu/catalog-index.json"
OUTPUT = Path("artifacts/wnmu/catalog-8")


def approved_source(url):
    p = urlsplit(url)
    if p.scheme != "https" or p.netloc != "catalog.wnmu.edu" or p.username or p.password:
        raise ValueError("Unapproved WNMU catalog origin")
    q = parse_qs(p.query, keep_blank_values=True)
    valid_index = p.path == "/content.php" and q == {"catoid": ["8"], "navoid": ["612"]}
    valid_program = (
        p.path == "/preview_program.php"
        and set(q) == {"catoid", "poid", "returnto"}
        and q["catoid"] == ["8"]
        and q["returnto"] == ["612"]
        and len(q["poid"]) == 1
        and re.fullmatch(r"[0-9]+", q["poid"][0])
    )
    if not (valid_index or valid_program) or (
        p.fragment and not re.fullmatch(r"ent[0-9]+", p.fragment)
    ):
        raise ValueError("Unapproved catalog path, version, query or fragment")
    return url


def build_stage(snapshot_path=FIXTURE):
    raw = snapshot_path.read_bytes()
    capture = json.loads(raw)
    if (
        capture["catalog"] != "2025-2026 Catalog"
        or capture["source_url"] != INDEX
        or capture["capture_method"] != "visible_public_browser_dom_projection"
        or capture["all_links_conform_to_template"] is not True
    ):
        raise ValueError("Unexpected source snapshot")
    retrieved = datetime.fromisoformat(capture["retrieved_at"])
    if retrieved.tzinfo is None:
        raise ValueError("Source timestamp must include a timezone")
    source = {
        "url": approved_source(capture["source_url"]),
        "retrieved_at": retrieved.isoformat(),
        "snapshot_sha256": hashlib.sha256(raw).hexdigest(),
        "capture_method": capture["capture_method"],
        "coverage": "program_index_only_not_complete_academic_catalog",
    }
    departments, programs, units = [], [], []
    unit_ids, program_ids = set(), set()

    def add_program(poid, title, category, parent):
        if (
            not re.fullmatch(r"[0-9]+", poid)
            or poid in program_ids
            or not title.strip()
            or title != title.strip()
            or not category.strip()
        ):
            raise ValueError("Duplicate or invalid official program identity/title")
        program_ids.add(poid)
        url = approved_source(capture["link_template"].format(poid=poid))
        programs.append(
            {
                "official_source_id": f"catoid=8:poid={poid}",
                "official_name": title,
                "official_category": category,
                "academic_unit_source_id": parent,
                "official_source_url": url,
                "index_source_url": INDEX,
                "total_credit_hours": None,
                "duration": None,
                "eligibility": None,
                "capacity": None,
                "officially_active": None,
                "review_reasons": [
                    "program_details_and_rules_not_fully_retrieved",
                    "not_ready_for_education_planner",
                ],
                "catalog_wording": "pending_approval" if "(Pending Approval)" in title else None,
            }
        )

    for entity, name, categories in capture["units"]:
        if (
            entity in unit_ids
            or not re.fullmatch(r"ent[0-9]+", entity)
            or not name.strip()
            or name != name.strip()
        ):
            raise ValueError("Duplicate or invalid academic unit")
        unit_ids.add(entity)
        identity = "catoid=8:" + entity
        unit = {
            "official_source_id": identity,
            "official_name": name,
            "official_source_url": approved_source(INDEX + "#" + entity),
        }
        units.append(unit)
        # A college and an administrative office are not mislabeled as departments.
        if name.startswith(("Department of ", "School of ")):
            departments.append(unit)
        for category, entries in categories:
            for poid, title in entries:
                add_program(poid, title, category, identity)
    for poid, title in capture["universityPrograms"]:
        add_program(poid, title, "Other Programs", None)
    if (
        len(programs) != capture["observed_link_count"]
        or len(program_ids) != capture["observed_unique_program_ids"]
        or len(programs) != 234
        or len(units) != 14
        or len(departments) != 12
    ):
        raise ValueError("Snapshot completeness differs from the observed index")
    stage = {
        "institution_id": str(UNIVERSITY_ID),
        "catalog_year": "2025-2026",
        "catalog_id": "8",
        "source": source,
        "academic_units": units,
        "departments": sorted(departments, key=lambda r: r["official_source_id"]),
        "programs": sorted(programs, key=lambda r: r["official_source_id"]),
        "publication_complete": False,
        "publication_scope": "departments_only_program_inventory_review_only",
    }
    stage["stage_hash"] = canonical_hash(stage)
    return stage


def as_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


async def apply_review_stage(connection, stage, expected_hash):
    body = {k: v for k, v in stage.items() if k != "stage_hash"}
    if (
        canonical_hash(body) != expected_hash
        or stage["stage_hash"] != expected_hash
        or stage["institution_id"] != str(UNIVERSITY_ID)
        or stage["catalog_year"] != "2025-2026"
    ):
        raise ValueError("Stage checksum or institution mismatch")
    run_id = uuid.uuid5(UNIVERSITY_ID, "wnmu-index-review-v1:" + expected_hash)
    retrieved = datetime.fromisoformat(stage["source"]["retrieved_at"])
    async with connection.transaction(isolation="serializable"):
        await connection.execute("SET LOCAL statement_timeout='30s'")
        await connection.execute("SET LOCAL lock_timeout='5s'")
        await connection.execute(
            "SELECT pg_advisory_xact_lock($1)",
            int.from_bytes(UNIVERSITY_ID.bytes[:8], "big", signed=True),
        )
        institutions = await connection.fetch(
            "SELECT university_id,university_name,city,state,website FROM universities "
            "WHERE university_id=$1 OR university_name='Western New Mexico University'",
            UNIVERSITY_ID,
        )
        if len(institutions) != 1 or dict(institutions[0]) != {
            "university_id": UNIVERSITY_ID,
            "university_name": "Western New Mexico University",
            "city": "Silver City",
            "state": "New Mexico",
            "website": "https://wnmu.edu",
        }:
            raise ValueError("Reviewed WNMU target identity changed")
        before = await protected_fingerprints(connection)
        previous = await connection.fetchrow(
            "SELECT status,summary_json FROM catalog_import_runs WHERE import_run_id=$1", run_id
        )
        if previous:
            summary = json.loads(previous["summary_json"])
            count = await connection.fetchval(
                "SELECT count(*) FROM catalog_change_audit WHERE import_run_id=$1", run_id
            )
            if (
                previous["status"] != "completed"
                or summary.get("stage_hash") != expected_hash
                or count != len(stage["departments"]) + len(stage["programs"])
            ):
                raise ValueError("Conflicting or incomplete existing run ledger")
            return {
                "import_run_id": str(run_id),
                "already_applied": True,
                "departments_inserted_this_run": 0,
                "review_records_inserted_this_run": 0,
                "summary": summary,
            }
        await connection.execute(
            "INSERT INTO catalog_import_runs (import_run_id,university_id,catalog_name,"
            "source_root_url,mode,status,retrieved_at,started_at,summary_json,error_json) "
            "VALUES ($1,$2,$3,$4,'apply','running',$5,$6,'{}'::jsonb,'{}'::jsonb)",
            run_id,
            UNIVERSITY_ID,
            "WNMU 2025-2026 departments and program inventory review",
            INDEX,
            retrieved,
            datetime.now(UTC),
        )

        async def audit(key, table, record_id, action, old, proposed, source, method, confidence):
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
                as_json(old),
                as_json(proposed),
                approved_source(source),
                method,
                confidence,
                "Index evidence only. No existing values overwritten. Academic records remain "
                "review-only; unknown credits/rules/status are never invented.",
                datetime.now(UTC),
                datetime.now(UTC) if action == "insert" else None,
            )

        inserted, conflicts = 0, 0
        for department in stage["departments"]:
            identity = department["official_source_id"]
            # Stable scoped ID first, exact source URL second. Exact name is review-only.
            matches = await connection.fetch(
                "SELECT * FROM catalog_departments WHERE university_id=$1 AND "
                "(official_source_id=$2 OR official_source_url=$3 OR department_name=$4)",
                UNIVERSITY_ID,
                identity,
                department["official_source_url"],
                department["official_name"],
            )
            proposed = {
                **department,
                "catalog_year": stage["catalog_year"],
                "university_id": str(UNIVERSITY_ID),
                "department_id": str(uuid.uuid5(UNIVERSITY_ID, "wnmu:" + identity)),
                "department_name": department["official_name"],
                "source_retrieved_at": retrieved.isoformat(),
                "officially_active": None,
                "active_evidence_url": None,
                "source_evidence": stage["source"],
            }
            if matches:
                row = matches[0] if len(matches) == 1 else None
                exact = row and row["official_source_id"] == identity
                unchanged = exact and row["department_name"] == department["official_name"]
                action = "no_change" if unchanged else "review"
                conflicts += not unchanged
                await audit(
                    "department:" + identity,
                    "catalog_departments",
                    row["department_id"] if row else None,
                    action,
                    [dict(r) for r in matches],
                    proposed,
                    department["official_source_url"],
                    "scoped_official_entity_id" if exact else "name_or_source_review",
                    "high" if unchanged else "low",
                )
                continue
            record_id = uuid.uuid5(UNIVERSITY_ID, "wnmu:" + identity)
            await connection.execute(
                "INSERT INTO catalog_departments (department_id,university_id,"
                "official_source_id,department_name,official_source_url,source_retrieved_at) "
                "VALUES ($1,$2,$3,$4,$5,$6)",
                record_id,
                UNIVERSITY_ID,
                identity,
                department["official_name"],
                department["official_source_url"],
                retrieved,
            )
            inserted += 1
            await audit(
                "department:" + identity,
                "catalog_departments",
                record_id,
                "insert",
                {},
                proposed,
                department["official_source_url"],
                "scoped_official_entity_id",
                "high",
            )
        for program in stage["programs"]:
            await audit(
                "program:" + program["official_source_id"],
                "programs",
                None,
                "review",
                {},
                {
                    "record": program,
                    "source_evidence": stage["source"],
                    "institution_id": str(UNIVERSITY_ID),
                    "catalog_year": stage["catalog_year"],
                    "publication_status": "review_only_not_published",
                },
                program["official_source_url"],
                "official_index_identity_only",
                "low",
            )
        after = await protected_fingerprints(connection)
        if before != after:
            raise ValueError("Academic or student data changed; rolling back")
        summary = {
            "stage_hash": expected_hash,
            "departments_inserted": inserted,
            "departments_awaiting_review": conflicts,
            "program_review_records": len(stage["programs"]),
            "academic_rows_inserted": 0,
            "academic_rows_updated": 0,
            "protected_tables_unchanged": True,
            "protected_fingerprints": before,
            "publication_complete": False,
            "publication_scope": stage["publication_scope"],
            "catalog_year": stage["catalog_year"],
        }
        await connection.execute(
            "UPDATE catalog_import_runs SET status='completed',completed_at=$2,"
            "summary_json=$3::jsonb WHERE import_run_id=$1",
            run_id,
            datetime.now(UTC),
            as_json(summary),
        )
    return {
        "import_run_id": str(run_id),
        "already_applied": False,
        "departments_inserted_this_run": inserted,
        "review_records_inserted_this_run": len(stage["programs"]),
        "summary": summary,
    }


async def run(args):
    stage = build_stage(args.snapshot)
    save_json(args.output / "staged-catalog.json", stage)
    if not args.apply_departments_and_review_only:
        print(
            as_json(
                {
                    "stage_hash": stage["stage_hash"],
                    "departments": len(stage["departments"]),
                    "program_inventory": len(stage["programs"]),
                    "academic_publication": False,
                }
            )
        )
        return
    if not args.expected_stage_hash or args.expected_stage_hash != stage["stage_hash"]:
        raise ValueError("Explicit reviewed --expected-stage-hash required to apply")
    config = {**dotenv_values(".env"), **os.environ}
    url = make_url(config["DATABASE_URL"])
    connection = await asyncpg.connect(
        url.set(drivername="postgresql").render_as_string(hide_password=False), timeout=15
    )
    try:
        report = await apply_review_stage(connection, stage, args.expected_stage_hash)
    finally:
        await connection.close()
    name = (
        "database-repeat-report.json" if report["already_applied"] else "database-apply-report.json"
    )
    save_json(args.output / name, report)
    print(as_json({k: v for k, v in report.items() if k != "summary"}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=FIXTURE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--expected-stage-hash")
    parser.add_argument("--apply-departments-and-review-only", action="store_true")
    asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    main()
