"""enforce single active plan schedule

Revision ID: 0008
Revises: 0007
Create Date: 2026-06-09
"""

from alembic import op
import sqlalchemy as sa

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        WITH ranked AS (
            SELECT
                schedule_id,
                row_number() OVER (
                    PARTITION BY plan_id
                    ORDER BY generated_at DESC, schedule_id DESC
                ) AS active_rank
            FROM plan_schedules
            WHERE status = 'Active'
        )
        UPDATE plan_schedules ps
        SET status = 'Archived'
        FROM ranked
        WHERE ps.schedule_id = ranked.schedule_id
          AND ranked.active_rank > 1
        """
    )
    op.create_index(
        "ux_plan_schedules_one_active_per_plan",
        "plan_schedules",
        ["plan_id"],
        unique=True,
        postgresql_where=sa.text("status = 'Active'"),
    )


def downgrade() -> None:
    op.drop_index("ux_plan_schedules_one_active_per_plan", table_name="plan_schedules")
