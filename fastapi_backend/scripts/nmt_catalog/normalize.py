"""Conservative academic normalization. Unsupported semantics remain explicit review nodes."""

from __future__ import annotations

import hashlib
import json
import re
from decimal import Decimal, InvalidOperation

from .sources import PageParser

COURSE_CODE = re.compile(r"[A-Z][A-Z& ]{1,9}\d{3,4}[A-Z]{0,3}\Z")
PLACEHOLDERS = {"undefined", "untitled course set", "program", "course", "null"}
ACADEMIC_FIELDS = (
    "id",
    "_id",
    "code",
    "programGroupId",
    "courseGroupId",
    "name",
    "longName",
    "catalogDisplayName",
    "catalogDescription",
    "catalogFullDescription",
    "description",
    "degreeDesignation",
    "degreeDesignations",
    "level",
    "type",
    "departments",
    "information",
    "policies",
    "learningOutcomes",
    "specializations",
    "degreeMaps",
    "requisites",
    "requirementLevels",
    "credits",
    "courseLevel",
    "subjectCode",
    "courseNumber",
    "equivalent",
    "crossListedCourses",
    "courseEquivalencies",
    "effectiveStartDate",
    "effectiveEndDate",
    "notes",
)


def clean(value):
    return re.sub(r"\s+", " ", value).strip() if isinstance(value, str) else value


def plain(value):
    if not isinstance(value, str):
        return ""
    return clean(" ".join(PageParser(value).text))


def valid_name(value):
    return (
        isinstance(value, str) and bool(clean(value)) and clean(value).lower() not in PLACEHOLDERS
    )


