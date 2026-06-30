import asyncio
import uuid

from app.student.domains.discovery.models import University
from app.student.domains.discovery.repositories.university_repository import UniversityRepository


class _ScalarResult:
    def __init__(self, values):
        self._values = values

    def all(self):
        return self._values


class _Result:
    def __init__(self, values):
        self._values = values

    def scalars(self):
        return _ScalarResult(self._values)

    def scalar_one_or_none(self):
        return self._values[0] if self._values else None


class _Session:
    def __init__(self, values):
        self.values = values
        self.statements = []

    async def execute(self, statement):
        self.statements.append(statement)
        return _Result(self.values)


def _university(university_id=None, name="University of New Mexico-Main Campus"):
    return University(
        university_id=university_id or uuid.uuid4(),
        university_name=name,
        city="Albuquerque",
        state="NM",
        website="https://www.unm.edu",
    )


def test_list_universities_returns_uuid_and_compatibility_aliases():
    university = _university()
    repository = UniversityRepository()
    session = _Session([university])

    result = asyncio.run(repository.list_universities(session, search="new mexico"))

    assert result == [
        {
            "university_id": str(university.university_id),
            "unit_id": str(university.university_id),
            "university_name": "University of New Mexico-Main Campus",
            "name": "University of New Mexico-Main Campus",
            "city": "Albuquerque",
            "state": "NM",
            "website": "https://www.unm.edu",
            "college_info": {
                "website": "https://www.unm.edu",
                "location": "Albuquerque, NM",
            },
            "organization_type": "University",
            "location_type": None,
            "size": None,
            "graduation_rate": None,
            "average_annual_cost": None,
            "median_earnings": None,
            "financial_aid_debt": None,
            "typical_earnings": None,
            "acceptance_rate": None,
        }
    ]
    assert len(session.statements) == 1


def test_get_university_by_id_returns_one_university():
    university_id = uuid.uuid4()
    university = _university(university_id=university_id)
    repository = UniversityRepository()
    session = _Session([university])

    result = asyncio.run(repository.get_university_by_id(session, str(university_id)))

    assert result["university_id"] == str(university_id)
    assert result["name"] == "University of New Mexico-Main Campus"


def test_get_university_by_id_rejects_invalid_uuid_without_query():
    repository = UniversityRepository()
    session = _Session([_university()])

    result = asyncio.run(repository.get_university_by_id(session, "not-a-uuid"))

    assert result is None
    assert session.statements == []


def test_get_universities_by_ids_preserves_requested_order():
    first_id = uuid.uuid4()
    second_id = uuid.uuid4()
    first = _university(university_id=first_id, name="First University")
    second = _university(university_id=second_id, name="Second University")
    repository = UniversityRepository()
    session = _Session([second, first])

    result = asyncio.run(
        repository.get_universities_by_ids(session, [str(first_id), str(second_id)])
    )

    assert [entry["university_id"] for entry in result] == [str(first_id), str(second_id)]
