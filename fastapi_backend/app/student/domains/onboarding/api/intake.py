from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.student.domains.onboarding.services import intake_service

router = APIRouter(prefix="/intake", tags=["intake"])
logger = logging.getLogger(__name__)


@router.post("")
async def save_intake(payload: dict, db: AsyncSession = Depends(get_db)):
    """Save intake form submission to the database."""
    try:
        entry = await intake_service.save_submission(db, payload)
        return {"success": True, "message": "Saved", "data": {"id": entry.id}}
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.exception("Failed to save intake submission")
        raise HTTPException(status_code=500, detail="Failed to save intake data") from exc
