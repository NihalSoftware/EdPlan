"""Provision the Mesa tables on a PostgreSQL database managed by another revision chain."""

import asyncio

from sqlalchemy import text

import app.models  # noqa: F401  Ensure the referenced users table is registered.
from app.db.base import Base
from app.db.session import engine
from app.mesa.models import MesaConversation, MesaDailyMetric, MesaScenario

MESA_TABLES = [
    MesaConversation.__table__,
    MesaScenario.__table__,
    MesaDailyMetric.__table__,
]


async def install_schema():
    try:
        async with engine.begin() as connection:
            await connection.execute(text("SET LOCAL lock_timeout = '5s'"))
            await connection.execute(
                text("SELECT pg_advisory_xact_lock(hashtext('edplan.mesa.install_schema'))")
            )
            await connection.run_sync(
                lambda sync: Base.metadata.create_all(sync, tables=MESA_TABLES, checkfirst=True)
            )
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(install_schema())
    print("Mesa tables are ready.")
