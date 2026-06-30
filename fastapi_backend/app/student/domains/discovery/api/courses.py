from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.student.domains.discovery.schemas.course import (
    CourseCorequisiteListResponse,
    CourseDetailResponse,
    CourseListResponse,
    CoursePrerequisiteListResponse,
)
from app.student.domains.discovery.services.course_service import course_service

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get(
    "",
    response_model=CourseListResponse,
    summary="List catalog courses",
)
async def list_courses(
    program_id: str | None = Query(
        None,
        min_length=1,
        description="Filter by the live UUID of a program.",
    ),
    search: str | None = Query(
        None,
        min_length=1,
        description="Case-insensitive search across course code, name, and description.",
    ),
    db: AsyncSession = Depends(get_db),
):
    courses = await course_service.list_courses(
        db,
        program_id=program_id,
        search=search,
    )
    return {"success": True, "data": courses, "metadata": {"count": len(courses)}}


@router.get(
    "/{course_id}",
    response_model=CourseDetailResponse,
    summary="Get catalog course details",
)
async def get_course(course_id: str, db: AsyncSession = Depends(get_db)):
    course = await course_service.get_course_by_id(db, course_id)
    return {"success": True, "data": course}


@router.get(
    "/{course_id}/prerequisites",
    response_model=CoursePrerequisiteListResponse,
    summary="List prerequisite courses for a catalog course",
)
async def list_course_prerequisites(course_id: str, db: AsyncSession = Depends(get_db)):
    prerequisites = await course_service.list_prerequisites(db, course_id)
    return {
        "success": True,
        "data": prerequisites,
        "metadata": {"count": len(prerequisites), "course_id": course_id},
    }


@router.get(
    "/{course_id}/corequisites",
    response_model=CourseCorequisiteListResponse,
    summary="List corequisite courses for a catalog course",
)
async def list_course_corequisites(course_id: str, db: AsyncSession = Depends(get_db)):
    corequisites = await course_service.list_corequisites(db, course_id)
    return {
        "success": True,
        "data": corequisites,
        "metadata": {"count": len(corequisites), "course_id": course_id},
    }
