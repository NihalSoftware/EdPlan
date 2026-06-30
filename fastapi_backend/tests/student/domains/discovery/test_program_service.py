import asyncio
import uuid

import pytest
from fastapi import HTTPException

from app.student.domains.discovery.services.program_service import ProgramService


class _Repository:
    def __init__(self):
        self.calls = []
        self.program = {
            "program_id": str(uuid.uuid4()),
            "program_name": "Computer Science",
        }

    async def get_programs(self, db, *, university_id=None, degree=None, search=None):
        self.calls.append(
            {
                "method": "get_programs",
                "university_id": university_id,
                "degree": degree,
                "search": search,
            }
        )
        return [self.program]

    async def get_program_by_id(self, db, program_id):
        self.calls.append({"method": "get_program_by_id", "program_id": program_id})
        return self.program


def test_get_programs_delegates_clean_filters_to_repository():
    repository = _Repository()
    service = ProgramService(repository)
    university_id = str(uuid.uuid4())

    result = asyncio.run(
        service.get_programs(
            object(),
            university_id=f" {university_id} ",
            degree=" Bachelor of Science ",
            search=" computer ",
        )
    )

    assert result == [repository.program]
    assert repository.calls == [
        {
            "method": "get_programs",
            "university_id": university_id,
            "degree": "Bachelor of Science",
            "search": "computer",
        }
    ]


def test_get_programs_rejects_invalid_university_uuid():
    repository = _Repository()
    service = ProgramService(repository)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(service.get_programs(object(), university_id="not-a-uuid"))

    assert exc_info.value.status_code == 400
    assert repository.calls == []


def test_get_program_by_id_rejects_invalid_program_uuid():
    repository = _Repository()
    service = ProgramService(repository)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(service.get_program_by_id(object(), "not-a-uuid"))

    assert exc_info.value.status_code == 400
    assert repository.calls == []


def test_get_program_by_id_raises_404_when_missing():
    class _MissingRepository(_Repository):
        async def get_program_by_id(self, db, program_id):
            self.calls.append({"method": "get_program_by_id", "program_id": program_id})
            return None

    repository = _MissingRepository()
    service = ProgramService(repository)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(service.get_program_by_id(object(), str(uuid.uuid4())))

    assert exc_info.value.status_code == 404
