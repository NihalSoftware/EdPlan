"""allow active plan schedules

Revision ID: 0007
Revises: 0006
Create Date: 2026-06-09
"""

from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("plan_schedules_status_chk", "plan_schedules", type_="check")
    op.create_check_constraint(
        "plan_schedules_status_chk",
        "plan_schedules",
        "status IN ('Draft', 'Active', 'Final', 'Archived')",
    )


def downgrade() -> None:
    op.execute(
        "UPDATE plan_schedules SET status = 'Final' WHERE status = 'Active'"
    )
    op.drop_constraint("plan_schedules_status_chk", "plan_schedules", type_="check")
    op.create_check_constraint(
        "plan_schedules_status_chk",
        "plan_schedules",
        "status IN ('Draft', 'Final', 'Archived')",
    )
