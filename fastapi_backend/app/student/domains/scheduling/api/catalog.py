from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.student.domains.scheduling.schemas.catalog import (
    AcademicTermDetailResponse,
    AcademicTermListResponse,
    CourseOfferingDetailResponse,
    CourseOfferingListResponse,
    SectionDetailResponse,
    SectionListResponse,
    SectionMeetingListResponse,
)
from app.student.domains.scheduling.services.catalog_service import (
    offering_service,
    section_meeting_service,
    section_service,
    term_service,
)

router = APIRouter(tags=["scheduling catalog"])


@router.get("/terms", response_model=AcademicTermListResponse)
async def list_terms(db: AsyncSession = Depends(get_db)):
    terms = await term_service.list_terms(db)
    return {"success": True, "data": terms, "metadata": {"count": len(terms)}}


@router.get("/terms/{id}", response_model=AcademicTermDetailResponse)
async def get_term(id: str, db: AsyncSession = Depends(get_db)):
    term = await term_service.get_term_by_id(db, id)
    return {"success": True, "data": term}


@router.get("/courses/{id}/offerings", response_model=CourseOfferingListResponse)
async def list_course_offerings(id: str, db: AsyncSession = Depends(get_db)):
    offerings = await offering_service.list_offerings_by_course(db, id)
    return {
        "success": True,
        "data": offerings,
        "metadata": {"count": len(offerings), "course_id": id},
    }


@router.get("/offerings/{id}", response_model=CourseOfferingDetailResponse)
async def get_offering(id: str, db: AsyncSession = Depends(get_db)):
    offering = await offering_service.get_offering_by_id(db, id)
    return {"success": True, "data": offering}


@router.get("/offerings/{id}/sections", response_model=SectionListResponse)
async def list_offering_sections(id: str, db: AsyncSession = Depends(get_db)):
    sections = await section_service.list_sections_by_offering(db, id)
    return {
        "success": True,
        "data": sections,
        "metadata": {"count": len(sections), "offering_id": id},
    }


@router.get("/sections/{id}", response_model=SectionDetailResponse)
async def get_section(id: str, db: AsyncSession = Depends(get_db)):
    section = await section_service.get_section_by_id(db, id)
    return {"success": True, "data": section}


@router.get("/sections/{id}/meetings", response_model=SectionMeetingListResponse)
async def list_section_meetings(id: str, db: AsyncSession = Depends(get_db)):
    meetings = await section_meeting_service.list_meetings_by_section(db, id)
    return {
        "success": True,
        "data": meetings,
        "metadata": {"count": len(meetings), "section_id": id},
    }
