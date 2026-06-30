"""create schedulepilot phase-b1 tables

Revision ID: 0010
Revises: 0009
Create Date: 2026-06-26
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql


revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not inspector.has_table("schedule_pilot_schedules"):
        op.create_table(
            "schedule_pilot_schedules",
            sa.Column(
                "schedule_id",
                sa.Uuid(),
                primary_key=True,
                server_default=sa.text("gen_random_uuid()"),
            ),
            sa.Column(
                "plan_id",
                sa.Uuid(),
                sa.ForeignKey(
                    "ed_plans.plan_id",
                    name="schedule_pilot_schedules_plan_fk",
                    onupdate="CASCADE",
                    ondelete="CASCADE",
                ),
                nullable=False,
            ),
            sa.Column(
                "parent_schedule_id",
                sa.Uuid(),
                sa.ForeignKey(
                    "schedule_pilot_schedules.schedule_id",
                    name="schedule_pilot_schedules_parent_fk",
                    onupdate="CASCADE",
                    ondelete="SET NULL",
                ),
            ),
            sa.Column("schedule_name", sa.String(length=160)),
            sa.Column("status", sa.String(length=30), nullable=False, server_default="Draft"),
            sa.Column(
                "source",
                sa.String(length=40),
                nullable=False,
                server_default="system_generated",
            ),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("is_favorite", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("total_credits", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("score", sa.Float()),
            sa.Column("normalized_score", sa.Float()),
            sa.Column("rank_at_generation", sa.Integer()),
            sa.Column(
                "selected_term_id",
                sa.Uuid(),
                sa.ForeignKey(
                    "academic_terms.term_id",
                    name="schedule_pilot_schedules_selected_term_fk",
                    onupdate="CASCADE",
                    ondelete="SET NULL",
                ),
            ),
            sa.Column(
                "metrics_snapshot",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=False,
                server_default=sa.text("'{}'::jsonb"),
            ),
            sa.Column(
                "conflicts_snapshot",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=False,
                server_default=sa.text("'[]'::jsonb"),
            ),
            sa.Column(
                "warnings_snapshot",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=False,
                server_default=sa.text("'[]'::jsonb"),
            ),
            sa.Column(
                "tradeoffs_snapshot",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=False,
                server_default=sa.text("'[]'::jsonb"),
            ),
            sa.Column(
                "explanation_snapshot",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=False,
                server_default=sa.text("'{}'::jsonb"),
            ),
            sa.Column(
                "generation_metadata",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=False,
                server_default=sa.text("'{}'::jsonb"),
            ),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("archived_at", sa.DateTime(timezone=True)),
            sa.Column("deleted_at", sa.DateTime(timezone=True)),
            sa.CheckConstraint(
                "status IN ('Draft', 'Active', 'Final', 'Archived', 'Deleted')",
                name="schedule_pilot_schedules_status_chk",
            ),
            sa.CheckConstraint(
                "source IN ('system_generated', 'user_created', 'ai_generated', 'conversation_edit')",
                name="schedule_pilot_schedules_source_chk",
            ),
            sa.CheckConstraint(
                "total_credits >= 0",
                name="schedule_pilot_schedules_total_credits_chk",
            ),
        )
        op.create_index(
            "idx_schedule_pilot_schedules_plan_id",
            "schedule_pilot_schedules",
            ["plan_id"],
        )
        op.create_index(
            "idx_schedule_pilot_schedules_parent_schedule_id",
            "schedule_pilot_schedules",
            ["parent_schedule_id"],
        )
        op.create_index(
            "idx_schedule_pilot_schedules_plan_status",
            "schedule_pilot_schedules",
            ["plan_id", "status"],
        )
        op.create_index(
            "idx_schedule_pilot_schedules_plan_favorite",
            "schedule_pilot_schedules",
            ["plan_id", "is_favorite"],
        )
        op.create_index(
            "idx_schedule_pilot_schedules_selected_term_id",
            "schedule_pilot_schedules",
            ["selected_term_id"],
        )
        op.create_index(
            "idx_schedule_pilot_schedules_created_at",
            "schedule_pilot_schedules",
            ["created_at"],
        )
        op.create_index(
            "ux_schedule_pilot_schedules_one_active_per_plan",
            "schedule_pilot_schedules",
            ["plan_id"],
            unique=True,
            postgresql_where=sa.text("is_active = true"),
        )

    if not inspector.has_table("schedule_pilot_schedule_sections"):
        op.create_table(
            "schedule_pilot_schedule_sections",
            sa.Column(
                "id",
                sa.Uuid(),
                primary_key=True,
                server_default=sa.text("gen_random_uuid()"),
            ),
            sa.Column(
                "schedule_id",
                sa.Uuid(),
                sa.ForeignKey(
                    "schedule_pilot_schedules.schedule_id",
                    name="schedule_pilot_schedule_sections_schedule_fk",
                    onupdate="CASCADE",
                    ondelete="CASCADE",
                ),
                nullable=False,
            ),
            sa.Column(
                "section_id",
                sa.Uuid(),
                sa.ForeignKey(
                    "sections.section_id",
                    name="schedule_pilot_schedule_sections_section_fk",
                    onupdate="CASCADE",
                    ondelete="RESTRICT",
                ),
                nullable=False,
            ),
            sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("course_id_snapshot", sa.Uuid()),
            sa.Column("section_number_snapshot", sa.String(length=20)),
            sa.Column("crn_snapshot", sa.String(length=30)),
            sa.Column("instruction_method_snapshot", sa.String(length=40)),
            sa.Column(
                "meeting_snapshot",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=False,
                server_default=sa.text("'[]'::jsonb"),
            ),
            sa.Column("notes", sa.Text()),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint(
                "schedule_id",
                "section_id",
                name="schedule_pilot_schedule_sections_schedule_section_uk",
            ),
        )
        op.create_index(
            "idx_schedule_pilot_schedule_sections_schedule_id",
            "schedule_pilot_schedule_sections",
            ["schedule_id"],
        )
        op.create_index(
            "idx_schedule_pilot_schedule_sections_section_id",
            "schedule_pilot_schedule_sections",
            ["section_id"],
        )
        op.create_index(
            "idx_schedule_pilot_schedule_sections_display_order",
            "schedule_pilot_schedule_sections",
            ["schedule_id", "display_order"],
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if inspector.has_table("schedule_pilot_schedule_sections"):
        op.drop_index(
            "idx_schedule_pilot_schedule_sections_display_order",
            table_name="schedule_pilot_schedule_sections",
        )
        op.drop_index(
            "idx_schedule_pilot_schedule_sections_section_id",
            table_name="schedule_pilot_schedule_sections",
        )
        op.drop_index(
            "idx_schedule_pilot_schedule_sections_schedule_id",
            table_name="schedule_pilot_schedule_sections",
        )
        op.drop_table("schedule_pilot_schedule_sections")

    if inspector.has_table("schedule_pilot_schedules"):
        op.drop_index(
            "ux_schedule_pilot_schedules_one_active_per_plan",
            table_name="schedule_pilot_schedules",
        )
        op.drop_index(
            "idx_schedule_pilot_schedules_created_at",
            table_name="schedule_pilot_schedules",
        )
        op.drop_index(
            "idx_schedule_pilot_schedules_selected_term_id",
            table_name="schedule_pilot_schedules",
        )
        op.drop_index(
            "idx_schedule_pilot_schedules_plan_favorite",
            table_name="schedule_pilot_schedules",
        )
        op.drop_index(
            "idx_schedule_pilot_schedules_plan_status",
            table_name="schedule_pilot_schedules",
        )
        op.drop_index(
            "idx_schedule_pilot_schedules_parent_schedule_id",
            table_name="schedule_pilot_schedules",
        )
        op.drop_index(
            "idx_schedule_pilot_schedules_plan_id",
            table_name="schedule_pilot_schedules",
        )
        op.drop_table("schedule_pilot_schedules")
