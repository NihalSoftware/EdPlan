from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, JSON, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MesaConversation(Base):
    __tablename__ = "mesa_conversations"
    __table_args__ = (Index("ix_mesa_conversations_owner_updated", "user_id", "updated_at"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    guest_digest: Mapped[str | None] = mapped_column(String(64))
    retained: Mapped[bool] = mapped_column(default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    state: Mapped[dict] = mapped_column(JSON)


class MesaScenario(Base):
    __tablename__ = "mesa_scenarios"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    conversation_id: Mapped[UUID] = mapped_column(
        ForeignKey("mesa_conversations.id", ondelete="CASCADE"), index=True
    )
    comparison: Mapped[dict] = mapped_column(JSON)


class MesaDailyMetric(Base):
    __tablename__ = "mesa_daily_metrics"

    day: Mapped[str] = mapped_column(String(10), primary_key=True)
    intent: Mapped[str] = mapped_column(String(3), primary_key=True)
    event: Mapped[str] = mapped_column(String(24), primary_key=True)
    count: Mapped[int] = mapped_column(default=0)
