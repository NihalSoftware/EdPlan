from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.security.auth import create_access_token
from app.student.domains.auth.schemas.auth import LoginRequest, RegisterRequest, UserProfile
from app.student.domains.auth.services import user_service

router = APIRouter(tags=["users"])


@router.post("/users")
async def register_user(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await user_service.register_user(db, payload)
    token = create_access_token(user.email)
    profile = UserProfile.model_validate(user)
    return {
        "success": True,
        "message": "User registered successfully",
        "data": {"bearer_token": token, "profile": profile.model_dump()},
    }


@router.post("/users/login")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await user_service.authenticate_user(db, payload.email, payload.password)
    token = create_access_token(user.email)
    profile = UserProfile.model_validate(user)
    return {
        "success": True,
        "message": "You are logged in successfully.",
        "data": {
            "bearer_token": token,
            "role": str(user.role.value if hasattr(user.role, "value") else user.role),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile": profile.model_dump(),
        },
    }
