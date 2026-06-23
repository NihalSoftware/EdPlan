"""create phase-a agentic schema

Revision ID: 0009
Revises: 0008
Create Date: 2026-06-23
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    op.execute("CREATE SCHEMA IF NOT EXISTS agentic")

    if not _has_table(inspector, "orchestrator_runs"):
        op.create_table(
            "orchestrator_runs",
            sa.Column(
                "run_id",
                sa.Uuid(),
                primary_key=True,
                server_default=sa.text("gen_random_uuid()"),
            ),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey(
                    "public.users.id",
                    name="orchestrator_runs_user_fk",
                    onupdate="CASCADE",
                    ondelete="CASCADE",
                ),
                nullable=False,
            ),
            sa.Column(
                "plan_id",
                sa.Uuid(),
                sa.ForeignKey(
                    "public.ed_plans.plan_id",
                    name="orchestrator_runs_plan_fk",
                    onupdate="CASCADE",
                    ondelete="CASCADE",
                ),
                nullable=False,
            ),
            sa.Column("query", sa.Text(), nullable=False),
            sa.Column("intent", sa.String(length=128)),
            sa.Column(
                "selected_modules",
                sa.JSON(),
                nullable=False,
                server_default=sa.text("'[]'::json"),
            ),
            sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
            sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("completed_at", sa.DateTime(timezone=True)),
            sa.Column("error", sa.Text()),
            sa.Column(
                "metadata",
                sa.JSON(),
                nullable=False,
                server_default=sa.text("'{}'::json"),
            ),
            schema="agentic",
        )
        op.create_index(
            "ix_agentic_orchestrator_runs_user_id",
            "orchestrator_runs",
            ["user_id"],
            schema="agentic",
        )
        op.create_index(
            "ix_agentic_orchestrator_runs_plan_id",
            "orchestrator_runs",
            ["plan_id"],
            schema="agentic",
        )
        op.create_index(
            "ix_agentic_orchestrator_runs_status",
            "orchestrator_runs",
            ["status"],
            schema="agentic",
        )

    if not _has_table(inspector, "workflow_events"):
        op.create_table(
            "workflow_events",
            sa.Column(
                "event_id",
                sa.Uuid(),
                primary_key=True,
                server_default=sa.text("gen_random_uuid()"),
            ),
            sa.Column(
                "run_id",
                sa.Uuid(),
                sa.ForeignKey(
                    "agentic.orchestrator_runs.run_id",
                    name="workflow_events_run_fk",
                    ondelete="CASCADE",
                ),
                nullable=False,
            ),
            sa.Column("event_type", sa.String(length=128), nullable=False),
            sa.Column(
                "metadata",
                sa.JSON(),
                nullable=False,
                server_default=sa.text("'{}'::json"),
            ),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            schema="agentic",
        )
        op.create_index(
            "ix_agentic_workflow_events_run_id",
            "workflow_events",
            ["run_id"],
            schema="agentic",
        )
        op.create_index(
            "ix_agentic_workflow_events_run_created_at",
            "workflow_events",
            ["run_id", "created_at"],
            schema="agentic",
        )

    if not _has_table(inspector, "module_executions"):
        op.create_table(
            "module_executions",
            sa.Column(
                "execution_id",
                sa.Uuid(),
                primary_key=True,
                server_default=sa.text("gen_random_uuid()"),
            ),
            sa.Column(
                "run_id",
                sa.Uuid(),
                sa.ForeignKey(
                    "agentic.orchestrator_runs.run_id",
                    name="module_executions_run_fk",
                    ondelete="CASCADE",
                ),
                nullable=False,
            ),
            sa.Column("module_name", sa.String(length=128), nullable=False),
            sa.Column("status", sa.String(length=32), nullable=False, server_default="running"),
            sa.Column("success", sa.Boolean()),
            sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("completed_at", sa.DateTime(timezone=True)),
            sa.Column("duration_ms", sa.Integer()),
            sa.Column("error", sa.Text()),
            sa.Column(
                "metadata",
                sa.JSON(),
                nullable=False,
                server_default=sa.text("'{}'::json"),
            ),
            schema="agentic",
        )
        op.create_index(
            "ix_agentic_module_executions_run_id",
            "module_executions",
            ["run_id"],
            schema="agentic",
        )
        op.create_index(
            "ix_agentic_module_executions_module_name",
            "module_executions",
            ["module_name"],
            schema="agentic",
        )

    if not _has_table(inspector, "student_preferences"):
        op.create_table(
            "student_preferences",
            sa.Column(
                "preference_id",
                sa.Uuid(),
                primary_key=True,
                server_default=sa.text("gen_random_uuid()"),
            ),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey(
                    "public.users.id",
                    name="student_preferences_user_fk",
                    onupdate="CASCADE",
                    ondelete="CASCADE",
                ),
                nullable=False,
            ),
            sa.Column(
                "plan_id",
                sa.Uuid(),
                sa.ForeignKey(
                    "public.ed_plans.plan_id",
                    name="student_preferences_plan_fk",
                    onupdate="CASCADE",
                    ondelete="CASCADE",
                ),
            ),
            sa.Column("preference_key", sa.String(length=128), nullable=False),
            sa.Column("preference_value", sa.Text(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            schema="agentic",
        )
        op.create_index(
            "ix_agentic_student_preferences_user_id",
            "student_preferences",
            ["user_id"],
            schema="agentic",
        )
        op.create_index(
            "ix_agentic_student_preferences_plan_id",
            "student_preferences",
            ["plan_id"],
            schema="agentic",
        )

    if not _has_table(inspector, "conversation_memory"):
        op.create_table(
            "conversation_memory",
            sa.Column(
                "memory_id",
                sa.Uuid(),
                primary_key=True,
                server_default=sa.text("gen_random_uuid()"),
            ),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey(
                    "public.users.id",
                    name="conversation_memory_user_fk",
                    onupdate="CASCADE",
                    ondelete="CASCADE",
                ),
                nullable=False,
            ),
            sa.Column(
                "plan_id",
                sa.Uuid(),
                sa.ForeignKey(
                    "public.ed_plans.plan_id",
                    name="conversation_memory_plan_fk",
                    onupdate="CASCADE",
                    ondelete="CASCADE",
                ),
                nullable=False,
            ),
            sa.Column(
                "run_id",
                sa.Uuid(),
                sa.ForeignKey(
                    "agentic.orchestrator_runs.run_id",
                    name="conversation_memory_run_fk",
                    ondelete="SET NULL",
                ),
            ),
            sa.Column("summary", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            schema="agentic",
        )
        op.create_index(
            "ix_agentic_conversation_memory_user_id",
            "conversation_memory",
            ["user_id"],
            schema="agentic",
        )
        op.create_index(
            "ix_agentic_conversation_memory_plan_id",
            "conversation_memory",
            ["plan_id"],
            schema="agentic",
        )
        op.create_index(
            "ix_agentic_conversation_memory_run_id",
            "conversation_memory",
            ["run_id"],
            schema="agentic",
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    for table_name in (
        "conversation_memory",
        "student_preferences",
        "module_executions",
        "workflow_events",
        "orchestrator_runs",
    ):
        if _has_table(inspector, table_name):
            op.drop_table(table_name, schema="agentic")

    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.schemata
                WHERE schema_name = 'agentic'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'agentic'
            ) THEN
                DROP SCHEMA agentic;
            END IF;
        END $$;
        """
    )


def _has_table(inspector, table_name: str) -> bool:
    return inspector.has_table(table_name, schema="agentic")
