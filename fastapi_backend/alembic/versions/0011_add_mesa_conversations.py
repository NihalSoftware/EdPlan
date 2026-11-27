"""Add expiry-scoped Mesa sessions, saved scenarios, and anonymous counters."""

import sqlalchemy as sa
from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade():
    # These optional catalog fields are already read by the discovery and planning models.
    # Some databases were provisioned with them outside Alembic.
    op.execute("ALTER TABLE universities ADD COLUMN IF NOT EXISTS college_profile JSONB")
    op.execute("ALTER TABLE programs ADD COLUMN IF NOT EXISTS metadata_json JSONB")
    op.execute("ALTER TABLE courses ADD COLUMN IF NOT EXISTS metadata_json JSONB")
    op.execute("ALTER TABLE courses ADD COLUMN IF NOT EXISTS source_sequence INTEGER")
    op.create_table(
        "mesa_conversations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("guest_digest", sa.String(64)),
        sa.Column("retained", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("state", sa.JSON(), nullable=False),
    )
    op.create_index("ix_mesa_conversations_expires_at", "mesa_conversations", ["expires_at"])
    op.create_index("ix_mesa_conversations_owner_updated", "mesa_conversations", ["user_id", "updated_at"])
    op.create_table(
        "mesa_scenarios",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("conversation_id", sa.Uuid(), sa.ForeignKey("mesa_conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("comparison", sa.JSON(), nullable=False),
    )
    op.create_index("ix_mesa_scenarios_conversation_id", "mesa_scenarios", ["conversation_id"])
    op.create_table(
        "mesa_daily_metrics",
        sa.Column("day", sa.String(10), primary_key=True),
        sa.Column("intent", sa.String(3), primary_key=True),
        sa.Column("event", sa.String(24), primary_key=True),
        sa.Column("count", sa.Integer(), nullable=False),
    )


def downgrade():
    # Preserve catalog fields that may predate this migration.
    op.drop_table("mesa_daily_metrics")
    op.drop_table("mesa_scenarios")
    op.drop_table("mesa_conversations")
