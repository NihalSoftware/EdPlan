"""Offline checks and report writing for the read-only New Mexico audit.

No database or network client is used here. Source facts are deliberately small,
explicitly located spot checks, never a substitute for a complete catalog crawl.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation

from scripts.audit_nm_colleges import normalized, stored_source_url

SIPI_PDF = "https://4.files.edl.io/5a02/08/05/26/202024-20015adf-0052-4850-bffb-b464a67a8f78.pdf"
CNM_PDF = (
    "https://www.cnm.edu/students/services/catalog-resources/documents/"
    "2026-2027-cnm-catalog-volume-58.pdf"
)
OBSERVED = "2026-10-22; exact HTTP retrieval time not exposed by web tool"


def decimal_equal(left, right):
    """Unknown is not zero; numerical display precision is not a discrepancy."""
    if left is None or right is None:
        return left is right
    try:
        return Decimal(str(left)) == Decimal(str(right))
    except InvalidOperation:
        return False


def code_key(value):
    # Comparison only: preserve official punctuation and suffixes in evidence.
    return "".join((value or "").split()).upper()


def compare_nmjc_degree_index(snapshot, institutions, fixture_path, findings):
    """Compare a published subset; never infer a missing record from a weak name match."""
    if not fixture_path.exists():
        return
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    parent_ids = {
        p["university_id"] for i in institutions if i["key"] == "nmjc" for p in i["parents"]
    }
    programs = [p for p in snapshot["rows"]["programs"] if p["university_id"] in parent_ids]
    for entry in fixture["entries"]:
        candidates = [
            p
            for p in programs
            if normalized(p["program_name"]) == normalized(entry["name"])
            and "associate" in p["degree"].lower()
        ]
        findings.append(
            {
                "institution_key": "nmjc",
                "catalog_year": fixture["catalog_year"],
                "program_name": entry["name"],
                "credential": entry["credential"],
                "db_id": [p["program_id"] for p in candidates],
                "issue": "NMJC_ASSOCIATE_ENTRY_YEAR_CREDENTIAL_REVIEW",
                "db_value": [
                    {"degree": p["degree"], "year": p["metadata_json"].get("catalog_year")}
                    for p in candidates
                ]
                or "No exact normalized title candidate; aliases not resolved",
                "catalog_value": entry,
                "source_url": fixture["source_url"],
                "source_location": fixture["source_location"],
                "retrieved_at": fixture["retrieved_at"],
                "review_status": "SOURCE_UNVERIFIED",
                "confidence": "medium" if candidates else "low",
                "needs_human_review": True,
                "recommendation": "Resolve exact title, credential and DB year; generic Associate labels are not award equivalence",
            }
        )


def cyclic_components(edges):
    """Iterative Kosaraju; includes concurrent groups, without calling them invalid."""
    forward, reverse = defaultdict(set), defaultdict(set)
    for a, b in edges:
        forward[a].add(b)
        forward.setdefault(b, set())
        reverse[b].add(a)
        reverse.setdefault(a, set())
    seen, order = set(), []
    for root in sorted(forward):
        if root in seen:
            continue
        stack = [(root, False)]
        while stack:
            node, expanded = stack.pop()
            if expanded:
                order.append(node)
            elif node not in seen:
                seen.add(node)
                stack.append((node, True))
                stack.extend(
                    (n, False) for n in sorted(forward[node], reverse=True) if n not in seen
                )
    seen, cycles = set(), []
    for root in reversed(order):
        if root in seen:
            continue
        group, stack = [], [root]
        seen.add(root)
        while stack:
            node = stack.pop()
            group.append(node)
            for other in sorted(reverse[node]):
                if other not in seen:
                    seen.add(other)
                    stack.append(other)
        if len(group) > 1:
            cycles.append(sorted(group))
    return sorted(cycles)


def enrich_findings(findings, table, snapshot, sources):
    for row in findings:
        key = row["institution_key"]
        source = sources.get(key, {})
        row.setdefault("db_table", table)
        record_id = row.get("db_id", "")
        if table == "course_dependencies" and not record_id:
            if isinstance(row.get("db_value"), dict) and row["db_value"].get("id"):
                record_id = row["db_value"]["id"]
            else:
                # Code alone is not a global identifier: constrain by parent institution.
                record_id = "See explicit db_record_id; no globally matched code IDs inferred"
        row.setdefault("db_record_id", record_id)
        row.setdefault(
            "retrieved_at",
            source.get("observed_at", OBSERVED)
            if row.get("source_url")
            else snapshot["captured_at"],
        )
        row.setdefault(
            "confidence",
            "high"
            if row["issue"]
            in {
                "NO_LINKED_CATALOG_COURSES",
                "SOURCE_OR_CATALOG_YEAR_UNRECORDED",
                "DANGLING_DEPENDENCY",
                "SELF_DEPENDENCY",
                "CROSS_INSTITUTION_DEPENDENCY",
                "ORPHAN_PROGRAM",
                "ORPHAN_COURSE",
                "NEGATIVE_CREDITS",
            }
            else "medium",
        )
        row.setdefault("needs_human_review", True)
        row.setdefault(
            "recommendation",
            "Review exact institution, catalog year and official source; "
            "prepare a versioned proposal only. Do not change or delete automatically.",
        )


def additional_checks(snapshot, institutions, sources, program_diffs, course_diffs, dep_diffs):
    programs, courses = snapshot["rows"]["programs"], snapshot["rows"]["courses"]
    pmap = {p["program_id"]: p for p in programs}
    cmap = {c["course_id"]: c for c in courses}
    parent_owner = {r["university_id"]: i["key"] for i in institutions for r in i["parents"]}
    owner = {
        p["program_id"]: parent_owner.get(p["university_id"], "out_of_scope") for p in programs
    }
    identities, samples = [], []
    for item in institutions:
        for parent in item["parents"]:
            for field, actual, expected in (
                ("city", parent.get("city"), item["city"]),
                ("state", parent.get("state"), item.get("state", "New Mexico")),
                ("university_name", parent["university_name"], item["name"]),
            ):
                if normalized(actual) == normalized(expected):
                    continue
                # A main-campus alias is not by itself an incorrect institutional name.
                alias = field == "university_name" and item["key"] != "sipi"
                identities.append(
                    {
                        "institution_key": item["key"],
                        "db_table": "universities",
                        "db_record_id": parent["university_id"],
                        "field": field,
                        "db_value": actual,
                        "catalog_value": expected,
                        "source_url": item["landing_url"],
                        "source_location": "Official directory identity",
                        "retrieved_at": OBSERVED,
                        "review_status": "PARTIAL" if alias else "MISMATCH",
                        "confidence": "medium" if alias else "high",
                        "needs_human_review": True,
                        "recommendation": "Review alias without merging IDs"
                        if alias
                        else "Prepare identity-only correction; preserve foreign keys and campus distinctions",
                    }
                )
    for p in programs:
        if p["university_id"] not in {r["university_id"] for r in snapshot["rows"]["universities"]}:
            program_diffs.append(
                {
                    "institution_key": "orphan",
                    "db_id": p["program_id"],
                    "program_name": p["program_name"],
                    "issue": "ORPHAN_PROGRAM",
                    "db_value": p["university_id"],
                    "review_status": "MISMATCH",
                }
            )
    for c in courses:
        if c["program_id"] not in pmap:
            course_diffs.append(
                {
                    "institution_key": "orphan",
                    "db_id": c["course_id"],
                    "course_code": c["course_code"],
                    "issue": "ORPHAN_COURSE",
                    "db_value": c["program_id"],
                    "review_status": "MISMATCH",
                }
            )
        if c.get("credits") is not None and Decimal(str(c["credits"])) < 0:
            course_diffs.append(
                {
                    "institution_key": owner.get(c["program_id"], "orphan"),
                    "db_id": c["course_id"],
                    "course_code": c["course_code"],
                    "issue": "NEGATIVE_CREDITS",
                    "db_value": c["credits"],
                    "review_status": "MISMATCH",
                }
            )
    cycle_counts = {}
    departments = {d["department_id"]: d for d in snapshot["rows"]["catalog_departments"]}
    bridge_problems = []
    for table, record_field, targets in (
        ("program_departments", "program_id", pmap),
        ("course_departments", "course_id", cmap),
    ):
        for relation in snapshot["rows"][table]:
            target = targets.get(relation[record_field])
            department = departments.get(relation["department_id"])
            target_program = (
                target
                if table == "program_departments"
                else pmap.get((target or {}).get("program_id"))
            )
            if (
                not target_program
                or not department
                or target_program["university_id"] != department["university_id"]
            ):
                bridge_problems.append(
                    {
                        "table": table,
                        "id": relation["id"],
                        "issue": "ORPHAN_OR_CROSS_INSTITUTION_DEPARTMENT_LINK",
                    }
                )
    for table, field, kind in (
        ("course_prerequisites", "prerequisite_course_id", "prerequisite"),
        ("course_corequisites", "corequisite_course_id", "corequisite"),
    ):
        components = cyclic_components((r["course_id"], r[field]) for r in snapshot["rows"][table])
        cycle_counts[kind] = len(components)
        for group in components:
            a = cmap.get(group[0], {})
            dep_diffs.append(
                {
                    "institution_key": owner.get(a.get("program_id"), "orphan"),
                    "db_table": table,
                    "db_record_id": [
                        e["id"]
                        for e in snapshot["rows"][table]
                        if e["course_id"] in group and e[field] in group
                    ],
                    "catalog_year": "UNSPECIFIED",
                    "course_code": a.get("course_code", group[0]),
                    "dependency_type": kind,
                    "dependency_course": [cmap.get(i, {}).get("course_code", i) for i in group],
                    "issue": "PREREQUISITE_CYCLE_REVIEW"
                    if kind == "prerequisite"
                    else "CONCURRENT_GROUP_REVIEW",
                    "db_value": group,
                    "catalog_value": "Official exceptions/concurrent rules not verified",
                    "source_location": "Database graph; co-requisite cycles may be legitimate",
                    "review_status": "PARTIAL",
                }
            )
    # Attach exact IDs to stored narrative checks. A code can occur in multiple programs.
    for row in dep_diffs:
        if row["issue"] == "COMPLEX_NARRATIVE_REQUIRES_RULE_REVIEW":
            row["db_table"] = "courses.metadata_json"
            row["db_record_id"] = [
                c["course_id"]
                for c in courses
                if owner.get(c["program_id"]) == row["institution_key"]
                and c["course_code"] == row["course_code"]
                and c["metadata_json"].get(row["dependency_type"]) == row["db_value"]
            ]
    # Same-edition, exact program title/credential spot checks (not full requirement validation).
    sipi = [p for p in programs if owner.get(p["program_id"]) == "sipi"]
    accounting = [
        p
        for p in sipi
        if normalized(p["program_name"]) == "accounting"
        and p["degree"] == "Associate of Applied Science"
    ]
    if not accounting:
        program_diffs.append(
            {
                "institution_key": "sipi",
                "catalog_year": "2026-2027",
                "program_name": "Accounting",
                "credential": "Associate of Applied Science",
                "db_id": "",
                "issue": "PUBLISHED_CREDENTIAL_WITHOUT_MATCHING_PROGRAM",
                "db_value": "Accounting Certificate exists; no Accounting AAS title/award match",
                "catalog_value": "AAS published; credit total conflicts internally (60 table / 63 sequence)",
                "source_url": SIPI_PDF,
                "source_location": "PDF pages 65-67, Accounting AAS",
                "review_status": "MISSING_IN_DB",
                "confidence": "medium",
                "recommendation": "Review proposed versioned insertion; resolve official 60/63 credit conflict before preparing values",
            }
        )
    program_diffs.append(
        {
            "institution_key": "sipi",
            "catalog_year": "2026-2027",
            "program_name": "Accounting",
            "credential": "Associate of Applied Science",
            "db_id": [p["program_id"] for p in accounting],
            "issue": "OFFICIAL_SOURCE_INTERNAL_CREDIT_CONFLICT",
            "db_value": "No value chosen",
            "catalog_value": "60 credits in requirement table; 63 in suggested sequence",
            "source_url": SIPI_PDF,
            "source_location": "PDF page 66 total vs page 67 total",
            "review_status": "PARTIAL",
            "confidence": "high",
            "recommendation": "Obtain official clarification; do not choose a credit total automatically",
        }
    )
    for name, degree, credits, location in (
        ("Business Administration", "Associate of Science", 68, "PDF pages 71-72, total credits"),
        (
            "Business Administration",
            "Associate of Applied Science",
            63,
            "PDF pages 74-75, total credits",
        ),
        ("Business Administration", "Certificate", 33, "PDF page 76, total credits"),
        ("Computer Aided Drafting and Design", "Certificate", 38, "PDF page 78, total credits"),
    ):
        for p in sipi:
            if normalized(p["program_name"]) != normalized(name) or p["degree"] != degree:
                continue
            same_year = p["metadata_json"].get("catalog_year") == "2026-2027"
            status = (
                "VERIFIED"
                if same_year and decimal_equal(p["total_credit_hours"], credits)
                else "PARTIAL"
            )
            samples.append(
                {
                    "institution_key": "sipi",
                    "db_table": "programs",
                    "db_record_id": p["program_id"],
                    "catalog_year": "2026-2027",
                    "field": "total_credit_hours",
                    "db_value": p["total_credit_hours"],
                    "catalog_value": credits,
                    "source_url": SIPI_PDF,
                    "source_location": location,
                    "retrieved_at": OBSERVED,
                    "review_status": status,
                    "scope": "Selected field only; no full-program certification",
                }
            )
    # One matching course sample uses exact code after whitespace normalization only.
    pid = "2641548b-c08e-492d-98df-d027b09b7acd"
    for c in courses:
        if c["program_id"] == pid and code_key(c["course_code"]) == "BCIS1110":
            samples.append(
                {
                    "institution_key": "sipi",
                    "db_table": "courses",
                    "db_record_id": c["course_id"],
                    "catalog_year": "2026-2027",
                    "field": "credits",
                    "db_value": c["credits"],
                    "catalog_value": 3,
                    "source_url": SIPI_PDF,
                    "source_location": "PDF page 71, program-specific requirements",
                    "retrieved_at": OBSERVED,
                    "review_status": "VERIFIED"
                    if decimal_equal(c["credits"], 3)
                    and c["metadata_json"].get("catalog_year") == "2026-2027"
                    else "PARTIAL",
                    "scope": "Selected course credits only",
                }
            )
    # Source conflicts are not forced into automatic curriculum corrections.
    dep_diffs.append(
        {
            "institution_key": "sipi",
            "catalog_year": "2026-2027",
            "db_id": pid,
            "db_table": "programs",
            "course_code": "ENGL 1110 / ENGL 2110",
            "dependency_type": "sequencing/source conflict",
            "dependency_course": "Composition I",
            "issue": "OFFICIAL_SOURCE_INTERNAL_CODE_CONFLICT",
            "db_value": "not automatically corrected",
            "catalog_value": "Required-course table and suggested sequence use different codes",
            "source_url": SIPI_PDF,
            "source_location": "PDF pages 69-71 and 73-74; Business AS/AAS",
            "review_status": "PARTIAL",
            "confidence": "high",
            "recommendation": "Ask registrar to resolve table/sequence code conflicts; preserve source text",
        }
    )
    cnm_program = next(
        (p for p in programs if p["program_id"] == "aaaaaaaa-0004-0000-0000-000000000004"), None
    )
    if cnm_program:
        program_diffs.append(
            {
                "institution_key": "cnm",
                "catalog_year": "2026-2027 source; DB unspecified",
                "program_name": cnm_program["program_name"],
                "credential": cnm_program["degree"],
                "db_id": cnm_program["program_id"],
                "issue": "CANDIDATE_PROGRAM_VERSION_TITLE_CREDIT_REVIEW",
                "db_value": {
                    "title": cnm_program["program_name"],
                    "credits": cnm_program["total_credit_hours"],
                },
                "catalog_value": {
                    "title": "Computer Information Systems (AAS), Cyber Security Concentration",
                    "credits": 62,
                },
                "source_url": CNM_PDF,
                "source_location": "PDF pages 70-71 (printed 69-70)",
                "review_status": "SOURCE_UNVERIFIED",
                "confidence": "low",
                "recommendation": "Do not equate a standalone title and concentration without year/identity review",
            }
        )
        dep_diffs.append(
            {
                "institution_key": "cnm",
                "catalog_year": "2026-2027 source; DB unspecified",
                "db_id": cnm_program["program_id"],
                "db_table": "programs",
                "course_code": "BCIS 1110 / CSCI 1108",
                "dependency_type": "program alternative",
                "dependency_course": "OR requirement",
                "issue": "SOURCE_ALTERNATIVE_NOT_FLAT_ALL_REQUIRED",
                "db_value": "Candidate program relationship unresolved",
                "catalog_value": "Choose one introductory computing alternative",
                "source_url": CNM_PDF,
                "source_location": "PDF page 70, first-term curriculum",
                "review_status": "PARTIAL",
                "confidence": "low",
            }
        )
    # Blanket credit defaults are suspicious, not confirmed source errors.
    nmt = [p for p in programs if owner.get(p["program_id"]) == "nmt"]
    nmt_counts = Counter(str(p["total_credit_hours"]) for p in nmt)
    for p in nmt:
        if p["total_credit_hours"] == 120 and "bachelor" not in p["degree"].lower():
            program_diffs.append(
                {
                    "institution_key": "nmt",
                    "db_id": p["program_id"],
                    "catalog_year": p["metadata_json"].get("catalog_year", "UNSPECIFIED"),
                    "program_name": p["program_name"],
                    "credential": p["degree"],
                    "issue": "SUSPICIOUS_UNIFORM_CREDIT_DEFAULT",
                    "db_value": 120,
                    "catalog_value": "Not independently established for this record/year",
                    "source_url": sources["nmt"]["resolved_url"],
                    "source_location": "DB credit distribution across unlike credentials",
                    "review_status": "SOURCE_UNVERIFIED",
                    "confidence": "low",
                }
            )
    return {
        "identity": identities,
        "samples": samples,
        "metrics": {
            "programs_without_catalog_year": sum(
                not p["metadata_json"].get("catalog_year") for p in programs
            ),
            "programs_explicitly_partial_import": sum(
                p["metadata_json"].get("course_import_is_partial") is True for p in programs
            ),
            "courses_explicitly_partial_import": sum(
                c["metadata_json"].get("course_import_is_partial") is True for c in courses
            ),
            "courses_without_catalog_year": sum(
                not c["metadata_json"].get("catalog_year") for c in courses
            ),
            "programs_without_official_source_url": sum(
                not p.get("official_source_url") for p in programs
            ),
            "programs_without_any_recorded_source_url": sum(
                not stored_source_url(p) for p in programs
            ),
            "courses_without_official_source_url": sum(
                not c.get("official_source_url") for c in courses
            ),
            "courses_without_any_recorded_source_url": sum(
                not stored_source_url(c) for c in courses
            ),
            "department_bridge_issues": bridge_problems,
            "orphan_program_rows": sum(
                p["university_id"]
                not in {u["university_id"] for u in snapshot["rows"]["universities"]}
                for p in programs
            ),
            "orphan_course_rows": sum(c["program_id"] not in pmap for c in courses),
            "dangling_dependency_edges": sum(
                e["course_id"] not in cmap or e[field] not in cmap
                for table, field in (
                    ("course_prerequisites", "prerequisite_course_id"),
                    ("course_corequisites", "corequisite_course_id"),
                )
                for e in snapshot["rows"][table]
            ),
            "excluded_branch_rows": sum(
                len(i["related"]) for i in institutions if i["key"] != "dine"
            ),
            "dine_center_rows": sum(len(i["related"]) for i in institutions if i["key"] == "dine"),
            "fractional_course_credit_rows": sum(
                Decimal(str(c["credits"])) % 1 != 0 for c in courses if c.get("credits") is not None
            ),
            "zero_credit_course_rows_review_not_automatically_invalid": sum(
                decimal_equal(c.get("credits"), 0) for c in courses
            ),
            "cycle_components": cycle_counts,
            "nmt_program_credit_distribution": dict(nmt_counts),
            "selected_field_verifications": sum(s["review_status"] == "VERIFIED" for s in samples),
            "source_status_counts": dict(Counter(s["status"] for s in sources.values())),
        },
    }


def write_supporting_reports(output, snapshot, directory, sources, summary, evidence):
    source_lines = [
        "# Official-source log",
        "",
        "Observation date: 2026-10-22. Collection: bounded public reads through the web tool; no bulk crawl, authentication bypass, or private API.",
        "Exact HTTP retrieval timestamps are not exposed by that tool; the observation date is recorded rather than invented seconds. Cached WNMU fixtures retain their original October 16 timestamps. Browser initialization failed (kernel asset path error), so no browser visual inspection is claimed.",
        "",
        "Blocked responses were not treated as evidence of absent programs. Sources were reused through tool references to avoid duplicate downloads; site access restrictions were not bypassed. Custom User-Agent control is not available through the web tool; the reusable audit script performs no HTTP crawl. Any future crawler must use a descriptive User-Agent, approved hosts, robots/terms review and per-host delays (WNMU previously advertised 120 seconds).",
        "",
    ]
    for institution in directory:
        s = sources[institution["key"]]
        source_lines += [
            f"## {institution['key']} — {institution['name']}",
            "",
            f"- Discovery: {institution['landing_url']}",
            f"- Resolved source: {s['resolved_url']}",
            f"- Other source URLs: {'; '.join(s.get('additional_urls', [])) or 'none established'}",
            f"- Edition: {s['catalog_year']}",
            f"- Access/coverage: {s['status']}",
            f"- Observation: {s.get('observed_at', OBSERVED)}",
            f"- Location: {s['location']}",
            f"- Limits: {s['notes']}",
            "",
        ]
    (output / "source-log.md").write_text("\n".join(source_lines), encoding="utf-8")
    (output / "remediation-plan.md").write_text(
        """# Proposed remediation — NOT executed

