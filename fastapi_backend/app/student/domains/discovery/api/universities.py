from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.student.domains.discovery.schemas.university import (
    CompareRequest,
    UniversityCompareResponse,
    UniversityDetailResponse,
    UniversityListResponse,
)
from app.student.domains.discovery.services import university_service

router = APIRouter(prefix="/universities", tags=["universities"])


@router.get("", response_model=UniversityListResponse)
async def search_universities(
    search: str | None = None,
    state: str | None = None,
    page: int = Query(0, ge=0),
    per_page: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    payload = await university_service.search_universities(
        db,
        page=page,
        per_page=per_page,
        search=search,
        state=state,
    )
    return {
        "success": True,
        "data": payload["results"],
        "metadata": payload.get("metadata"),
    }


@router.get("/{unit_id}", response_model=UniversityDetailResponse)
async def get_university(unit_id: str, db: AsyncSession = Depends(get_db)):
    school = await university_service.get_university(db, unit_id)
    return {"success": True, "data": school}


@router.post("/compare", response_model=UniversityCompareResponse)
async def compare_universities(
    payload: CompareRequest,
    db: AsyncSession = Depends(get_db),
):
    schools = await university_service.compare_universities(db, payload.unit_ids)
    return {"success": True, "data": schools}
