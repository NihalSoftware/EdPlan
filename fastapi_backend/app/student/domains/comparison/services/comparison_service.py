from __future__ import annotations

import re
import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.student.domains.comparison.repositories.comparison_repository import (
    ComparisonRepository,
    comparison_repository,
)


class ComparisonService:
    def __init__(self, repository: ComparisonRepository = comparison_repository) -> None:
        self.repository = repository

    async def search_universities(
        self,
        db: AsyncSession,
        *,
        state: str | None = None,
        city: str | None = None,
        name: str | None = None,
        limit: int = 10,
    ) -> dict:
        _validate_search_filters(state=state, city=city, name=name)
        universities = await self.repository.search_universities(
            db,
            state=_clean_optional(state),
            city=_clean_optional(city),
            name=_clean_optional(name),
            limit=_limit(limit),
        )
        return {"results": universities, "metadata": {"count": len(universities), "source": "edplan_database"}}

    async def compare_universities(self, db: AsyncSession, university_ids: list[str]) -> dict:
        ids = _validate_id_list(university_ids, "university_ids", minimum=2, maximum=5)
        universities = await self.repository.get_universities_by_ids(db, ids)
        return {
            "universities": universities,
            "metadata": {
                "requested_count": len(ids),
                "found_count": len(universities),
                "unavailable_fields": ["rankings", "tuition", "placement_rates", "acceptance_rates", "scholarships"],
            },
        }

    async def search_programs(
        self,
        db: AsyncSession,
        *,
        university_id: str | None = None,
        degree: str | None = None,
        name: str | None = None,
        limit: int = 20,
    ) -> dict:
        if university_id is not None:
            _validate_uuid(university_id, "university_id")
        if degree is None and name is None and university_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one program search filter is required")
        programs = await self.repository.search_programs(
            db,
            university_id=_clean_optional(university_id),
            degree=_clean_optional(degree),
            name=_clean_optional(name),
            limit=_limit(limit),
        )
        return {"results": programs, "metadata": {"count": len(programs), "source": "edplan_database"}}

    async def compare_programs(self, db: AsyncSession, program_ids: list[str]) -> dict:
        ids = _validate_id_list(program_ids, "program_ids", minimum=2, maximum=6)
        programs = await self.repository.get_programs_by_ids(db, ids)
        careers_by_program = await self.repository.get_careers_for_programs(db, ids)
        for program in programs:
            program["available_careers"] = careers_by_program.get(program["program_id"], [])
        return {
            "programs": programs,
            "metadata": {
                "requested_count": len(ids),
                "found_count": len(programs),
                "unavailable_fields": ["rankings", "salaries", "placement_rates", "tuition"],
            },
        }

    async def compare_career_paths(self, db: AsyncSession, program_ids: list[str]) -> dict:
        ids = _validate_id_list(program_ids, "program_ids", minimum=2, maximum=6)
        careers_by_program = await self.repository.get_careers_for_programs(db, ids)
        career_sets = {
            program_id: {career["career_id"] for career in careers}
            for program_id, careers in careers_by_program.items()
        }
        overlap_ids = set.intersection(*career_sets.values()) if career_sets else set()
        all_careers = {
            career["career_id"]: career
            for careers in careers_by_program.values()
            for career in careers
        }
        unique_by_program = {
            program_id: [career for career in careers if career["career_id"] not in overlap_ids]
            for program_id, careers in careers_by_program.items()
        }
        return {
            "mapped_careers": careers_by_program,
            "overlapping_careers": [all_careers[career_id] for career_id in sorted(overlap_ids, key=lambda value: all_careers[value]["career_name"])],
            "unique_careers": unique_by_program,
            "metadata": {
                "source_tables": ["careers", "program_careers", "course_careers"],
                "message": None if any(careers_by_program.values()) else "Career mapping information is not available in the current EdPlan database.",
            },
        }

    async def build_advising_comparison(
        self,
        db: AsyncSession,
        *,
        student_context: dict[str, Any],
        query: str,
    ) -> dict[str, Any]:
        """Build deterministic UniversityAdvisor comparison output from existing data."""
        program_name = _program_name(student_context, query)
        university_names = _requested_university_names(query)
        universities = await self._resolve_universities(
            db,
            names=university_names,
            student_context=student_context,
        )
        programs = await self._resolve_programs(
            db,
            universities=universities,
            program_name=program_name,
        )
        universities = _unique_by(
            [*universities, *_universities_from_programs(programs)],
            "university_id",
        )

        if len(universities) < 2 and len(programs) < 2:
            return _needs_context_response(
                student_context=student_context,
                query=query,
                missing=["universities_or_programs_to_compare"],
            )

        compared_program_ids = [program["program_id"] for program in programs[:6]]
        career_paths = (
            await self.compare_career_paths(db, compared_program_ids)
            if len(compared_program_ids) >= 2
            else {"mapped_careers": {}, "overlapping_careers": [], "unique_careers": {}}
        )
        comparison_table = _comparison_table(universities, programs, career_paths)
        ranked = _rank_recommendations(
            universities=universities,
            programs=programs,
            student_context=student_context,
            query=query,
            career_paths=career_paths,
        )
        recommended = ranked[0] if ranked else None
        validation = _validation(universities, programs, comparison_table)
        warnings = list(validation["warnings"])
        unavailable_fields = _unavailable_fields(comparison_table)
        if unavailable_fields:
            warnings.append(
                "Some requested fields are unavailable in the current EdPlan database: "
                + ", ".join(unavailable_fields)
                + "."
            )

        return {
            "summary": {
                "status": "ready",
                "query": query,
                "university_count": len(universities),
                "program_count": len(programs),
                "recommended_university": (
                    recommended.get("university_name") if recommended else None
                ),
                "program_focus": program_name,
            },
            "student_context": student_context,
            "universities": universities,
            "programs": programs,
            "recommended_university": recommended,
            "comparison_table": comparison_table,
            "ranked_recommendations": ranked,
            "pros": _pros(ranked, programs),
            "cons": _cons(comparison_table),
            "advisor_notes": [],
            "recommendations": _recommendation_notes(ranked, warnings),
            "validation": validation,
            "warnings": _unique_strings(warnings),
            "career_paths": career_paths,
            "multi_agent_context": _multi_agent_context(student_context),
        }

    async def _resolve_universities(
        self,
        db: AsyncSession,
        *,
        names: list[str],
        student_context: dict[str, Any],
    ) -> list[dict[str, Any]]:
        universities: list[dict[str, Any]] = []
        for name in names:
            search = await self.search_universities(db, name=_alias(name), limit=3)
            universities.extend(search["results"])

        context_university = student_context.get("university")
        context_university_id = (
            context_university.get("university_id")
            if isinstance(context_university, dict)
            else None
        )
        if context_university_id:
            universities.extend(
                await self.repository.get_universities_by_ids(db, [context_university_id])
            )

        return _unique_by(universities, "university_id")

    async def _resolve_programs(
        self,
        db: AsyncSession,
        *,
        universities: list[dict[str, Any]],
        program_name: str | None,
    ) -> list[dict[str, Any]]:
        programs: list[dict[str, Any]] = []
        for university in universities:
            university_id = university.get("university_id")
            if not university_id:
                continue
            search = await self.search_programs(
                db,
                university_id=university_id,
                name=program_name,
                limit=5,
            )
            programs.extend(search["results"])
        if len(programs) >= 2:
            return (await self.compare_programs(db, [program["program_id"] for program in programs[:6]]))[
                "programs"
            ]
        if program_name:
            search = await self.search_programs(db, name=program_name, limit=6)
            if len(search["results"]) >= 2:
                return (await self.compare_programs(db, [program["program_id"] for program in search["results"][:6]]))[
                    "programs"
                ]
        return programs


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    return cleaned


