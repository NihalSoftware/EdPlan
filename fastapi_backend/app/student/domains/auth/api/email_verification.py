from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["users"])


@router.post("/users/email-verification/request")
async def request_email_verification(data: dict):
    """Email verification is currently disabled."""
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="email is required")

    return {
        "success": True,
        "message": "Email verification is disabled. You can continue signup.",
        "data": {"email": email},
    }


@router.get("/users/email-verification/status")
async def get_email_verification_status(email: str):
    """Check if email is verified (simplified implementation)"""
    if not email:
        raise HTTPException(status_code=400, detail="email parameter is required")

    return {
        "success": True,
        "message": "Verification status retrieved",
        "data": {"verified": True, "email": email},
    }
