from app.db.base import Base


def test_catalog_models_are_registered_in_alembic_metadata():
    assert {
        "universities",
        "programs",
        "courses",
        "course_prerequisites",
        "course_corequisites",
    }.issubset(Base.metadata.tables)