def _validate_search_filters(**filters: str | None) -> None:
    if not any(_clean_optional(value) for value in filters.values()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one university search filter is required")


def _validate_id_list(values: list[str], field_name: str, *, minimum: int, maximum: int) -> list[str]:
    if len(values) < minimum:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"At least {minimum} {field_name} are required")
    selected = values[:maximum]
    for value in selected:
        _validate_uuid(value, field_name.rstrip("s"))
    return selected


def _validate_uuid(value: str, field_name: str) -> None:
    try:
        uuid.UUID(str(value))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid {field_name}") from exc


def _limit(value: int) -> int:
    if value < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="limit must be greater than or equal to 1")
    return min(value, 50)


def _needs_context_response(
    *,
    student_context: dict[str, Any],
    query: str,
    missing: list[str],
) -> dict[str, Any]:
    return {
        "summary": {
            "status": "needs_context",
            "query": query,
            "university_count": 0,
            "program_count": 0,
            "recommended_university": None,
            "program_focus": _program_name(student_context, query),
        },
        "student_context": student_context,
        "universities": [],
        "programs": [],
        "recommended_university": None,
        "comparison_table": [],
        "ranked_recommendations": [],
        "pros": [],
        "cons": [],
        "advisor_notes": [],
        "recommendations": [
            "Please name at least two universities or a program you want to compare."
        ],
        "validation": {
            "status": "needs_context",
            "missing": missing,
            "warnings": [],
        },
        "warnings": [],
        "career_paths": {"mapped_careers": {}, "overlapping_careers": [], "unique_careers": {}},
        "multi_agent_context": _multi_agent_context(student_context),
    }