No SQL, migration, import, merge, deletion, or application fix below has been applied.

## Priorities and approval gates

1. **P1: parent identities.** Propose a Diné parent at Tsaile, Arizona, retaining Shiprock as its NM service location. Review the two existing center IDs before introducing parent/campus links. Resolve UNM's two parent candidates through reference counts and a user-approved canonical-ID/alias map; do not delete either ID or move saved plans automatically. Correct SIPI's official spelling in a separately approved identity-only update.
2. **P1: recover catalog provenance and schema history.** Reconcile live Alembic 0014 with local sources through 0010 from the authoritative migration history. Do not stamp or reset. Document DB environment ownership, obtain a dedicated read-only role/replica, then establish per-record edition, source ID/URL and retrieval timestamp. Unknown year is not the latest year.
3. **P1: version-scoped missing content.** WNMU's October 16 same-edition index has unmatched official IDs (see CSV). Review for source-URL/name matches before proposing insertion; an unmatched ID alone is not proof that no equivalent row exists. Empty catalog rosters (including NMMI) require permitted official sources, not synthetic courses. Do not mark programs absent from one crawl inactive.
4. **P1: planning semantics.** Model requirement groups/alternatives, grade thresholds, placement, admission and concurrent exceptions without flattening OR into AND. Keep exact narratives. Separate planned from completed credits in graduation feedback. Validate alternatives and removal guards using synthetic fixtures before any release; do not change academic rules based on this audit alone.
5. **P2: source conflicts and suspicious credits.** Ask SIPI's registrar to resolve code differences between requirement tables and suggested sequences. Review NMT's repeated 120-credit values across unlike awards against exact year/credential pages. CNM Cybersecurity versus current CIS AAS concentration is a review suggestion, not a safe match or approved 64-to-62 correction.
6. **P2: sources not fully accessible.** Obtain permitted exports/PDFs for NMSU Las Cruces, NNMC, NMMI, San Juan and SFCC; a current Mesalands document; and accessible IAIA/Luna/dynamic inventories. Finish program, course, credit and dependency comparisons for every accessible institution. No full curriculum certification is issued here.
7. **P2: type/provenance boundaries.** Live numeric credits can include fractions but ORM/API use integers. Review a backward-compatible Decimal/range representation and serialization contract. Catalog departments exist but course-department bridge coverage is empty; do not infer department ownership from a shared code alone.

