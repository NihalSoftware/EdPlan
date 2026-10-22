"""Read-only proposals. Weak names NEVER authorize updates or insertions."""

from __future__ import annotations

import re
from urllib.parse import urlsplit

from .normalize import clean


def match_record(source, existing):
    same_parent = [
        row
        for row in existing
        if row.get("institution") == source["institution"]
        and row.get("catalog_year") == source["catalog_year"]
    ]
    fields = (
        ("external_id", "stable_official_id"),
        ("code", "exact_official_code"),
        ("source_url", "exact_official_source_url"),
    )
    for field, method in fields:
        value = source["source"]["url"] if field == "source_url" else source.get(field)
        matches = [row for row in same_parent if value and row.get(field) == value]
        if matches:
            if len(matches) > 1:
                return {
                    "action": "review",
                    "confidence": "low",
                    "method": method,
                    "reason": "duplicate_existing_identity",
                    "matches": matches,
                }
            return {
                "action": "prepare_update",
                "confidence": "high",
                "method": method,
                "record_id": matches[0]["record_id"],
            }
    normalized = clean(source["title"]).casefold()
    matches = [
        row
        for row in same_parent
        if clean(row.get("title", "")).casefold() == normalized
        and set(row.get("departments", [])) & set(source.get("departments", []))
    ]
    if matches:
        return {
            "action": "review",
            "confidence": "medium",
            "method": "exact_name_and_department",
            "matches": matches,
        }
    unversioned = [
        row
        for row in existing
        if row.get("institution") == source["institution"]
        and row.get("catalog_year") != source["catalog_year"]
        and (
            row.get("code") == source.get("code")
            or clean(row.get("title", "")).casefold() == normalized
        )
    ]
    if unversioned:
        return {
            "action": "review",
            "confidence": "low",
            "method": "unversioned_or_other_catalog",
            "reason": "existing_identity_cannot_be_safely_migrated",
            "matches": unversioned,
        }
    return {
        "action": "proposed_insertion",
        "confidence": "high",
        "method": "new_stable_identity",
        "requires_schema_and_academic_review": True,
    }


def merge_nonempty(old, proposed):
    """For reviewed future application only. Never erase known values with unknown ones."""
    merged = dict(old)
    for key, value in proposed.items():
        if value is None or value == "" or value == [] or value == {}:
            continue
        if isinstance(value, dict) and isinstance(old.get(key), dict):
            merged[key] = merge_nonempty(old[key], value)
        else:
            merged[key] = value
    return merged


def baseline_program_rows(baseline):
    rows = []
    for row in baseline.get("existing_nmt_programs", []):
        metadata = row.get("metadata_json") or {}
        if isinstance(metadata, str):
            import json

            metadata = json.loads(metadata)
        url = row.get("official_source_url") or metadata.get("source_url")
        code = metadata.get("official_program_code") or metadata.get("program_code")
        # Stable URLs are useful suggestions, but not a catalog version assertion.
        if not code and url and urlsplit(url).hostname == "catalog.nmt.edu":
            slug = urlsplit(url).path.rsplit("/", 1)[-1]
            if re.fullmatch(r"(?:BS|BA|MS|ME|PHD|PM|UC|GC)-[A-Z .&-]+", slug):
                code = slug
        rows.append(
            {
                "record_id": str(row["program_id"]),
                "institution": "NMT",
                "catalog_year": metadata.get("catalog_year"),
                "code": code,
                "external_id": row.get("official_source_id"),
                "source_url": url,
                "title": row["program_name"],
                "departments": metadata.get("department_codes") or [],
            }
        )
    return rows


def dry_run_report(stage, baseline):
    existing = baseline_program_rows(baseline)
    proposed = [
        {
            "kind": "program",
            "code": row["code"],
            "source": row["source"],
            **match_record(row, existing),
        }
        for row in stage["programs"]
    ]
    # Do not pretend to match legacy program-scoped courses to canonical versioned courses.
    proposed += [
        {
            "kind": "course",
            "code": row["code"],
            "source": row["source"],
            "action": "review",
            "confidence": "low",
            "method": "legacy_course_model_incompatible",
            "reason": "requires institution/catalog identity and program-course bridge",
        }
        for row in stage["courses"]
    ]
    return {
        "mode": "dry_run_only",
        "schema_history_aligned": baseline.get("schema_history_aligned"),
        "existing_nmt_program_count": len(existing),
        "proposals": proposed,
        "rows_inserted": 0,
        "rows_updated": 0,
        "rows_deleted": 0,
        "records_not_found_in_latest_crawl": (
            "not classified as absent: crawl coverage is incomplete"
        ),
        "protected_fingerprints_before": baseline.get("protected_fingerprints"),
        "apply_blocked": True,
    }
