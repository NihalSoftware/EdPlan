from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class TokenPayload(BaseModel):
    sub: str
    exp: int


class TokenResponse(BaseModel):
    success: bool
    message: str
    data: dict


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str | None = None
    password: str
    role: UserRole = UserRole.CUSTOMER


class UserProfile(BaseModel):
    id: int
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    role: UserRole
    last_login_at: datetime | None = None

    class Config:
        from_attributes = True


class EmailVerificationRequest(BaseModel):
    email: EmailStr
