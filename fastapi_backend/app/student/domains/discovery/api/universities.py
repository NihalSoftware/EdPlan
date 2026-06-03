from fastapi import APIRouter, HTTPException, Query

from app.student.domains.discovery.schemas.university import CompareRequest, University
from app.student.domains.discovery.services import university_service

router = APIRouter(prefix="/universities", tags=["universities"])


@router.get("", response_model=dict)
async def search_universities(
    search: str | None = None,
    state: str | None = None,
    page: int = 0,
    per_page: int = Query(10, ge=1, le=100),
):
    payload = await university_service.search_universities(
    page=page, per_page=per_page, search=search, state=state
    )
    return {
        "success": True,
        "data": payload["results"],
        "metadata": payload.get("metadata"),
    }


@router.get("/{unit_id}", response_model=dict)
async def get_university(unit_id: str):
    school = await university_service.get_university(unit_id)
    if not school:
        raise HTTPException(status_code=404, detail="University not found")
    return {"success": True, "data": school}


@router.post("/compare", response_model=dict)
async def compare_universities(payload: CompareRequest):
    schools = await university_service.compare_universities(payload.unit_ids)
    results: list[University] = [University(**school) for school in schools]
    return {"success": True, "data": [item.model_dump() for item in results]}
