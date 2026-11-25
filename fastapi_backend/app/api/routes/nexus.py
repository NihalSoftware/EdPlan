from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.nexus_service import NexusChatRequest, NexusChatResponse, NexusService

router = APIRouter(prefix="/nexus", tags=["nexus"])


def get_nexus_service(db: AsyncSession = Depends(get_db)) -> NexusService:
    return NexusService(db=db)


@router.post("/chat", response_model=NexusChatResponse)
async def chat(
    request: NexusChatRequest,
    service: NexusService = Depends(get_nexus_service),
) -> NexusChatResponse:
    try:
        return await service.send_message(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