## Safe change design (requires a later explicit approval)

- Establish target institution, exact catalog year, official ID/code and parent scope. High-confidence ID/code/URL matches can be staged; exact-name and fuzzy cases remain review-only. Never match globally on course code.
- Generate a deterministic dry-run diff and immutable evidence hashes; report inserts, field updates, relationship changes and not-found rows separately. Preserve valid nonempty values and all historical curricula.
- Take an approved backup/snapshot and verify restore access. Rehearse against a disposable copy with masked/synthetic student data. The audit itself did not access student row contents.
- For approved batches only: use parameterized SQL/ORM and one bounded transaction, advisory/optimistic concurrency protection, expected-old-value predicates, FK checks and uniqueness scoped to institution/year/program as appropriate. Before values change, persist old/new values, table/record IDs, run ID, match/confidence, source URL and timestamp in the audit trail. Abort on unexpected counts or concurrent drift.
- Saved plans may reference program/course UUIDs. Prefer additive catalog-version records and stable aliases; avoid in-place cross-year replacement or cascading deletion. Report reference counts without exporting personal rows; ask for approval before remapping any plan.
- Roll back the transaction on validation failure. After commit, restore only the exact audited fields/IDs with expected-new-value predicates in a separately approved compensating transaction; do not overwrite later edits. Verify API serialization and planner behavior with existing plus new fixture tests.

