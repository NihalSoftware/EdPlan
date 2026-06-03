from __future__ import annotations

import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.student.domains.discovery.models import Program, University


class ProgramRepository:
    async def get_programs(self, db: AsyncSession) -> list[dict]:
        result = await db.execute(_program_query().order_by(Program.program_name))
        return [_program_to_dict(program) for program in result.scalars().all()]

    async def get_program_by_id(
        self, db: AsyncSession, program_id: str
    ) -> dict | None:
        parsed_program_id = _parse_uuid(program_id)
        if parsed_program_id is None:
            return None
        result = await db.execute(
            _program_query().where(Program.program_id == parsed_program_id)
        )
        program = result.scalar_one_or_none()
        return _program_to_dict(program) if program else None

    async def search_programs(self, db: AsyncSession, query: str) -> list[dict]:
        term = f"%{query.strip()}%"
        result = await db.execute(
            _program_query()
            .join(Program.university)
            .where(
                or_(
                    Program.program_name.ilike(term),
                    Program.degree.ilike(term),
                    University.university_name.ilike(term),
                )
            )
            .order_by(Program.program_name)
        )
        return [_program_to_dict(program) for program in result.scalars().all()]

    async def get_programs_by_university(
        self, db: AsyncSession, university_id: str
    ) -> list[dict]:
        parsed_university_id = _parse_uuid(university_id)
        if parsed_university_id is None:
            return []
        result = await db.execute(
            _program_query()
            .where(Program.university_id == parsed_university_id)
            .order_by(Program.program_name)
        )
        return [_program_to_dict(program) for program in result.scalars().all()]


def _program_query():
    return select(Program).options(joinedload(Program.university))


def _parse_uuid(value: str) -> uuid.UUID | None:
    try:
        return uuid.UUID(str(value))
    except (TypeError, ValueError):
        return None


def _program_to_dict(program: Program) -> dict:
    university = program.university
    return {
        "program_id": str(program.program_id),
        "program_name": program.program_name,
        "degree": program.degree,
        "total_credit_hours": program.total_credit_hours,
        "university": {
            "university_id": str(university.university_id),
            "university_name": university.university_name,
            "city": university.city,
            "state": university.state,
            "website": university.website,
        },
    }


program_repository = ProgramRepository()
