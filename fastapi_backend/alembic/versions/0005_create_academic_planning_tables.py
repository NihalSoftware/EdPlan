"""create academic planning tables

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-09
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def uuid_pk_column(name: str):
    return sa.Column(
        name,
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    op.create_table(
        "universities",
        uuid_pk_column("university_id"),
        sa.Column("university_name", sa.String(length=255), nullable=False),
        sa.Column("city", sa.String(length=120), nullable=False),
        sa.Column("state", sa.String(length=120), nullable=False),
        sa.Column("website", sa.String(length=255)),
        sa.UniqueConstraint(
            "university_name", "city", "state", name="universities_name_city_state_uk"
        ),
    )

    op.create_table(
        "programs",
        uuid_pk_column("program_id"),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("program_name", sa.String(length=255), nullable=False),
        sa.Column("degree", sa.String(length=120), nullable=False),
        sa.Column("total_credit_hours", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["university_id"],
            ["universities.university_id"],
            name="programs_university_fk",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "university_id", "program_name", "degree", name="programs_university_name_degree_uk"
        ),
        sa.UniqueConstraint("program_id", "university_id", name="programs_program_university_uk"),
        sa.CheckConstraint("total_credit_hours > 0", name="programs_total_credit_hours_chk"),
    )
    op.create_index("idx_programs_university_id", "programs", ["university_id"])

    op.create_table(
        "courses",
        uuid_pk_column("course_id"),
        sa.Column("program_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("course_code", sa.String(length=40), nullable=False),
        sa.Column("course_name", sa.String(length=255), nullable=False),
        sa.Column("credits", sa.Integer(), nullable=False),
        sa.Column("lecture_hours", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("lab_hours", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("recommended_year", sa.Integer()),
        sa.Column("recommended_semester", sa.String(length=20)),
        sa.Column("description", sa.Text()),
        sa.ForeignKeyConstraint(
            ["program_id"],
            ["programs.program_id"],
            name="courses_program_fk",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("program_id", "course_code", name="courses_program_code_uk"),
        sa.CheckConstraint("credits > 0", name="courses_credits_chk"),
        sa.CheckConstraint("lecture_hours >= 0 AND lab_hours >= 0", name="courses_hours_chk"),
        sa.CheckConstraint(
            "recommended_year IS NULL OR recommended_year BETWEEN 1 AND 8",
            name="courses_recommended_year_chk",
        ),
        sa.CheckConstraint(
            "recommended_semester IS NULL OR recommended_semester IN "
            "('Fall', 'Spring', 'Summer', 'Winter')",
            name="courses_recommended_semester_chk",
        ),
    )
    op.create_index("idx_courses_program_id", "courses", ["program_id"])
    op.create_index("idx_courses_course_code", "courses", ["course_code"])

    op.create_table(
        "course_prerequisites",
        uuid_pk_column("id"),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("prerequisite_course_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.course_id"],
            name="course_prerequisites_course_fk",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["prerequisite_course_id"],
            ["courses.course_id"],
            name="course_prerequisites_prerequisite_fk",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "course_id", "prerequisite_course_id", name="course_prerequisites_pair_uk"
        ),
        sa.CheckConstraint(
            "course_id <> prerequisite_course_id", name="course_prerequisites_not_self_chk"
        ),
    )
    op.create_index("idx_course_prerequisites_course_id", "course_prerequisites", ["course_id"])
    op.create_index(
        "idx_course_prerequisites_prerequisite_course_id",
        "course_prerequisites",
        ["prerequisite_course_id"],
    )

    op.create_table(
        "course_corequisites",
        uuid_pk_column("id"),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("corequisite_course_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.course_id"],
            name="course_corequisites_course_fk",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["corequisite_course_id"],
            ["courses.course_id"],
            name="course_corequisites_corequisite_fk",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("course_id", "corequisite_course_id", name="course_corequisites_pair_uk"),
        sa.CheckConstraint(
            "course_id <> corequisite_course_id", name="course_corequisites_not_self_chk"
        ),
    )
    op.create_index("idx_course_corequisites_course_id", "course_corequisites", ["course_id"])
    op.create_index(
        "idx_course_corequisites_corequisite_course_id",
        "course_corequisites",
        ["corequisite_course_id"],
    )

    op.create_table(
        "academic_terms",
        uuid_pk_column("term_id"),
        sa.Column("term_name", sa.String(length=80), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("term_name", name="academic_terms_name_uk"),
        sa.CheckConstraint("start_date < end_date", name="academic_terms_date_chk"),
    )
    op.create_index("idx_academic_terms_is_active", "academic_terms", ["is_active"])

    op.create_table(
        "course_offerings",
        uuid_pk_column("offering_id"),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("term_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("offering_type", sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.course_id"],
            name="course_offerings_course_fk",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["term_id"],
            ["academic_terms.term_id"],
            name="course_offerings_term_fk",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "course_id", "term_id", "offering_type", name="course_offerings_course_term_type_uk"
        ),
        sa.CheckConstraint(
            "offering_type IN ('Lecture', 'Lab', 'Lecture+Lab', 'Online')",
            name="course_offerings_type_chk",
        ),
    )
    op.create_index("idx_course_offerings_course_id", "course_offerings", ["course_id"])
    op.create_index("idx_course_offerings_term_id", "course_offerings", ["term_id"])

    op.create_table(
        "sections",
        uuid_pk_column("section_id"),
        sa.Column("offering_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("section_number", sa.String(length=20), nullable=False),
        sa.Column("crn", sa.String(length=30), nullable=False),
        sa.Column("campus", sa.String(length=120)),
        sa.Column("instructor", sa.String(length=150)),
        sa.Column("instruction_method", sa.String(length=40), nullable=False, server_default="In Person"),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("enrolled", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="Open"),
        sa.ForeignKeyConstraint(
            ["offering_id"],
            ["course_offerings.offering_id"],
            name="sections_offering_fk",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("crn", name="sections_crn_uk"),
        sa.UniqueConstraint("offering_id", "section_number", name="sections_offering_section_uk"),
        sa.CheckConstraint("capacity >= 0", name="sections_capacity_chk"),
        sa.CheckConstraint("enrolled >= 0 AND enrolled <= capacity", name="sections_enrolled_chk"),
        sa.CheckConstraint("status IN ('Open', 'Closed', 'Cancelled')", name="sections_status_chk"),
        sa.CheckConstraint(
            "instruction_method IN ('In Person', 'Online', 'Hybrid')",
            name="sections_instruction_method_chk",
        ),
    )
    op.create_index("idx_sections_offering_id", "sections", ["offering_id"])
    op.create_index("idx_sections_status", "sections", ["status"])
    op.create_index("idx_sections_offering_status", "sections", ["offering_id", "status"])

    op.create_table(
        "section_meetings",
        uuid_pk_column("meeting_id"),
        sa.Column("section_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("weekday", sa.SmallInteger()),
        sa.Column("start_time", sa.Time()),
        sa.Column("end_time", sa.Time()),
        sa.Column("building", sa.String(length=80)),
        sa.Column("room", sa.String(length=40)),
        sa.Column("meeting_type", sa.String(length=30), nullable=False, server_default="Class"),
        sa.ForeignKeyConstraint(
            ["section_id"],
            ["sections.section_id"],
            name="section_meetings_section_fk",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "section_id",
            "weekday",
            "start_time",
            "end_time",
            "meeting_type",
            name="section_meetings_unique_time_uk",
            postgresql_nulls_not_distinct=True,
        ),
        sa.CheckConstraint(
            "weekday IS NULL OR weekday BETWEEN 1 AND 7",
            name="section_meetings_weekday_chk",
        ),
        sa.CheckConstraint(
            "(weekday IS NULL AND start_time IS NULL AND end_time IS NULL) OR "
            "(weekday IS NOT NULL AND start_time IS NOT NULL AND end_time IS NOT NULL "
            "AND start_time < end_time)",
            name="section_meetings_time_pair_chk",
        ),
        sa.CheckConstraint(
            "meeting_type IN ('Class', 'Lab', 'Exam', 'Online Async')",
            name="section_meetings_type_chk",
        ),
    )
    op.create_index("idx_section_meetings_section_id", "section_meetings", ["section_id"])
    op.create_index(
        "idx_section_meetings_conflict_lookup",
        "section_meetings",
        ["weekday", "start_time", "end_time"],
    )

    op.create_table(
        "careers",
        uuid_pk_column("career_id"),
        sa.Column("career_name", sa.String(length=160), nullable=False),
        sa.Column("career_description", sa.Text()),
        sa.Column("industry", sa.String(length=120), nullable=False),
        sa.Column("career_level", sa.String(length=40), nullable=False),
        sa.Column("average_salary", sa.Numeric(12, 2)),
        sa.Column("growth_rate", sa.String(length=80)),
        sa.UniqueConstraint("career_name", name="careers_name_uk"),
        sa.CheckConstraint(
            "career_level IN ('Entry', 'Associate', 'Mid', 'Senior')",
            name="careers_level_chk",
        ),
        sa.CheckConstraint(
            "average_salary IS NULL OR average_salary >= 0",
            name="careers_average_salary_chk",
        ),
    )
    op.create_index("idx_careers_industry", "careers", ["industry"])

    op.create_table(
        "program_careers",
        uuid_pk_column("id"),
        sa.Column("program_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("career_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("relevance_score", sa.Integer(), nullable=False, server_default="80"),
        sa.ForeignKeyConstraint(
            ["program_id"],
            ["programs.program_id"],
            name="program_careers_program_fk",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["career_id"],
            ["careers.career_id"],
            name="program_careers_career_fk",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("program_id", "career_id", name="program_careers_pair_uk"),
        sa.CheckConstraint(
            "relevance_score BETWEEN 0 AND 100",
            name="program_careers_relevance_score_chk",
        ),
    )
    op.create_index("idx_program_careers_program_id", "program_careers", ["program_id"])
    op.create_index("idx_program_careers_career_id", "program_careers", ["career_id"])

    op.create_table(
        "course_careers",
        uuid_pk_column("id"),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("career_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("relevance_score", sa.Integer(), nullable=False, server_default="80"),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.course_id"],
            name="course_careers_course_fk",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["career_id"],
            ["careers.career_id"],
            name="course_careers_career_fk",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("course_id", "career_id", name="course_careers_pair_uk"),
        sa.CheckConstraint(
            "relevance_score BETWEEN 0 AND 100",
            name="course_careers_relevance_score_chk",
        ),
    )
    op.create_index("idx_course_careers_course_id", "course_careers", ["course_id"])
    op.create_index("idx_course_careers_career_id", "course_careers", ["career_id"])

    op.create_table(
        "ed_plans",
        uuid_pk_column("plan_id"),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("program_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plan_name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="ed_plans_user_fk",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["university_id"],
            ["universities.university_id"],
            name="ed_plans_university_fk",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["program_id", "university_id"],
            ["programs.program_id", "programs.university_id"],
            name="ed_plans_program_university_fk",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("user_id", "plan_name", name="ed_plans_user_name_uk"),
    )
    op.create_index("idx_ed_plans_user_id", "ed_plans", ["user_id"])
    op.create_index("idx_ed_plans_university_id", "ed_plans", ["university_id"])
    op.create_index("idx_ed_plans_program_id", "ed_plans", ["program_id"])

    op.create_table(
        "plan_courses",
        uuid_pk_column("id"),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("planned_term_id", postgresql.UUID(as_uuid=True)),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="Planned"),
        sa.Column("notes", sa.Text()),
        sa.ForeignKeyConstraint(
            ["plan_id"],
            ["ed_plans.plan_id"],
            name="plan_courses_plan_fk",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.course_id"],
            name="plan_courses_course_fk",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["planned_term_id"],
            ["academic_terms.term_id"],
            name="plan_courses_planned_term_fk",
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
        sa.UniqueConstraint("plan_id", "course_id", name="plan_courses_plan_course_uk"),
        sa.CheckConstraint(
            "status IN ('Planned', 'In Progress', 'Completed')",
            name="plan_courses_status_chk",
        ),
    )
    op.create_index("idx_plan_courses_plan_id", "plan_courses", ["plan_id"])
    op.create_index("idx_plan_courses_course_id", "plan_courses", ["course_id"])
    op.create_index("idx_plan_courses_planned_term_id", "plan_courses", ["planned_term_id"])

    op.create_table(
        "plan_sections",
        uuid_pk_column("id"),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("section_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("is_enrolled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("enrollment_status", sa.String(length=30), nullable=False, server_default="Planned"),
        sa.Column("notes", sa.Text()),
        sa.ForeignKeyConstraint(
            ["plan_id"],
            ["ed_plans.plan_id"],
            name="plan_sections_plan_fk",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["section_id"],
            ["sections.section_id"],
            name="plan_sections_section_fk",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("plan_id", "section_id", name="plan_sections_plan_section_uk"),
        sa.CheckConstraint(
            "enrollment_status IN ('Planned', 'Enrolled', 'Waitlisted', 'Completed')",
            name="plan_sections_enrollment_status_chk",
        ),
    )
    op.create_index("idx_plan_sections_plan_id", "plan_sections", ["plan_id"])
    op.create_index("idx_plan_sections_section_id", "plan_sections", ["section_id"])

    op.create_table(
        "plan_schedules",
        uuid_pk_column("schedule_id"),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("total_credits", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="Draft"),
        sa.Column("notes", sa.Text()),
        sa.ForeignKeyConstraint(
            ["plan_id"],
            ["ed_plans.plan_id"],
            name="plan_schedules_plan_fk",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.CheckConstraint("total_credits >= 0", name="plan_schedules_total_credits_chk"),
        sa.CheckConstraint(
            "status IN ('Draft', 'Final', 'Archived')",
            name="plan_schedules_status_chk",
        ),
    )
    op.create_index("idx_plan_schedules_plan_id", "plan_schedules", ["plan_id"])

    op.create_table(
        "login_history",
        uuid_pk_column("login_id"),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("login_time", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("logout_time", sa.DateTime(timezone=True)),
        sa.Column("ip_address", sa.String(length=45)),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="login_history_user_fk",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "logout_time IS NULL OR logout_time >= login_time",
            name="login_history_logout_after_login_chk",
        ),
        sa.CheckConstraint("status IN ('Success', 'Failed', 'Locked')", name="login_history_status_chk"),
    )
    op.create_index("idx_login_history_user_id", "login_history", ["user_id"])
    op.create_index("idx_login_history_login_time", "login_history", ["login_time"])


def downgrade() -> None:
    op.drop_index("idx_login_history_login_time", table_name="login_history")
    op.drop_index("idx_login_history_user_id", table_name="login_history")
    op.drop_table("login_history")

    op.drop_index("idx_plan_schedules_plan_id", table_name="plan_schedules")
    op.drop_table("plan_schedules")

    op.drop_index("idx_plan_sections_section_id", table_name="plan_sections")
    op.drop_index("idx_plan_sections_plan_id", table_name="plan_sections")
    op.drop_table("plan_sections")

    op.drop_index("idx_plan_courses_planned_term_id", table_name="plan_courses")
    op.drop_index("idx_plan_courses_course_id", table_name="plan_courses")
    op.drop_index("idx_plan_courses_plan_id", table_name="plan_courses")
    op.drop_table("plan_courses")

    op.drop_index("idx_ed_plans_program_id", table_name="ed_plans")
    op.drop_index("idx_ed_plans_university_id", table_name="ed_plans")
    op.drop_index("idx_ed_plans_user_id", table_name="ed_plans")
    op.drop_table("ed_plans")

    op.drop_index("idx_course_careers_career_id", table_name="course_careers")
    op.drop_index("idx_course_careers_course_id", table_name="course_careers")
    op.drop_table("course_careers")

    op.drop_index("idx_program_careers_career_id", table_name="program_careers")
    op.drop_index("idx_program_careers_program_id", table_name="program_careers")
    op.drop_table("program_careers")

    op.drop_index("idx_careers_industry", table_name="careers")
    op.drop_table("careers")

    op.drop_index("idx_section_meetings_conflict_lookup", table_name="section_meetings")
    op.drop_index("idx_section_meetings_section_id", table_name="section_meetings")
    op.drop_table("section_meetings")

    op.drop_index("idx_sections_offering_status", table_name="sections")
    op.drop_index("idx_sections_status", table_name="sections")
    op.drop_index("idx_sections_offering_id", table_name="sections")
    op.drop_table("sections")

    op.drop_index("idx_course_offerings_term_id", table_name="course_offerings")
    op.drop_index("idx_course_offerings_course_id", table_name="course_offerings")
    op.drop_table("course_offerings")

    op.drop_index("idx_academic_terms_is_active", table_name="academic_terms")
    op.drop_table("academic_terms")

    op.drop_index("idx_course_corequisites_corequisite_course_id", table_name="course_corequisites")
    op.drop_index("idx_course_corequisites_course_id", table_name="course_corequisites")
    op.drop_table("course_corequisites")

    op.drop_index("idx_course_prerequisites_prerequisite_course_id", table_name="course_prerequisites")
    op.drop_index("idx_course_prerequisites_course_id", table_name="course_prerequisites")
    op.drop_table("course_prerequisites")

    op.drop_index("idx_courses_course_code", table_name="courses")
    op.drop_index("idx_courses_program_id", table_name="courses")
    op.drop_table("courses")

    op.drop_index("idx_programs_university_id", table_name="programs")
    op.drop_table("programs")

    op.drop_table("universities")
