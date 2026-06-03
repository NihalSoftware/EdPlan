from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.student.domains.onboarding.models.intake import IntakeSubmission
from app.student.domains.onboarding.repositories import intake_repository


async def save_submission(db: AsyncSession, payload: dict[str, Any]) -> IntakeSubmission:
    return await intake_repository.create_submission(db, payload)
