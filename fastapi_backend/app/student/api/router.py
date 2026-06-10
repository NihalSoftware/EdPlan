from fastapi import APIRouter

from app.student.domains.auth.api import auth, email_verification
from app.student.domains.discovery.api import courses, programs, universities
from app.student.domains.notifications.api import advisors
from app.student.domains.onboarding.api import intake
from app.student.domains.planning.api import normalized_plans, plans
from app.student.domains.scheduling.api import catalog, reschedules


def get_student_router() -> APIRouter:
    router = APIRouter()
    router.include_router(auth.router, prefix="/api")
    router.include_router(email_verification.router, prefix="/api")
    router.include_router(catalog.router, prefix="/api")
    router.include_router(normalized_plans.router, prefix="/api")
    router.include_router(plans.router, prefix="/api")
    router.include_router(reschedules.router, prefix="/api")
    router.include_router(advisors.router, prefix="/api")
    router.include_router(programs.router, prefix="/api")
    router.include_router(courses.router, prefix="/api")
    router.include_router(universities.router, prefix="/api")
    router.include_router(intake.router, prefix="/api")
    return router
