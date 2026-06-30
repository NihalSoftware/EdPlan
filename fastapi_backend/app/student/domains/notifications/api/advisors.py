from fastapi import APIRouter, HTTPException

from app.student.domains.notifications.services import notification_service

router = APIRouter(tags=["users"])


@router.post("/users/email-advisor")
async def email_advisor(data: dict):
    email = data.get("email")
    advisor_email = data.get("advisorEmail")
    body = data.get("body", "")
    if not (email and advisor_email):
        raise HTTPException(status_code=400, detail="email and advisorEmail are required")
    notification_service.notify_advisor(
        email=email,
        advisor_email=advisor_email,
        body=body,
        phone=data.get("phone"),
    )
    return {"success": True, "message": "Advisor notified", "data": None}
