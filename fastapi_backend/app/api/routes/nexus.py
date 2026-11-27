from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/nexus", tags=["nexus"])


@router.post("/chat", deprecated=True)
async def chat():
    raise HTTPException(410, "EdPlan Nexus chat has moved to Mesa. Open /mesa to start a conversation.")
