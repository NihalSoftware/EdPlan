from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_by_id(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)


async def create_user(
    db: AsyncSession,
    *,
    email: str,
    first_name: str | None,
    last_name: str | None,
    phone_number: str | None,
    role: str,
    password_hash: str,
) -> User:
    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        role=role,
        password_hash=password_hash,
    )
    db.add(user)
    return user


async def update_last_login(db: AsyncSession, user: User, value) -> User:
    user.last_login_at = value
    return user


async def save(db: AsyncSession, user: User) -> User:
    await db.commit()
    await db.refresh(user)
    return user
