"""Resumable official-source crawl and deterministic, non-publishing staging output."""

from __future__ import annotations

import json
import logging
import re
from collections import Counter
from pathlib import Path
from urllib.parse import quote, urlsplit

from .baseline import save_json
from .normalize import canonical_hash, normalize, plain, walk
from .sources import ORIGIN, PageParser, PublicCatalogClient, approved_url, decode_nuxt

LOGGER = logging.getLogger(__name__)
INDEXES = (
    "/",
    "/institute-reqs/nmt-degrees",
    "/programs",
    "/departments",
    "/courses",
    "/institute-reqs/gen-ed",
    "/institute-reqs/degree-requirements",
)


def program_link(href):
    """Program tabs repeat the same complete SSR record; they are not new programs."""
    return bool(re.fullmatch(r"/programs/[^/]+/?", urlsplit(href).path))


def record_from_page(html, kind, year):
    parser = PageParser(html)
    if not parser.nuxt:
        raise ValueError("Missing public structured SSR state; manual extraction needed")
    data = decode_nuxt(parser.nuxt)
    settings = data.get("pinia", {}).get("settings", {})
    if year not in str(settings.get("catalogDisplayName", "")):
        raise ValueError("Official page does not identify the requested catalog year")
    records = [
        v[kind]
        for v in data.get("data", {}).values()
        if isinstance(v, dict) and isinstance(v.get(kind), dict)
    ]
    if len(records) != 1:
        raise ValueError("Expected exactly one official academic record")
    return records[0], data, parser


def pdf_inventory(output):
    path = output / "pdf-pages.jsonl"
    manifest = output / "pdf-manifest.json"
    if not path.exists() or not manifest.exists():
        raise ValueError("Extract the supplied PDF evidence first")
    pages = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    candidates = {}
    for page in pages:
        for match in re.finditer(
            r"(?m)(?<!\S)([A-Z][A-Z&]{1,9} ?\d{3,4}[A-Z]{0,3})\s+-\s+", page["text"]
        ):
            code = match[1]
            ref = {
                k: page[k] for k in ("pdf_page_index", "pdf_page_number", "printed_page", "sha256")
            }
            if ref not in candidates.setdefault(code, []):
                candidates[code].append(ref)
    return candidates, pages, json.loads(manifest.read_text(encoding="utf-8"))


