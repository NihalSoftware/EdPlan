from app.db.base import Base


def test_normalized_planning_models_are_registered_in_alembic_metadata():
    assert {"ed_plans", "plan_courses"}.issubset(Base.metadata.tables)