## Completion gate for a follow-up audit

All 20 parents reconciled; every source edition established or explicitly blocked; full official program inventories matched; required/selectable course groups and narrative dependencies reconciled; source conflicts resolved; dry-run reviewed; existing saved-plan identities preserved. Row counts and selected passing fields are not completeness proof.
""",
        encoding="utf-8",
    )
    (output / "repository-review.md").write_text(
        """# Repository and schema review (read-only)

## Implementation and mappings

- Frontend: React 18/Vite/Tailwind in `ChatbotUI`; backend: Python/FastAPI, SQLAlchemy asyncio/asyncpg, Pydantic and Alembic in `fastapi_backend`. Existing catalog scripts use official HTML/PDF fixture extraction; no new dependency or framework was added for this audit.
- `universities.university_id -> programs.university_id -> courses.program_id` is the catalog chain. Courses repeat across programs, so global code uniqueness would be unsafe. `program_courses.education_plan_id` is a student-plan table, NOT a catalog membership bridge; its contents were not read.
- Flat `course_prerequisites` and `course_corequisites` contain directional course UUID edges. Department identity and bridge tables exist; counts/constraints/indexes/column definitions are preserved in `database-snapshot.json` and `schema-evidence.json`.
- No normalized `catalog_versions` table; institution type/abbreviation/active-parent fields unavailable. Current/historical flags inside JSON are not a universal lifecycle contract. No database triggers were returned by schema discovery. DB revision 0014 is not represented by the available local migration files through 0010.
- Live academic rows have `official_source_id`, `official_source_url`, `source_retrieved_at`; JSON also carries mixed import formats/partial-planning flags. A missing dedicated provenance column is reported as a storage gap, not proof that every JSON narrative is unsourced.

