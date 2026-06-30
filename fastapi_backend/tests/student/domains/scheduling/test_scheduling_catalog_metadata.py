from app.db.base import Base


def test_scheduling_models_are_registered_in_alembic_metadata():
    assert {
        "academic_terms",
        "course_offerings",
        "sections",
        "section_meetings",
    }.issubset(Base.metadata.tables)
