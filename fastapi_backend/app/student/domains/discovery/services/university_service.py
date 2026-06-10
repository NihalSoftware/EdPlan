from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.student.domains.discovery.repositories.university_repository import (
    UniversityRepository,
    university_repository,
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


class UniversityService:
    def __init__(self, repository: UniversityRepository = university_repository) -> None:
        self.repository = repository

    async def search_universities(
        self,
        db: AsyncSession,
        *,
        search: str | None = None,
        state: str | None = None,
        page: int = 0,
        per_page: int = 10,
    ) -> dict:
        if page < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="page must be greater than or equal to 0",
            )
        if per_page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="per_page must be greater than or equal to 1",
            )

        search = _clean_filter(search, "search")
        state = _clean_filter(state, "state")
        universities = await self.repository.list_universities(
            db,
            search=search,
            state=state,
            offset=page * per_page,
            limit=per_page,
        )
        return {
            "results": universities,
            "metadata": {
                "count": len(universities),
                "page": page,
                "per_page": per_page,
                "source": "live_database",
            },
        }

    async def get_university(self, db: AsyncSession, university_id: str) -> dict:
        _validate_uuid(university_id, "university_id")
        university = await self.repository.get_university_by_id(db, university_id)
        if not university:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="University not found",
            )
        return university

    async def compare_universities(
        self, db: AsyncSession, university_ids: list[str]
    ) -> list[dict]:
        if len(university_ids) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least two universities are required",
            )
        selected_ids = university_ids[:5]
        for university_id in selected_ids:
            _validate_uuid(university_id, "university_id")
        return await self.repository.get_universities_by_ids(db, selected_ids)


university_service = UniversityService()


async def search_universities(
    db: AsyncSession,
    *,
    search: str | None = None,
    state: str | None = None,
    page: int = 0,
    per_page: int = 10,
) -> dict:
    return await university_service.search_universities(
        db,
        page=page,
        per_page=per_page,
        search=search,
        state=state,
    )


async def get_university(db: AsyncSession, university_id: str) -> dict:
    return await university_service.get_university(db, university_id)


async def compare_universities(db: AsyncSession, university_ids: list[str]) -> list[dict]:
    return await university_service.compare_universities(db, university_ids)
