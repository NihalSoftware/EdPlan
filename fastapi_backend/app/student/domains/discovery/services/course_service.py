from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.student.domains.discovery.repositories.course_repository import (
    CourseRepository,
    course_repository,
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


def _validate_uuid(value: str, field_name: str) -> None:
    try:
        uuid.UUID(str(value))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name}",
        ) from exc


class CourseService:
    def __init__(self, repository: CourseRepository = course_repository) -> None:
        self.repository = repository

    async def list_courses(
        self,
        db: AsyncSession,
        *,
        program_id: str | None = None,
        search: str | None = None,
    ) -> list[dict]:
        program_id = _clean_filter(program_id, "program_id")
        search = _clean_filter(search, "search")
        if program_id:
            _validate_uuid(program_id, "program_id")
        return await self.repository.list_courses(
            db,
            program_id=program_id,
            search=search,
        )

    async def get_course_by_id(self, db: AsyncSession, course_id: str) -> dict:
        _validate_uuid(course_id, "course_id")
        course = await self.repository.get_course_by_id(db, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )
        return course

    async def list_prerequisites(self, db: AsyncSession, course_id: str) -> list[dict]:
        _validate_uuid(course_id, "course_id")
        prerequisites = await self.repository.list_prerequisites(db, course_id)
        if prerequisites is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )
        return prerequisites

    async def list_corequisites(self, db: AsyncSession, course_id: str) -> list[dict]:
        _validate_uuid(course_id, "course_id")
        corequisites = await self.repository.list_corequisites(db, course_id)
        if corequisites is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )
        return corequisites


course_service = CourseService()