def build_stage(output: Path, year: str, *, offline=False, max_courses=0, max_programs=0):
    client = PublicCatalogClient(output / "cache", offline=offline)
    programs, courses, inventory, failures, source_pages = {}, {}, {}, [], {}
    departments, policies = {}, []
    discovered_programs = set()
    pdf_codes, pdf_pages, pdf_manifest = pdf_inventory(output)

    def load(url):
        html, source = client.fetch(url)
        source_pages[source["url"]] = source
        return html, source

    try:
        for path in INDEXES:
            url = ORIGIN + path
            try:
                html, source = load(url)
                parser = PageParser(html)
                for link in parser.links:
                    if program_link(link["href"]):
                        discovered_programs.add(approved_url(link["href"]))
                state = decode_nuxt(parser.nuxt)
                settings = state.get("pinia", {}).get("settings", {})
                if year not in str(settings.get("catalogDisplayName", "")):
                    raise ValueError("Index catalog year mismatch")
                for department in state.get("pinia", {}).get("departments", {}).get("all", []):
                    code = department.get("id")
                    if code and department.get("name"):
                        departments[code] = {
                            "code": code,
                            "name": department["name"],
                            "display_name": department.get("displayName"),
                            "subject_codes": department.get("subjectCodes") or [],
                            "institution": "NMT",
                            "catalog_year": year,
                            "source": source,
                            "publication_status": "staged_only",
                            "verification_status": "awaiting_review",
                        }
                if path.startswith("/institute-reqs/") and "nmt-degrees" not in path:
                    page = next(
                        (
                            v
                            for v in state.get("data", {}).values()
                            if isinstance(v, dict) and v.get("content")
                        ),
                        {},
                    )
                    policies.append(
                        {
                            "url": url,
                            "title": page.get("name"),
                            "html": page.get("content"),
                            "source": source,
                            "verification_status": "awaiting_review",
                        }
                    )
            except (ValueError, OSError, KeyError, PermissionError) as error:
                failures.append({"url": url, "phase": "index", "error": type(error).__name__})
            except Exception as error:
                failures.append({"url": url, "phase": "index", "error": type(error).__name__})

        # Follow actual hrefs, including opaque URL IDs. Never infer degree type from URL text.
        pending = sorted(discovered_programs)
        visited = set()
        while pending:
            url = pending.pop(0)
            inventory[url] = {"kind": "program", "url": url, "status": "awaiting_review"}
            if max_programs and len(visited) >= max_programs:
                inventory[url]["reason"] = "crawl_limit"
                continue
            visited.add(url)
            try:
                html, source = load(url)
                record, _, parser = record_from_page(html, "program", year)
                normalized = normalize("program", record, source, year)
                key = normalized["external_id"]
                if key in programs and programs[key]["content_hash"] != normalized["content_hash"]:
                    failures.append(
                        {"url": url, "phase": "program", "error": "conflicting_identity"}
                    )
                else:
                    programs[key] = normalized
                inventory[url].update(
                    status="staged_awaiting_review", external_id=key, code=normalized["code"]
                )
                for link in parser.links:
                    if program_link(link["href"]):
                        linked = approved_url(link["href"])
                        if linked not in discovered_programs:
                            discovered_programs.add(linked)
                            pending.append(linked)
                pending.sort()
            except Exception as error:
                inventory[url]["reason"] = type(error).__name__
                failures.append({"url": url, "phase": "program", "error": type(error).__name__})
            if len(visited) % 10 == 0:
                LOGGER.info(
                    json.dumps(
                        {
                            "event": "program_progress",
                            "visited": len(visited),
                            "staged": len(programs),
                            "remaining": len(pending),
                        }
                    )
                )

        # PDF heading detection discovers candidates only; a candidate is not a verified course.
        candidate_codes = set(pdf_codes)
        for program in programs.values():
            candidate_codes.update(program["course_references"])
        priority = [
            "BIOL2110L",
            "BIOL2610L",
            "BIOL2110",
            "BIOL2610",
            "BIOL2141",
            "BIOL5079",
            "BIOL5082",
            "BIOL5001",
            "BIOL5090",
        ]
        pending_codes = [c for c in priority if c in candidate_codes]
        pending_codes += sorted(candidate_codes - set(pending_codes))
        visited_codes = set()
        while pending_codes:
            code = pending_codes.pop(0)
            url = ORIGIN + "/courses/" + quote(code, safe="")
            entry = {
                "kind": "course",
                "code": code,
                "url": url,
                "discovery_method": "pdf_heading_candidate"
                if code in pdf_codes
                else "official_program_rule",
                "pdf_evidence": pdf_codes.get(code, []),
                "status": "awaiting_review",
            }
            inventory[url] = entry
            if max_courses and len(visited_codes) >= max_courses:
                entry["reason"] = "crawl_limit"
                continue
            visited_codes.add(code)
            try:
                html, source = load(url)
                record, _, _ = record_from_page(html, "course", year)
                normalized = normalize("course", record, source, year)
                if normalized["code"] != code:
                    raise ValueError("Course URL and official code disagree")
                normalized["pdf_evidence"] = pdf_codes.get(code, [])
                courses[code] = normalized
                entry.update(status="staged_awaiting_review", external_id=normalized["external_id"])
                for dependency in normalized["course_references"]:
                    if dependency not in candidate_codes:
                        candidate_codes.add(dependency)
                        pending_codes.append(dependency)
            except Exception as error:
                entry["reason"] = type(error).__name__
                failures.append({"url": url, "phase": "course", "error": type(error).__name__})

        # Candidate page matching is not proof of cross-source field agreement.
        for program in programs.values():
            needle = plain(program["title"]).casefold()
            program["pdf_candidate_pages"] = [
                {k: p[k] for k in ("pdf_page_index", "pdf_page_number", "printed_page", "sha256")}
                for p in pdf_pages
                if needle in re.sub(r"\s+", " ", p["text"]).casefold()
            ]
            program["cross_source_verification"] = "pending_field_by_field_review"
        stage = {
            "format_version": 1,
            "institution": {
                "official_name": "New Mexico Institute of Mining and Technology",
                "display_name": "New Mexico Tech",
                "abbreviation": "NMT",
                "city": "Socorro",
                "state": "New Mexico",
                "state_code": "NM",
                "country": "USA",
                "website": "https://www.nmt.edu/",
                "catalog": ORIGIN + "/",
            },
            "catalog_year": year,
            "pdf_manifest": pdf_manifest,
            "programs": sorted(programs.values(), key=lambda r: (r["code"], r["external_id"])),
            "courses": sorted(courses.values(), key=lambda r: r["code"]),
            "departments": sorted(departments.values(), key=lambda r: r["code"]),
            "institution_requirements": sorted(policies, key=lambda r: r["url"]),
            "discovery_inventory": sorted(inventory.values(), key=lambda r: r["url"]),
            "sources": sorted(source_pages.values(), key=lambda r: r["url"]),
            "failures": sorted(failures, key=lambda r: (r["url"], r["phase"])),
            "coverage": {
                "degrees_index_program_links": len(discovered_programs),
                "pdf_course_code_candidates": len(pdf_codes),
                "programs_pathways_index": "client_rendered_list_not_exhaustively_cross_checked",
                "courses_index": "client_rendered_list_not_exhaustively_cross_checked",
                "errata": "not_yet_independently_verified",
                "discovery_complete": False,
            },
            "publication_status": "blocked_schema_history_and_academic_review",
        }
        stage["stage_hash"] = canonical_hash(stage)
        save_json(output / "staged-catalog.json", stage)
        report = validation_report(stage)
        save_json(output / "validation-report.json", report)
        save_json(
            output / "source-conflicts.json",
            [
                {"code": r["code"], "source": r["source"], "conflicts": r["conflicts"]}
                for r in stage["programs"] + stage["courses"]
                if r["conflicts"]
            ],
        )
        return stage, report
    finally:
        client.close()