## Verified code limitations (no app code changed)

1. `ChatbotUI/src/components/education/EducationPlanEditor.jsx:112` extracts known code substrings from narrative text. It cannot preserve general AND/OR logic or grade/permission/placement semantics; unknown codes may be omitted. Lines 180-225 validate sequencing, 797-817 guard additions and 905-940 guard removals. These guard paths were inspected, not runtime-tested with real student plans.
2. `fastapi_backend/app/student/domains/planning/services/planning_validation_service.py` validates flat prerequisite/corequisite edges and term credits. Passing those checks cannot prove a complex narrative is fulfilled. Existing service tests use fake repositories; see quality-verification.md for the actual run result.
3. `fastapi_backend/app/student/domains/planning/services/graduation_audit_service.py:45` counts planned courses as completed (lines 51-62), treats all program-linked courses as required, and sets graduation_ready from roster/credit coverage (line 88), without completed status or requirement-choice evaluation. This can overstate readiness or require all alternatives.
4. `fastapi_backend/app/student/domains/discovery/schemas/course.py:15` declares integer credits; the course model in `models/program.py` also uses Integer while live PostgreSQL stores numeric credits. Fractional/range values need a contract review; no API/model changes were made.

## Likely causes — hypotheses unless noted above

Mixed older seed/import formats, absent catalog-version identity, partial rosters, uniform default credits and mismatched live/local migration history are consistent with the observed gaps. This audit does not establish who introduced a value or when; transaction logs/import history would be needed to prove causation. Unsupported pricing/eligibility fields were not validated as academic requirements.

