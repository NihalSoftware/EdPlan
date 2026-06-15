from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.student.domains.planning.schemas.graduation_audit import (
    GraduationAuditResult,
)
from app.student.domains.planning.services.graduation_audit_service import (
    graduation_audit_service,
)

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("/{plan_id}/audit", response_model=GraduationAuditResult)
async def get_graduation_audit(plan_id: str, db: AsyncSession = Depends(get_db)):
    return await graduation_audit_service.get_audit(db, plan_id)