def validation_report(stage):
    records = stage["programs"] + stage["courses"]
    course_codes = {r["code"] for r in stage["courses"]}
    unresolved = [
        {"record_kind": r["kind"], "record_code": r["code"], "reference": code}
        for r in records
        for code in r["course_references"]
        if code not in course_codes
    ]
    review_rules = [
        {
            "record_kind": r["kind"],
            "code": r["code"],
            "reason": n.get("reason"),
            "source_id": n.get("source_id"),
        }
        for r in records
        for n in walk(r["requirement_tree"])
        if isinstance(n, dict) and n.get("op") == "REVIEW"
    ]
    plans = [p for r in stage["programs"] for p in r["sample_plans"]]
    return {
        "catalog_year": stage["catalog_year"],
        "stage_hash": stage["stage_hash"],
        "programs_staged": len(stage["programs"]),
        "courses_staged": len(stage["courses"]),
        "departments_staged": len(stage["departments"]),
        "programs_by_degree_designation": dict(
            sorted(Counter(r["degree_designation"] or "unknown" for r in stage["programs"]).items())
        ),
        "programs_by_category": dict(
            sorted(Counter(str(r["category"] or "unknown") for r in stage["programs"]).items())
        ),
        "sample_plans_staged_unverified": len(plans),
        "programs_without_official_sample_plan": [
            r["code"] for r in stage["programs"] if not r["sample_plans"]
        ],
        "source_conflict_count": sum(len(r["conflicts"]) for r in records),
        "unresolved_course_references": unresolved,
        "unsupported_rules_for_review": review_rules,
        "records_awaiting_review": len(records),
        "source_failures": stage["failures"],
        "discovery": stage["coverage"],
        "inventory_statuses": dict(Counter(r["status"] for r in stage["discovery_inventory"])),
        "database_rows_inserted": 0,
        "database_rows_updated": 0,
        "database_apply_executed": False,
        "production_ready": False,
        "blocking_issues": [
            "Database migration history 0011-0014 is absent locally",
            "Official errata and field-level HTML/PDF conflicts need review",
            "Client-rendered index completeness has not been verified",
            "Existing planner does not evaluate all NMT rule semantics",
        ],
    }