## Reproduction

From `fastapi_backend`, use the existing `.venv/Scripts/python.exe -m scripts.audit_nm_colleges --report` for offline report generation. `--collect --report` additionally performs bounded SELECT/SHOW in a repeatable-read, forced-read-only transaction using READ_ONLY_DATABASE_URL if set, otherwise the existing DATABASE_URL. Do not pass secrets on the command line. The script has no apply/write-to-database mode.

The source-evidence file is a manually curated observation log, not a crawler result claiming full inventories. Offline regression tests require no network or database. CSVs use UTF-8 BOM, serialize structured evidence as JSON, and prefix formula-like text with an apostrophe for safe spreadsheet viewing; unchanged raw values remain in the academic JSON snapshot. Difference counts include metadata gaps and review suggestions, NOT only proven academic errors.
""",
        encoding="utf-8",
    )
    schema_keys = (
        "columns",
        "constraints",
        "indexes",
        "triggers",
        "database_revision",
        "local_migration_revisions",
    )
    (output / "schema-evidence.json").write_text(
        json.dumps({k: snapshot[k] for k in schema_keys}, indent=2) + "\n", encoding="utf-8"
    )
    # Immutable input digest permits offline reproduction without reconnecting.
    digest = hashlib.sha256((output / "database-snapshot.json").read_bytes()).hexdigest()
    append = (
        "\n## Priorities and measured gaps\n\n"
        f"Programs without stored catalog year: {summary['programs_without_catalog_year']}/944; "
        f"course rows without year: {summary['courses_without_catalog_year']}/13706. "
        f"Selected field matches: {summary['selected_field_verifications']}; full curriculum verifications: 0. "
        "See verified-samples.csv; passing one field does not certify a program.\n\n"
        "Priorities: Diné/UNM identity reconciliation, version/provenance recovery, approved official-source "
        "inventory completion, then planner dependency/choice semantics. Source-blocked institutions: "
        + ", ".join(k for k, s in sources.items() if s["status"] == "SOURCE_BLOCKED")
        + ". Mesalands current edition remains unverified.\n\n"
        f"Snapshot SHA-256: `{digest}`. See remediation-plan.md and quality-verification.md.\n"
    )
    with (output / "audit-summary.md").open("a", encoding="utf-8") as stream:
        stream.write(append)
