from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings

# PostgreSQL 18 with asyncpg driver
# DATABASE_URL format: postgresql+asyncpg://user:password@host:5432/dbname
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    hide_parameters=True,  # SQL debug output must not expose student identifiers or credentials.
    future=True,
    poolclass=NullPool if settings.environment == "production" else None,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