def canonical_hash(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def decimal_value(value):
    if isinstance(value, bool) or value in (None, ""):
        return None
    try:
        parsed = Decimal(str(value))
        return format(parsed.normalize(), "f") if parsed.is_finite() and parsed >= 0 else None
    except InvalidOperation:
        return None


def credit_range(raw):
    if not isinstance(raw, dict):
        return {"min": None, "max": None, "raw": raw}
    return {
        "min": decimal_value(raw.get("min")),
        "max": decimal_value(raw.get("max")),
        "operator": raw.get("operator"),
        "raw": raw,
    }


def raw_academics(record):
    # Department staff/contact data and editing identities are not needed by this importer.
    result = {key: record[key] for key in ACADEMIC_FIELDS if key in record}
    if isinstance(result.get("departments"), list):
        result["departments"] = [
            d
            if isinstance(d, str)
            else {key: d[key] for key in ("id", "name", "displayName", "subjectCodes") if key in d}
            for d in result["departments"]
        ]
    return result


def selection_node(raw):
    """Only course-code selections with explicit AND/OR connectors are executable.

    courseSets IDs and generic elective placeholders are NEVER turned into courses.
    """
    if not isinstance(raw, dict) or raw.get("condition") != "courses":
        return {
            "op": "REVIEW",
            "reason": "non-course selection or unresolved course set",
            "raw": raw,
        }
    if raw.get("subSelections"):
        return {"op": "REVIEW", "reason": "nested sub-selection needs semantic review", "raw": raw}
    groups = []
    for group in raw.get("values", []):
        codes = group.get("value", [])
        logic = group.get("logic")
        if not isinstance(codes, list) or not codes or logic not in {"and", "or"}:
            return {"op": "REVIEW", "reason": "ambiguous selection connector", "raw": raw}
        if any(not isinstance(code, str) or not COURSE_CODE.fullmatch(code) for code in codes):
            return {
                "op": "REVIEW",
                "reason": "course identifier is not an official code",
                "raw": raw,
            }
        groups.append(
            {
                "op": "ALL" if logic == "and" else "ANY",
                "children": [{"op": "COURSE", "code": code} for code in codes],
            }
        )
    return {"op": "SELECTION", "groups": groups, "raw": raw}


def rule_node(rule):
    condition = rule.get("condition")
    node = {"source_id": rule.get("id"), "name": clean(rule.get("name", "")), "raw": rule}
    selection = selection_node(rule.get("value"))
    groups = selection.get("groups", [])
    if condition == "completedAllOf" and selection["op"] == "SELECTION":
        node.update(op="ALL", children=groups)
    elif condition == "enrolledIn" and selection["op"] == "SELECTION":
        node.update(op="ENROLLED", children=groups)
    elif condition == "completedAtLeastXOf" and selection["op"] == "SELECTION":
        # Counting unions/combination groups is not safely equivalent to counting courses.
        count = rule.get("restriction")
        if (
            isinstance(count, int)
            and count >= 1
            and all(g["op"] == "ANY" or len(g["children"]) == 1 for g in groups)
        ):
            node.update(
                op="AT_LEAST", count=count, children=[c for g in groups for c in g["children"]]
            )
        else:
            node.update(op="REVIEW", reason="ambiguous count/group semantics")
    elif condition == "minimumCredits" and selection["op"] == "SELECTION":
        credits = decimal_value(rule.get("credits"))
        if credits is not None:
            node.update(op="MIN_CREDITS", credits=credits, eligible_groups=groups)
        else:
            node.update(op="REVIEW", reason="unknown credit minimum")
    else:
        node.update(op="REVIEW", reason=selection.get("reason", "unsupported rule condition"))
    # Restrictions cannot be discarded just because the course selection was parsed.
    allowed = {
        "id",
        "condition",
        "value",
        "name",
        "sisId",
        "credits",
        "minCredits",
        "restriction",
        "description",
        "notes",
    }
    extra = {k: v for k, v in rule.items() if k not in allowed and v not in (None, "", [], {})}
    if extra:
        node["op"] = "REVIEW"
        node["reason"] = "additional restrictions require review"
        node["restrictions"] = extra
    return node


def requirement_tree(record):
    raw = record.get("requisites") or {}
    groups = []
    for group in raw.get("requisitesSimple", []):
        if group.get("showInCatalog") is False:
            continue
        label = (str(group.get("name", "")) + " " + str(group.get("type", ""))).lower()
        timing = (
            "before_or_concurrent"
            if re.search(r"pre\s*(?:or|/|-)\s*co", label)
            else "concurrent"
            if "corequisite" in label
            else "before"
            if "prerequisite" in label
            else None
        )
        groups.append(
            {
                "op": "GROUP",
                "source_id": group.get("id"),
                "name": group.get("name"),
                "timing": timing,
                "requirement_level": group.get("requirementLevel"),
                "raw": group,
                "children": [rule_node(r) for r in group.get("rules", [])],
            }
        )
    for key in ("requisitesAdvanced", "requisitesFreeform"):
        value = raw.get(key)
        if value and not (isinstance(value, dict) and value.get("showInCatalog") is False):
            groups.append({"op": "REVIEW", "reason": key, "raw": value})
    return {"op": "CATALOG_RULES", "children": groups}


def walk(value):
    yield value
    if isinstance(value, dict):
        for key, child in value.items():
            if key != "raw":
                yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def course_references(record):
    refs = set()

    def visit(value):
        if isinstance(value, dict):
            if value.get("condition") == "courses":
                for group in value.get("values", []):
                    refs.update(
                        c
                        for c in group.get("value", [])
                        if isinstance(c, str) and COURSE_CODE.fullmatch(c)
                    )
            if value.get("type") == "courses":
                choices = value.get("value", [])
                choices = [choices] if isinstance(choices, str) else choices
                if isinstance(choices, list):
                    refs.update(
                        c for c in choices if isinstance(c, str) and COURSE_CODE.fullmatch(c)
                    )
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(record.get("requisites", {}))
    visit(record.get("degreeMaps", []))
    for key in ("description", "catalogDescription", "information", "notes"):
        for link in PageParser(record.get(key) or "").links:
            if link["href"].startswith("/courses/"):
                code = link["href"].split("/courses/", 1)[1].split("#", 1)[0]
                if COURSE_CODE.fullmatch(code):
                    refs.add(code)
    return sorted(refs)


def internal_conflicts(record):
    conflicts = []
    for group in (record.get("requisites") or {}).get("requisitesSimple", []):
        for rule in group.get("rules", []):
            text = plain(rule.get("value"))
            match = re.search(r"(?:minimum of|at least)\s+(\d+(?:\.\d+)?)\s+credits?", text, re.I)
            numeric = decimal_value(rule.get("credits"))
            if match and numeric is not None and Decimal(match[1]) != Decimal(numeric):
                conflicts.append(
                    {
                        "field": "requirement_credits",
                        "rule_id": rule.get("id"),
                        "visible_text": text,
                        "structured_credits": numeric,
                        "status": "conflicting",
                        "resolution": None,
                    }
                )
    return conflicts


def normalize(kind, record, source, catalog_year):
    title = record.get("longName") or record.get("catalogDisplayName") or record.get("name")
    code = record.get("code")
    external_id = record.get("id") or record.get("_id")
    if not valid_name(title) or not isinstance(code, str) or not code.strip() or not external_id:
        raise ValueError("Record lacks stable identity, official code, or meaningful title")
    if kind == "course" and not COURSE_CODE.fullmatch(code):
        raise ValueError("Course code is a placeholder or an unsupported identifier")
    tree = requirement_tree(record)
    academic = raw_academics(record)
    departments = [
        d if isinstance(d, str) else d.get("id") for d in academic.get("departments", [])
    ]
    result = {
        "kind": kind,
        "institution": "NMT",
        "catalog_year": catalog_year,
        "external_id": external_id,
        "code": code,
        "title": clean(title),
        "display_title": clean(record.get("catalogDisplayName") or title),
        "description": plain(record.get("catalogDescription") or record.get("description")) or None,
        "departments": [d for d in departments if d],
        "source": source,
        "requirement_tree": tree,
        "course_references": course_references(record),
        "raw_academic_record": academic,
        "conflicts": internal_conflicts(record),
        "verification_status": "awaiting_review",
        "publication_status": "staged_only",
    }
    if kind == "program":
        info = plain(record.get("information"))
        policy = plain(record.get("policies"))
        policy_variants = [
            {"source_field": field, "text": text}
            for field, text in (("information", info), ("policies", policy))
            if text
        ]
        policy_conflict = bool(info and policy and info != policy)
        minimum = re.search(r"minimum credit hours required\s*[^\w]*\s*(\d+(?:\.\d+)?)", info, re.I)
        result.update(
            degree_designation=clean(record.get("degreeDesignation")) or None,
            category=record.get("type") or None,
            academic_level=record.get("level") or None,
            minimum_credits=decimal_value(minimum[1]) if minimum else None,
            policies=None if policy_conflict else info or policy or None,
            policy_variants=policy_variants,
            learning_outcomes=record.get("learningOutcomes") or None,
            specializations=record.get("specializations") or [],
            sample_plans=record.get("degreeMaps") or [],
            sample_plan_status="available_unverified"
            if record.get("degreeMaps")
            else "unavailable",
        )
        if policy_conflict:
            result["conflicts"].append(
                {
                    "field": "policies",
                    "values": policy_variants,
                    "status": "differing_source_fields_require_review",
                    "resolution": None,
                }
            )
    else:
        credits = record.get("credits") or {}
        result.update(
            credits=credit_range(credits.get("creditHours")),
            lecture_hours=credit_range(credits.get("lectureHours")),
            lab_hours=credit_range(credits.get("labHours")),
            academic_level=record.get("courseLevel") or None,
            equivalents=record.get("equivalent") or None,
        )
    result["content_hash"] = canonical_hash({k: v for k, v in result.items() if k != "source"})
    return result
