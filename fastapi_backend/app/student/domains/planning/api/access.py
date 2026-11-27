"""Current student ownership for normalized planning entry points."""
from uuid import UUID

from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.security.auth import get_current_user
from app.student.domains.planning.models.normalized_plan import EdPlan


async def require_plan_owner(
    request: Request, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    raw_id = request.path_params.get("plan_id")
    if raw_id is None:
        return
    try:
        plan_id = UUID(raw_id)
    except ValueError as exc:
        raise HTTPException(400, "Invalid plan_id") from exc
    owned = await db.scalar(select(EdPlan.plan_id).where(
        EdPlan.plan_id == plan_id, EdPlan.user_id == user.id
    ))
    if owned is None:
        raise HTTPException(404, "Plan not found")
