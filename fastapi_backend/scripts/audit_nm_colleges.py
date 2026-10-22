"""Read-only public academic-data audit. Never reads student-plan/user row contents.

Only SELECT/SHOW and session-local read-only/time-limit settings are issued.
Reports are local artifacts; production application code is never imported.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlsplit

import asyncpg
from dotenv import dotenv_values
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "reports/nm-college-audit"
ACADEMIC_TABLES = (
    "universities",
    "programs",
    "courses",
    "course_prerequisites",
    "course_corequisites",
    "catalog_departments",
    "program_departments",
    "course_departments",
)
MAX_ROWS = 50000


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )


def normalized(value):
    text = unicodedata.normalize("NFKD", value or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def stored_source_url(row):
    """Recognize recorded JSON provenance without certifying the URL as authoritative."""
    metadata = row.get("metadata_json") or {}
    nested = metadata.get("source") or {}
    values = [
        row.get("official_source_url"),
        metadata.get("source_url"),
        metadata.get("catalog_url"),
        metadata.get("catalog_source"),
    ]
    if isinstance(nested, dict):
        values.extend([nested.get("resolved_url"), nested.get("url")])
    return next(
        (v for v in values if isinstance(v, str) and v.startswith(("https://", "http://"))), None
    )


def public_metadata(value):
    value = json.loads(value) if isinstance(value, str) else value
    if not isinstance(value, dict):
        return {}
    keys = {
        "catalog_year",
        "catalog_name",
        "prerequisite",
        "corequisite",
        "is_elective",
        "curriculum_roster_complete",
        "course_rules_verified",
        "course_rules_status",
        "requirement_section",
        "level_of_study",
        "credits_min",
        "credits_max",
        "credit_range",
        "requirements",
        "requirements_text",
        "source_url",
        "total_credit_hours",
        "catalog_total_credits_min",
        "catalog_total_credits_max",
        "catalog_total_credits_text",
        "catalog_url",
        "catalog_source",
        "source_retrieved_at",
        "source_pdf_pages",
        "source_printed_pages",
        "source_requirements_text",
        "requirement_choices",
        "prerequisite_corequisite_text",
        "course_import_is_partial",
        "planning_ready",
        "includes_laboratory",
        "source_credit_cell",
        "source_section",
        "is_current_catalog",
    }
    result = {k: v for k, v in value.items() if k in keys}
    source = value.get("source")
    if isinstance(source, dict):
        result["source"] = {
            k: v
            for k, v in source.items()
            if k
            in {"url", "resolved_url", "catalog_year", "retrieved_at", "sha256", "snapshot_sha256"}
        }
    result["_original_metadata_keys"] = sorted(value.keys())
    return result


async def collect(env_path):
    cfg = {**dotenv_values(env_path), **os.environ}
    setting = "READ_ONLY_DATABASE_URL" if cfg.get("READ_ONLY_DATABASE_URL") else "DATABASE_URL"
    url = make_url(cfg[setting])
    snapshot = {
        "captured_at": datetime.now(UTC).isoformat(),
        "mode": "READ_ONLY",
        "connection_setting": setting,
        "declared_environment": cfg.get("ENVIRONMENT", "unspecified"),
        "target_class": "local"
        if url.host in {"localhost", "127.0.0.1", "::1"}
        else "remote_environment_unconfirmed",
        "student_row_contents_accessed": False,
        "tables": {},
        "rows": {},
    }
    connection = await asyncpg.connect(
        url.set(drivername="postgresql").render_as_string(hide_password=False),
        timeout=15,
        server_settings={
            "default_transaction_read_only": "on",
            "statement_timeout": "30000",
            "application_name": "edplan_nm_readonly_audit",
        },
    )
    try:
        async with connection.transaction(readonly=True, isolation="repeatable_read"):
            snapshot["transaction_read_only"] = await connection.fetchval(
                "SHOW transaction_read_only"
            )
            if snapshot["transaction_read_only"] != "on":
                raise RuntimeError("Refusing database audit without read-only enforcement")
            snapshot["server_version"] = await connection.fetchval("SHOW server_version")
            snapshot["role_has_write_privileges"] = await connection.fetchval(
                "SELECT has_table_privilege(current_user,'public.programs','INSERT,UPDATE,DELETE')"
            )
            snapshot["schema_tables"] = [
                r["table_name"]
                for r in await connection.fetch(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema='public' "
                    "ORDER BY table_name"
                )
            ]
            snapshot["columns"] = [
                dict(r)
                for r in await connection.fetch(
                    "SELECT table_name,column_name,data_type,is_nullable,column_default "
                    "FROM information_schema.columns WHERE table_schema='public' "
                    "AND table_name=ANY($1::text[]) ORDER BY table_name,ordinal_position",
                    list(ACADEMIC_TABLES)
                    + ["program_courses", "catalog_import_runs", "catalog_change_audit"],
                )
            ]
            snapshot["constraints"] = [
                dict(r)
                for r in await connection.fetch(
                    "SELECT conrelid::regclass::text table_name,conname,pg_get_constraintdef(oid) definition "
                    "FROM pg_constraint WHERE connamespace='public'::regnamespace "
                    "AND conrelid=ANY($1::regclass[]) ORDER BY 1,2",
                    list(ACADEMIC_TABLES),
                )
            ]
            snapshot["indexes"] = [
                dict(r)
                for r in await connection.fetch(
                    "SELECT tablename,indexname,indexdef FROM pg_indexes WHERE schemaname='public' "
                    "AND tablename=ANY($1::text[]) ORDER BY 1,2",
                    list(ACADEMIC_TABLES),
                )
            ]
            snapshot["triggers"] = [
                dict(r)
                for r in await connection.fetch(
                    "SELECT event_object_table,trigger_name FROM information_schema.triggers "
                    "WHERE trigger_schema='public' ORDER BY 1,2"
                )
            ]
            snapshot["database_revision"] = await connection.fetchval(
                "SELECT version_num FROM alembic_version"
            )
            queries = {
                "universities": "SELECT university_id,university_name,city,state,website FROM universities ORDER BY university_id",
                "programs": "SELECT * FROM programs ORDER BY program_id",
                "courses": "SELECT * FROM courses ORDER BY course_id",
                "course_prerequisites": "SELECT id,course_id,prerequisite_course_id FROM course_prerequisites ORDER BY id",
                "course_corequisites": "SELECT id,course_id,corequisite_course_id FROM course_corequisites ORDER BY id",
                "catalog_departments": "SELECT * FROM catalog_departments ORDER BY department_id",
                "program_departments": "SELECT * FROM program_departments ORDER BY id",
                "course_departments": "SELECT * FROM course_departments ORDER BY id",
            }
            for table, query in queries.items():
                if table not in snapshot["schema_tables"]:
                    snapshot["tables"][table] = {"status": "ABSENT"}
                    snapshot["rows"][table] = []
                    continue
                # Table and ORDER BY identifiers above are fixed code constants.
                count = await connection.fetchval(f'SELECT count(*) FROM "{table}"')
                if count > MAX_ROWS:
                    raise ValueError("Bounded audit row cap exceeded for " + table)
                rows = [dict(r) for r in await connection.fetch(query)]
                for row in rows:
                    if "metadata_json" in row:
                        row["metadata_json"] = public_metadata(row["metadata_json"])
                snapshot["tables"][table] = {
                    "count": count,
                    "complete_row_inventory": len(rows) == count,
                }
                snapshot["rows"][table] = rows
            snapshot["transaction_read_only_at_end"] = await connection.fetchval(
                "SHOW transaction_read_only"
            )
    finally:
        await connection.close()
    snapshot["local_migration_revisions"] = sorted(
        p.name.split("_", 1)[0] for p in (env_path.parent / "alembic/versions").glob("*.py")
    )
    snapshot["schema_history_aligned"] = (
        snapshot["database_revision"] in snapshot["local_migration_revisions"]
    )
    # UUID/Decimal/timestamp values become stable printable representations in the artifact.
    return json.loads(json.dumps(snapshot, default=str))


def reconcile(directory, rows):
    output, assigned = [], set()
    for institution in directory:
        names = {normalized(n) for n in [institution["name"], *institution.get("aliases", [])]}
        parent, related = [], []
        for row in rows:
            name = normalized(row["university_name"])
            host = (urlsplit(row.get("website") or "").hostname or "").removeprefix("www.")
            if name in names:
                parent.append(row)
            elif any(
                host == domain or host.endswith("." + domain) for domain in institution["domains"]
            ):
                # Never let a branch/center with a similar name satisfy a missing parent.
                related.append(row)
        status = (
            "MISSING_IN_DB"
            if not parent
            else ("POSSIBLE_DUPLICATE" if len(parent) > 1 else "VERIFIED")
        )
        if (
            institution["key"] == "sipi"
            and len(parent) == 1
            and normalized(parent[0]["university_name"]) != normalized(institution["name"])
        ):
            status = "MISMATCH"
        assigned.update(r["university_id"] for r in parent + related)
        output.append(
            {**institution, "parents": parent, "related": related, "institution_status": status}
        )
    return output, [r for r in rows if r["university_id"] not in assigned]


def academic_stats(snapshot, institution):
    ids = {r["university_id"] for r in institution["parents"]}
    programs = [p for p in snapshot["rows"]["programs"] if p["university_id"] in ids]
    pids = {p["program_id"] for p in programs}
    courses = [c for c in snapshot["rows"]["courses"] if c["program_id"] in pids]
    cids = {c["course_id"] for c in courses}
    stats = {
        "programs": len(programs),
        "courses": len(courses),
        "unique_course_codes": len({normalized(c["course_code"]) for c in courses}),
        "programs_without_courses": sum(
            not any(c["program_id"] == p["program_id"] for c in courses) for p in programs
        ),
        "programs_with_source_url": sum(bool(p.get("official_source_url")) for p in programs),
        "courses_with_source_url": sum(bool(c.get("official_source_url")) for c in courses),
        "program_catalog_years": dict(
            Counter(str(p["metadata_json"].get("catalog_year") or "UNSPECIFIED") for p in programs)
        ),
        "course_catalog_years": dict(
            Counter(str(c["metadata_json"].get("catalog_year") or "UNSPECIFIED") for c in courses)
        ),
    }
    for table, name in (
        ("course_prerequisites", "prerequisites"),
        ("course_corequisites", "corequisites"),
    ):
        stats[name] = sum(r["course_id"] in cids for r in snapshot["rows"][table])
    return stats, programs, courses


def csv_write(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            serialized = {
                k: json.dumps(v, ensure_ascii=False, sort_keys=True)
                if isinstance(v, (list, dict))
                else v
                for k, v in row.items()
            }
            # Protect spreadsheet readers; raw evidence remains unchanged in JSON.
            writer.writerow(
                {
                    k: "'" + v
                    if isinstance(v, str) and v.lstrip().startswith(("=", "+", "-", "@"))
                    else v
                    for k, v in serialized.items()
                }
            )


def write_reports(snapshot, directory, sources, output):
    institutions, unassigned = reconcile(directory, snapshot["rows"]["universities"])
    save_json(output / "institution-reconciliation.json", institutions)
    save_json(output / "source-evidence.json", sources)
    programs_by_id = {r["program_id"]: r for r in snapshot["rows"]["programs"]}
    courses_by_id = {r["course_id"]: r for r in snapshot["rows"]["courses"]}
    owner = {
        p["program_id"]: i["key"]
        for i in institutions
        for p in snapshot["rows"]["programs"]
        if p["university_id"] in {r["university_id"] for r in i["parents"]}
    }
    program_diffs, course_diffs, dependency_diffs = [], [], []
    matrix, rows, extras = [], [], []
    for item in institutions:
        key = item["key"]
        source = sources[key]
        stats, programs, courses = academic_stats(snapshot, item)
        item["stats"] = stats
        notes = []
        if item["related"]:
            notes.append("Related campus/center rows are separate and not counted as parents.")
        if item["institution_status"] == "MISSING_IN_DB":
            notes.append("No appropriate parent record; branch rows cannot satisfy the parent.")
        if len(item["parents"]) > 1:
            notes.append(
                "Multiple parent candidates; aggregate counts are not unique-parent coverage."
            )
        if stats["programs_without_courses"]:
            notes.append(
                str(stats["programs_without_courses"]) + " programs have no linked catalog courses."
            )
        ids = [r["university_id"] for r in item["parents"]]
        for p in programs:
            linked = [c for c in courses if c["program_id"] == p["program_id"]]
            if not linked:
                program_diffs.append(
                    {
                        "institution_key": key,
                        "catalog_year": p["metadata_json"].get("catalog_year", "UNSPECIFIED"),
                        "program_name": p["program_name"],
                        "credential": p["degree"],
                        "db_id": p["program_id"],
                        "issue": "NO_LINKED_CATALOG_COURSES",
                        "db_value": 0,
                        "catalog_value": "not_enumerated; not a source count",
                        "source_url": p.get("official_source_url") or source["resolved_url"],
                        "source_location": "Database relationship check only",
                        "review_status": "PARTIAL",
                    }
                )
        for p in programs:
            if not stored_source_url(p) or not p["metadata_json"].get("catalog_year"):
                program_diffs.append(
                    {
                        "institution_key": key,
                        "catalog_year": p["metadata_json"].get("catalog_year", "UNSPECIFIED"),
                        "program_name": p["program_name"],
                        "credential": p["degree"],
                        "db_id": p["program_id"],
                        "issue": "SOURCE_OR_CATALOG_YEAR_UNRECORDED",
                        "db_value": {
                            "source_url": stored_source_url(p),
                            "catalog_year": p["metadata_json"].get("catalog_year"),
                        },
                        "catalog_value": source["catalog_year"],
                        "source_url": source["resolved_url"],
                        "source_location": source["location"],
                        "review_status": "SOURCE_UNVERIFIED",
                    }
                )
        grouped = defaultdict(list)
        for c in courses:
            grouped[(c["program_id"], "".join(c["course_code"].split()).upper())].append(c)
            if not stored_source_url(c) or not c["metadata_json"].get("catalog_year"):
                course_diffs.append(
                    {
                        "institution_key": key,
                        "catalog_year": c["metadata_json"].get("catalog_year", "UNSPECIFIED"),
                        "course_code": c["course_code"],
                        "db_id": c["course_id"],
                        "issue": "SOURCE_OR_CATALOG_YEAR_UNRECORDED",
                        "db_value": {
                            "source_url": stored_source_url(c),
                            "catalog_year": c["metadata_json"].get("catalog_year"),
                        },
                        "catalog_value": source["catalog_year"],
                        "source_url": source["resolved_url"],
                        "source_location": source["location"],
                        "review_status": "SOURCE_UNVERIFIED",
                    }
                )
        for (_, code), duplicates in grouped.items():
            if len(duplicates) > 1:
                course_diffs.append(
                    {
                        "institution_key": key,
                        "catalog_year": "check_individual_rows",
                        "course_code": code,
                        "db_id": [c["course_id"] for c in duplicates],
                        "issue": "POSSIBLE_DUPLICATE_WITHIN_PROGRAM_CODE",
                        "db_value": {
                            "rows": len(duplicates),
                            "titles": [c["course_name"] for c in duplicates],
                            "credits": [c["credits"] for c in duplicates],
                        },
                        "catalog_value": "needs catalog-version/elective review; not automatic duplicate deletion",
                        "source_url": source["resolved_url"],
                        "source_location": "Database identity scope",
                        "review_status": "POSSIBLE_DUPLICATE",
                    }
                )
        for related in item["related"]:
            extras.append(
                {
                    "institution_key": key,
                    **related,
                    "classification": "DINE_CENTER_NOT_PARENT"
                    if key == "dine"
                    else "EXCLUDED_BRANCH_NOT_PARENT",
                }
            )
        for parent in item["parents"]:
            if normalized(parent["university_name"]) != normalized(item["name"]):
                notes.append(
                    "Stored name differs from canonical directory name; see identity report."
                )
        overall = (
            item["institution_status"] if item["institution_status"] != "VERIFIED" else "PARTIAL"
        )
        rows.append(
            {
                "key": key,
                "name": item["name"],
                "db_id": ";".join(ids),
                "category": item["category"],
                "catalog_year": source["catalog_year"],
                "catalog_url": source["resolved_url"],
                "institution_status": item["institution_status"],
                "programs_in_db": stats["programs"],
                "courses_in_db": stats["courses"],
                "prerequisites_in_db": stats["prerequisites"],
                "corequisites_in_db": stats["corequisites"],
                "verification_status": overall,
                "source_status": source["status"],
                "notes": " ".join(notes) + " Full curriculum verification not complete.",
            }
        )
        matrix.append(
            f"| {key} | {item['institution_status']} | {stats['programs']} | {stats['courses']} "
            f"| {stats['prerequisites']}/{stats['corequisites']} | {source['catalog_year']} | {overall} |"
        )
    # Dependency integrity is DB-verifiable without claiming catalog-rule correctness.
    for table, field, kind in (
        ("course_prerequisites", "prerequisite_course_id", "prerequisite"),
        ("course_corequisites", "corequisite_course_id", "corequisite"),
    ):
        groups = defaultdict(list)
        for edge in snapshot["rows"][table]:
            a, b = courses_by_id.get(edge["course_id"]), courses_by_id.get(edge[field])
            key = owner.get(a["program_id"], "out_of_scope") if a else "orphan"
            groups[(edge["course_id"], edge[field])].append(edge)
            issue = (
                "DANGLING_DEPENDENCY"
                if not a or not b
                else ("SELF_DEPENDENCY" if a["course_id"] == b["course_id"] else None)
            )
            if (
                a
                and b
                and programs_by_id.get(a["program_id"], {}).get("university_id")
                != programs_by_id.get(b["program_id"], {}).get("university_id")
            ):
                issue = "CROSS_INSTITUTION_DEPENDENCY"
            if issue:
                dependency_diffs.append(
                    {
                        "institution_key": key,
                        "catalog_year": "UNSPECIFIED",
                        "db_table": table,
                        "db_record_id": edge["id"],
                        "course_code": a["course_code"] if a else edge["course_id"],
                        "dependency_type": kind,
                        "dependency_course": b["course_code"] if b else edge[field],
                        "issue": issue,
                        "db_value": edge,
                        "catalog_value": "not_catalog_verified",
                        "source_url": "",
                        "source_location": "Database relationship integrity",
                        "review_status": "MISMATCH",
                    }
                )
        for (aid, bid), values in groups.items():
            if len(values) > 1:
                a, b = courses_by_id.get(aid), courses_by_id.get(bid)
                dependency_diffs.append(
                    {
                        "institution_key": owner.get(a["program_id"], "out_of_scope")
                        if a
                        else "orphan",
                        "db_table": table,
                        "db_record_id": [r["id"] for r in values],
                        "catalog_year": "UNSPECIFIED",
                        "course_code": a["course_code"] if a else aid,
                        "dependency_type": kind,
                        "dependency_course": b["course_code"] if b else bid,
                        "issue": "DUPLICATE_DEPENDENCY_EDGE",
                        "db_value": len(values),
                        "catalog_value": "review duplicate relationship IDs",
                        "source_url": "",
                        "source_location": "Database edge identity",
                        "review_status": "POSSIBLE_DUPLICATE",
                    }
                )
    for item in institutions:
        for c in snapshot["rows"]["courses"]:
            if owner.get(c["program_id"]) != item["key"]:
                continue
            metadata = c["metadata_json"]
            for field, kind in (("prerequisite", "prerequisite"), ("corequisite", "corequisite")):
                narrative = metadata.get(field)
                if isinstance(narrative, str) and re.search(
                    r"\bor\b|permission|placement|grade|standing|concurrent", narrative, re.I
                ):
                    dependency_diffs.append(
                        {
                            "institution_key": item["key"],
                            "catalog_year": metadata.get("catalog_year", "UNSPECIFIED"),
                            "course_code": c["course_code"],
                            "dependency_type": kind,
                            "dependency_course": "narrative_condition",
                            "issue": "COMPLEX_NARRATIVE_REQUIRES_RULE_REVIEW",
                            "db_value": narrative,
                            "catalog_value": "not newly source-verified",
                            "source_url": c.get("official_source_url")
                            or sources[item["key"]]["resolved_url"],
                            "source_location": "Stored narrative; flat-edge schema cannot prove equivalent semantics",
                            "review_status": "PARTIAL",
                        }
                    )
    supplement_from_cached_sources(
        snapshot, institutions, program_diffs, course_diffs, dependency_diffs
    )
    from scripts.nm_audit_analysis import (
        additional_checks,
        enrich_findings,
        write_supporting_reports,
    )

    evidence = additional_checks(
        snapshot, institutions, sources, program_diffs, course_diffs, dependency_diffs
    )
    from scripts.nm_audit_analysis import compare_nmjc_degree_index

    compare_nmjc_degree_index(
        snapshot, institutions, output / "nmjc-degree-index.json", program_diffs
    )
    for table, findings in (
        ("programs", program_diffs),
        ("courses", course_diffs),
        ("course_dependencies", dependency_diffs),
    ):
        enrich_findings(findings, table, snapshot, sources)
    evidence_fields = [
        "db_table",
        "db_record_id",
        "retrieved_at",
        "confidence",
        "needs_human_review",
        "recommendation",
    ]
    csv_write(output / "institutions.csv", list(rows[0]), rows)
    csv_write(
        output / "program-differences.csv",
        [
            "institution_key",
            "catalog_year",
            "program_name",
            "credential",
            "db_id",
            "issue",
            "db_value",
            "catalog_value",
            "source_url",
            "source_location",
            "review_status",
            *evidence_fields,
        ],
        program_diffs,
    )
    csv_write(
        output / "course-differences.csv",
        [
            "institution_key",
            "catalog_year",
            "course_code",
            "db_id",
            "issue",
            "db_value",
            "catalog_value",
            "source_url",
            "source_location",
            "review_status",
            *evidence_fields,
        ],
        course_diffs,
    )
    csv_write(
        output / "dependency-differences.csv",
        [
            "institution_key",
            "catalog_year",
            "course_code",
            "dependency_type",
            "dependency_course",
            "issue",
            "db_value",
            "catalog_value",
            "source_url",
            "source_location",
            "review_status",
            *evidence_fields,
        ],
        dependency_diffs,
    )
    csv_write(
        output / "identity-differences.csv", list(evidence["identity"][0]), evidence["identity"]
    )
    csv_write(output / "verified-samples.csv", list(evidence["samples"][0]), evidence["samples"])
    csv_write(
        output / "extra-institution-records.csv",
        [
            "institution_key",
            "university_id",
            "university_name",
            "city",
            "state",
            "website",
            "classification",
        ],
        extras
        + [
            {"institution_key": "", **r, "classification": "UNASSIGNED_OUTSIDE_DIRECTORY"}
            for r in unassigned
        ],
    )
    save_json(output / "institution-reconciliation.json", institutions)
    summary = {
        "expected": 20,
        "parent_keys_with_candidates": sum(bool(i["parents"]) for i in institutions),
        "unambiguous_parent_keys": sum(len(i["parents"]) == 1 for i in institutions),
        "missing_parent_keys": [i["key"] for i in institutions if not i["parents"]],
        "duplicate_parent_keys": [i["key"] for i in institutions if len(i["parents"]) > 1],
        "extra_related_records": len(extras),
        "full_curriculum_verifications": 0,
        "program_findings": dict(Counter(r["issue"] for r in program_diffs)),
        "course_findings": dict(Counter(r["issue"] for r in course_diffs)),
        "dependency_findings": dict(Counter(r["issue"] for r in dependency_diffs)),
        "database_mutations": 0,
        "student_row_contents_accessed": False,
        "database_counts": {k: v.get("count") for k, v in snapshot["tables"].items()},
        **evidence["metrics"],
    }
    save_json(output / "audit-metrics.json", summary)
    (output / "audit-summary.md").write_text(
        "# New Mexico academic-data audit — 2026-10-22\n\n"
        "Read-only database/institution audit with partial official-catalog comparison. "
        "**No institution is certified as fully imported or academically correct.**\n\n"
        f"Expected parent institutions: 20 (7 public four-year, 9 independent public, 4 tribal). "
        f"{summary['parent_keys_with_candidates']} keys have parent candidates; "
        f"{summary['unambiguous_parent_keys']} have exactly one. Missing parent: "
        f"{', '.join(summary['missing_parent_keys'])}; multiple parent candidates: "
        f"{', '.join(summary['duplicate_parent_keys'])}.\n\n"
        "Counts below are database row counts, NOT official catalog totals, distinct institutional "
        "course counts, offered sections, or verified completeness percentages.\n\n"
        "| Key | Parent identity | Programs | Course rows | Pre/co edges | Latest source edition established | Overall |\n"
        "|---|---|---:|---:|---:|---|---|\n" + "\n".join(matrix) + "\n\n"
        "## Safety and schema\n\n"
        f"Captured: {snapshot['captured_at']}. PostgreSQL {snapshot['server_version']}; "
        f"target: {snapshot['target_class']}; declared environment: {snapshot['declared_environment']}. "
        "A dedicated read-only URL was not configured unless recorded otherwise in database-snapshot.json. "
        f"Role has write privileges: {snapshot['role_has_write_privileges']}; both connection default and "
        "repeatable-read transaction were forced read-only and checked. Prefer a dedicated least-privilege "
        "audit account/read replica next time; environment ownership is not independently confirmed. "
        "No data/schema mutations or student row-content queries were issued.\n\n"
        f"Live Alembic revision {snapshot['database_revision']}; local source revisions: "
        f"{', '.join(snapshot['local_migration_revisions'])}. History aligned: "
        f"{snapshot['schema_history_aligned']}. `courses.program_id` defines catalog program membership; "
        "`program_courses.education_plan_id` is a student-plan relationship, not a catalog bridge. "
        "University identity has no dedicated type/abbreviation/current-parent flag, and no normalized "
        "catalog_versions table exists. Academic provenance/year fields are audited per record, not inferred.\n\n"
        "## Verified issues and interpretation\n\n"
        "- UNM has two parent candidates; preserve both until saved-plan references and aliases are reviewed.\n"
        "- Diné has Shiprock and Crownpoint center rows but no appropriate Tsaile parent row; no branch is counted as a parent.\n"
        "- SIPI stored name uses Southwest rather than the official Southwestern; alias match does not certify spelling.\n"
        "- Empty program course rosters and missing catalog-year/source provenance are enumerated in CSVs. "
        "They establish DB gaps, not invented official course counts.\n"
        "- Repeated codes across different programs/institutions are legitimate possibilities. Only within-program "
        "duplicate-code groups are flagged as candidates, with version/elective review required.\n"
        "- Cached WNMU same-edition program inventory and Pharmacy roster are compared separately with explicit "
        "capture dates. Other catalog visits establish editions and selected facts, not exhaustive curricula.\n\n"
        "## Coverage limits\n\n"
        "Every required source landing was attempted. See source-log.md for inaccessible pages, dynamic-only "
        "content, PDF availability and exact editions. PDF sources were inspected selectively, not exhaustively "
        "parsed into full course/requirement datasets. No missing edition was fabricated. "
        "Unknown DB catalog years prevent reliable like-for-like curriculum mismatch claims. "
        "No row-count comparison alone proves an import complete. Header-only or sparse differences do NOT "
        "mean zero source discrepancies.\n\n"
        "## Planner code review (not a student-data/runtime test)\n\n"
        "The editor extracts recognized course codes from text and checks prior-term prerequisites and same-term "
        "corequisites, including removal guards. It does not encode all narrative alternatives, minimum grades, "
        "placement or permission conditions. The graduation audit treats every linked catalog course as required "
        "and counts planned course IDs as completed; planned credits alone cannot prove graduation eligibility. "
        "These are verified implementation limitations, not a fresh end-to-end workflow pass. "
        "See repository-review.md for exact paths and line references.\n\n"
        "## Findings counts\n\n```json\n" + json.dumps(summary, indent=2) + "\n```\n",
        encoding="utf-8",
    )
    write_supporting_reports(output, snapshot, directory, sources, summary, evidence)
    return summary


def supplement_from_cached_sources(
    snapshot, institutions, program_diffs, course_diffs, dependency_diffs
):
    """Source-backed historical captures remain explicitly dated, never silently treated as fresh."""
    from scripts.publish_wnmu_batch import prepare_batch
    from scripts.wnmu_catalog import build_stage

    stage = build_stage()
    wnmu = next(i for i in institutions if i["key"] == "wnmu")
    _, programs, courses = academic_stats(snapshot, wnmu)
    source_ids = {p.get("official_source_id") for p in programs}
    for p in stage["programs"]:
        if p["official_source_id"] not in source_ids:
            candidates = [
                r["program_id"]
                for r in programs
                if normalized(r["program_name"]) == normalized(p["official_name"])
            ]
            program_diffs.append(
                {
                    "institution_key": "wnmu",
                    "catalog_year": "2025-2026",
                    "program_name": p["official_name"],
                    "credential": p["official_category"],
                    "db_id": candidates,
                    "issue": "OFFICIAL_ID_NOT_MATCHED_CACHED_PROGRAM_INDEX",
                    "db_value": "no exact official ID match; name candidates recorded separately",
                    "catalog_value": p["official_source_id"],
                    "source_url": p["official_source_url"],
                    "source_location": "Official index captured " + stage["source"]["retrieved_at"],
                    "retrieved_at": stage["source"]["retrieved_at"],
                    "review_status": "MISSING_IN_DB" if not candidates else "PARTIAL",
                }
            )
    batch = prepare_batch()
    for expected in batch["courses"]:
        matches = [
            c for c in courses if c.get("official_source_id") == expected["official_source_id"]
        ]
        for actual in matches:
            for field in ("course_code", "course_name", "credits"):
                same = (
                    Decimal(str(actual[field])) == Decimal(str(expected[field]))
                    if field == "credits"
                    else str(actual[field]) == str(expected[field])
                )
                if not same:
                    course_diffs.append(
                        {
                            "institution_key": "wnmu",
                            "catalog_year": "2025-2026",
                            "course_code": expected["course_code"],
                            "db_id": actual["course_id"],
                            "issue": "CACHED_ROSTER_FIELD_MISMATCH:" + field,
                            "db_value": actual[field],
                            "catalog_value": expected[field],
                            "source_url": expected["official_source_url"],
                            "source_location": "Program DOM captured "
                            + batch["source"]["retrieved_at"],
                            "retrieved_at": batch["source"]["retrieved_at"],
                            "review_status": "MISMATCH",
                        }
                    )
        if not matches:
            course_diffs.append(
                {
                    "institution_key": "wnmu",
                    "catalog_year": "2025-2026",
                    "course_code": expected["course_code"],
                    "db_id": "",
                    "issue": "CACHED_PHARMACY_ROSTER_COURSE_UNMATCHED",
                    "db_value": "no official ID match",
                    "catalog_value": expected["official_source_id"],
                    "source_url": expected["official_source_url"],
                    "source_location": "Program DOM captured " + batch["source"]["retrieved_at"],
                    "retrieved_at": batch["source"]["retrieved_at"],
                    "review_status": "MISSING_IN_DB",
                }
            )
    for c in courses:
        if c["metadata_json"].get("course_rules_status") == "not_fully_retrieved":
            dependency_diffs.append(
                {
                    "institution_key": "wnmu",
                    "catalog_year": "2025-2026",
                    "course_code": c["course_code"],
                    "dependency_type": "prerequisite/corequisite",
                    "dependency_course": "unknown",
                    "issue": "SOURCE_RULES_NOT_FULLY_RETRIEVED",
                    "db_value": c["metadata_json"]["course_rules_status"],
                    "catalog_value": "unverified; null does not mean no requirement",
                    "source_url": c.get("official_source_url"),
                    "source_location": "Import provenance flag",
                    "db_table": "courses.metadata_json",
                    "db_record_id": c["course_id"],
                    "retrieved_at": snapshot["captured_at"],
                    "review_status": "PARTIAL",
                }
            )


async def run(args):
    args.output.mkdir(parents=True, exist_ok=True)
    snapshot_path = args.output / "database-snapshot.json"
    if args.collect:
        try:
            snapshot = await collect(args.env)
        except Exception as error:
            # Do not copy driver error/DSN strings into public reports.
            save_json(
                args.output / "database-access-status.json",
                {
                    "status": "BLOCKED_NO_DB_ACCESS",
                    "exception_type": type(error).__name__,
                    "details": "Connection/read-only/schema check failed; credentials are never emitted.",
                },
            )
            raise RuntimeError("Read-only DB collection failed: " + type(error).__name__) from None
        save_json(snapshot_path, snapshot)
        save_json(
            args.output / "database-access-status.json",
            {
                "status": "VERIFIED_READ_ONLY_SNAPSHOT",
                "captured_at": snapshot["captured_at"],
                "database_mutations": 0,
                "student_row_contents_accessed": False,
            },
        )
        print(json.dumps({"event": "readonly_snapshot_saved", "counts": snapshot["tables"]}))
    else:
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    if args.report:
        directory = json.loads(
            (args.output / "institution-directory.json").read_text(encoding="utf-8")
        )
        sources = json.loads((args.output / "source-evidence.json").read_text(encoding="utf-8"))
        for source in sources.values():
            source.setdefault(
                "observed_at", "2026-10-22; exact HTTP retrieval time not exposed by web tool"
            )
            source.setdefault(
                "collection_method",
                "bounded official public web-tool reads; cached WNMU fixtures separately dated",
            )
        print(json.dumps(write_reports(snapshot, directory, sources, args.output), indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", type=Path, default=ROOT / "fastapi_backend/.env")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--collect", action="store_true", help="Bounded read-only database queries")
    parser.add_argument(
        "--report", action="store_true", help="Generate reports offline from saved evidence"
    )
    asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    main()
