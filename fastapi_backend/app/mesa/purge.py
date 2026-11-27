"""Delete expired Mesa conversations and aggregate metrics past their retention window."""

import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

from app.db.session import AsyncSessionLocal, engine
from app.mesa.models import MesaConversation, MesaDailyMetric


async def main():
    timestamp = datetime.now(timezone.utc)
    metric_cutoff = (timestamp.date() - timedelta(days=90)).isoformat()
    try:
        async with AsyncSessionLocal.begin() as db:
            await db.execute(delete(MesaConversation).where(MesaConversation.expires_at <= timestamp))
            await db.execute(delete(MesaDailyMetric).where(MesaDailyMetric.day < metric_cutoff))
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