def _requested_university_names(query: str) -> list[str]:
    normalized = " ".join(query.replace("?", " ").split())
    patterns = [
        r"compare\s+(.+?)\s+(?:vs|versus|and|with|to)\s+(.+)",
        r"(.+?)\s+(?:vs|versus)\s+(.+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, normalized, flags=re.IGNORECASE)
        if not match:
            continue
        names = [_clean_name(match.group(1)), _clean_name(match.group(2))]
        return [name for name in names if name]
    aliases = []
    lowered = normalized.lower()
    for alias in UNIVERSITY_ALIASES:
        if alias.lower() in lowered:
            aliases.append(alias)
    return aliases


def _clean_name(value: str) -> str:
    cleaned = re.sub(
        r"\b(for|program|computer science|cs|tuition|transfer|pathway|best|cheapest)\b",
        " ",
        value,
        flags=re.IGNORECASE,
    )
    return " ".join(cleaned.strip(" .,:;").split())


def _program_name(student_context: dict[str, Any], query: str) -> str | None:
    lowered = query.lower()
    program = student_context.get("program")
    if isinstance(program, dict):
        value = program.get("program_name") or program.get("name")
        if value:
            return str(value)
    known_programs = (
        "computer science",
        "data science",
        "engineering",
        "business",
        "nursing",
        "artificial intelligence",
        "ai",
    )
    for name in known_programs:
        if name in lowered:
            return "Artificial Intelligence" if name == "ai" else name.title()
    return None


UNIVERSITY_ALIASES = {
    "NNMC": "Northern New Mexico College",
    "SFCC": "Santa Fe Community College",
    "UNM": "University of New Mexico",
    "NMSU": "New Mexico State University",
    "SENMC": "Southeast New Mexico College",
}


def _alias(name: str) -> str:
    return UNIVERSITY_ALIASES.get(name.upper(), name)


def _comparison_table(
    universities: list[dict[str, Any]],
    programs: list[dict[str, Any]],
    career_paths: dict[str, Any],
) -> list[dict[str, Any]]:
    programs_by_university: dict[str, list[dict[str, Any]]] = {}
    for program in programs:
        university = program.get("university") if isinstance(program.get("university"), dict) else {}
        university_id = university.get("university_id")
        if university_id:
            programs_by_university.setdefault(university_id, []).append(program)

    rows = []
    for university in universities:
        university_programs = programs_by_university.get(university["university_id"], [])
        credits = [
            program.get("total_credit_hours")
            for program in university_programs
            if isinstance(program.get("total_credit_hours"), int)
        ]
        career_count = sum(
            len(career_paths.get("mapped_careers", {}).get(program.get("program_id"), []))
            for program in university_programs
        )
        rows.append(
            {
                "university_id": university["university_id"],
                "university_name": university["university_name"],
                "city": university.get("city"),
                "state": university.get("state"),
                "website": university.get("website"),
                "program_count": university.get("program_count", 0),
                "matching_programs": [
                    {
                        "program_id": program["program_id"],
                        "program_name": program["program_name"],
                        "degree": program["degree"],
                        "total_credit_hours": program.get("total_credit_hours"),
                        "course_count": program.get("course_count"),
                    }
                    for program in university_programs
                ],
                "lowest_matching_credits": min(credits) if credits else None,
                "curriculum_course_count": sum(
                    program.get("course_count") or 0 for program in university_programs
                ),
                "career_mapping_count": career_count,
                "tuition": None,
                "transfer_agreements": None,
                "delivery_mode": None,
                "institution_type": university.get("public_private"),
            }
        )
    return rows


def _universities_from_programs(programs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    universities = []
    for program in programs:
        university = program.get("university")
        if not isinstance(university, dict) or not university.get("university_id"):
            continue
        universities.append(
            {
                "university_id": university["university_id"],
                "university_name": university.get("university_name") or university.get("name"),
                "city": university.get("city"),
                "state": university.get("state"),
                "website": university.get("website"),
                "program_count": None,
                "public_private": university.get("public_private"),
            }
        )
    return universities


def _rank_recommendations(
    *,
    universities: list[dict[str, Any]],
    programs: list[dict[str, Any]],
    student_context: dict[str, Any],
    query: str,
    career_paths: dict[str, Any],
) -> list[dict[str, Any]]:
    table = _comparison_table(universities, programs, career_paths)
    lowered_query = query.lower()
    preferred_state = None
    context_university = student_context.get("university")
    if isinstance(context_university, dict):
        preferred_state = context_university.get("state")
    rankings = []
    for row in table:
        score = 0
        reasons = []
        if row["matching_programs"]:
            score += 40
            reasons.append("offers matching program data")
        if row["lowest_matching_credits"] is not None:
            score += max(0, 30 - abs(row["lowest_matching_credits"] - 120) / 4)
            reasons.append("has comparable degree-credit requirements")
        if row["career_mapping_count"]:
            score += min(15, row["career_mapping_count"] * 3)
            reasons.append("has mapped career pathways")
        if preferred_state and row.get("state") == preferred_state:
            score += 5
            reasons.append("matches current state context")
        if "cheap" in lowered_query or "tuition" in lowered_query:
            reasons.append("tuition ranking unavailable in current database")
        rankings.append(
            {
                "rank": 0,
                "university_id": row["university_id"],
                "university_name": row["university_name"],
                "score": round(score, 2),
                "reasons": reasons or ["limited comparable data available"],
                "programs": row["matching_programs"],
                "unavailable_fields": _row_unavailable_fields(row),
            }
        )
    rankings.sort(key=lambda item: (-item["score"], item["university_name"]))
    for index, item in enumerate(rankings, start=1):
        item["rank"] = index
    return rankings


def _validation(
    universities: list[dict[str, Any]],
    programs: list[dict[str, Any]],
    comparison_table: list[dict[str, Any]],
) -> dict[str, Any]:
    warnings = []
    if len(universities) < 2:
        warnings.append("Fewer than two universities were resolved from the request.")
    if not programs:
        warnings.append("No matching programs were found for the resolved universities.")
    if any(not row["matching_programs"] for row in comparison_table):
        warnings.append("At least one university has no matching program in the current catalog.")
    return {
        "status": "warning" if warnings else "valid",
        "warnings": warnings,
        "university_count": len(universities),
        "program_count": len(programs),
        "table_row_count": len(comparison_table),
    }


def _unavailable_fields(comparison_table: list[dict[str, Any]]) -> list[str]:
    unavailable = []
    for row in comparison_table:
        unavailable.extend(_row_unavailable_fields(row))
    return _unique_strings(unavailable)


def _row_unavailable_fields(row: dict[str, Any]) -> list[str]:
    return [
        field
        for field in ("tuition", "transfer_agreements", "delivery_mode", "institution_type")
        if row.get(field) is None
    ]


def _pros(ranked: list[dict[str, Any]], programs: list[dict[str, Any]]) -> list[str]:
    if not ranked:
        return []
    top = ranked[0]
    pros = [f"{top['university_name']} has the strongest deterministic match."]
    if top.get("programs"):
        pros.append("It has matching program data in the EdPlan catalog.")
    if programs:
        pros.append("Curriculum comparison is based on required course and credit data.")
    return pros


def _cons(comparison_table: list[dict[str, Any]]) -> list[str]:
    cons = []
    if _unavailable_fields(comparison_table):
        cons.append("Tuition, transfer agreements, delivery mode, or institution type may be unavailable.")
    if any(not row["matching_programs"] for row in comparison_table):
        cons.append("Some institutions do not have a matching program in the current catalog.")
    return cons


def _recommendation_notes(
    ranked: list[dict[str, Any]],
    warnings: list[str],
) -> list[str]:
    notes = []
    if ranked:
        notes.append("Review the top-ranked university against advisor-confirmed transfer rules.")
        notes.append("Use tuition and financial aid data when those tables are available.")
    if warnings:
        notes.append("Resolve unavailable comparison fields before making a final enrollment decision.")
    return notes


def _multi_agent_context(student_context: dict[str, Any]) -> dict[str, Any]:
    plan = student_context.get("plan") if isinstance(student_context.get("plan"), dict) else {}
    completed_courses = student_context.get("completed_courses") or []
    return {
        "has_active_plan": bool(plan),
        "remaining_credits": plan.get("remaining_credits"),
        "graduation_estimate": plan.get("graduation_estimate"),
        "completed_course_count": len(completed_courses),
    }


def _unique_by(items: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    seen = set()
    unique = []
    for item in items:
        value = item.get(key)
        if value in seen:
            continue
        seen.add(value)
        unique.append(item)
    return unique


def _unique_strings(values: list[str]) -> list[str]:
    unique = []
    for value in values:
        if value and value not in unique:
            unique.append(value)
    return unique


comparison_service = ComparisonService()
