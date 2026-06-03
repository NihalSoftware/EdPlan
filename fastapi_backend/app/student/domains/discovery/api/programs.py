from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.student.domains.discovery.schemas.program import (
    ProgramDetailResponse,
    ProgramListResponse,
)
from app.student.domains.discovery.services.program_service import program_service

router = APIRouter(prefix="/programs", tags=["programs"])


@router.get(
    "",
    response_model=ProgramListResponse,
    summary="List academic programs",
    description=(
        "Browse the temporary EdPlan program catalog. Results can be filtered "
        "by university, degree, and search text."
    ),
)
async def list_programs(
    university_id: str | None = Query(
        None,
        min_length=1,
        description="Stable university identifier returned in program responses.",
    ),
    degree: str | None = Query(
        None,
        min_length=1,
        description="Exact degree label to filter by, such as Bachelors or Certificate.",
    ),
    search: str | None = Query(
        None,
        min_length=1,
        description="Case-insensitive search across program, degree, and university name.",
    ),
    db: AsyncSession = Depends(get_db),
):
    programs = await program_service.get_programs(
        db,
        university_id=university_id,
        degree=degree,
        search=search,
    )
    return {
        "success": True,
        "data": programs,
        "metadata": {"count": len(programs)},
    }


@router.get(
    "/{program_id}",
    response_model=ProgramDetailResponse,
    summary="Get academic program details",
    description="Return one program from the temporary EdPlan program catalog.",
    responses={404: {"description": "Program not found"}},
)
async def get_program(program_id: str, db: AsyncSession = Depends(get_db)):
    program = await program_service.get_program_by_id(db, program_id)
    return {"success": True, "data": program}
