import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.student.domains.discovery.repositories.program_repository import (
    ProgramRepository,
    program_repository,
)


def _clean_filter(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} cannot be blank",
        )
    return cleaned


class ProgramService:
    def __init__(self, repository: ProgramRepository = program_repository) -> None:
        self.repository = repository

    async def get_programs(
        self,
        db: AsyncSession,
        *,
        university_id: str | None = None,
        degree: str | None = None,
        search: str | None = None,
    ) -> list[dict]:
        university_id = _clean_filter(university_id, "university_id")
        degree = _clean_filter(degree, "degree")
        search = _clean_filter(search, "search")

        if university_id:
            try:
                uuid.UUID(university_id)
            except ValueError as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid university_id",
                ) from exc
            programs = await self.repository.get_programs_by_university(db, university_id)
        elif search:
            programs = await self.repository.search_programs(db, search)
        else:
            programs = await self.repository.get_programs(db)

        if degree:
            normalized_degree = degree.strip().lower()
            programs = [
                program
                for program in programs
                if str(program.get("degree") or "").strip().lower() == normalized_degree
            ]

        if search and university_id:
            matching_ids = {
                program["program_id"]
                for program in await self.repository.search_programs(db, search)
            }
            programs = [
                program for program in programs if program["program_id"] in matching_ids
            ]

        return programs

    async def get_program_by_id(self, db: AsyncSession, program_id: str) -> dict:
        program = await self.repository.get_program_by_id(db, program_id)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Program not found",
            )
        return program


program_service = ProgramService()
