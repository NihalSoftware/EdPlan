"""add legacy education plan link

Revision ID: 0006
Revises: 0005
Create Date: 2026-06-09
"""

from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ed_plans", sa.Column("legacy_education_plan_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "ed_plans_legacy_education_plan_fk",
        "ed_plans",
        "education_plans",
        ["legacy_education_plan_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )
    op.create_index(
        "idx_ed_plans_legacy_education_plan_id",
        "ed_plans",
        ["legacy_education_plan_id"],
        unique=True,
    )

    op.execute(
        """
        UPDATE ed_plans ep
        SET legacy_education_plan_id = source.legacy_id
        FROM (
            SELECT plan_id, legacy_id
            FROM (
                SELECT
                    ep_inner.plan_id,
                    legacy.id AS legacy_id,
                    row_number() OVER (
                        PARTITION BY ep_inner.plan_id
                        ORDER BY legacy.updated_at DESC NULLS LAST, legacy.created_at DESC NULLS LAST
                    ) AS plan_match_rank,
                    row_number() OVER (
                        PARTITION BY legacy.id
                        ORDER BY legacy.updated_at DESC NULLS LAST, legacy.created_at DESC NULLS LAST, ep_inner.plan_id
                    ) AS legacy_match_rank
                FROM ed_plans ep_inner
                JOIN education_plans legacy
                  ON legacy.user_id = ep_inner.user_id
                 AND (
                        ep_inner.plan_name = legacy.university_name || ' - ' || legacy.program_name
                     OR ep_inner.plan_name = legacy.university_name || ' - ' || legacy.program_name || ' (' || legacy.degree || ')'
                     OR (
                            legacy.degree IS NULL
                        AND ep_inner.plan_name = legacy.university_name || ' - ' || legacy.program_name
                        )
                 )
                WHERE ep_inner.legacy_education_plan_id IS NULL
            ) ranked
            WHERE plan_match_rank = 1
              AND legacy_match_rank = 1
        ) AS source
        WHERE ep.plan_id = source.plan_id
        """
    )


def downgrade() -> None:
    op.drop_index("idx_ed_plans_legacy_education_plan_id", table_name="ed_plans")
    op.drop_constraint("ed_plans_legacy_education_plan_fk", "ed_plans", type_="foreignkey")
    op.drop_column("ed_plans", "legacy_education_plan_id")
