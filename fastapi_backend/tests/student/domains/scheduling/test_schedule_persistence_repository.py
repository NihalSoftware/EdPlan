from __future__ import annotations

import asyncio
import uuid
from datetime import datetime

from app.student.domains.scheduling.models import (
    SchedulePilotSchedule,
    SchedulePilotScheduleSection,
)
from app.student.domains.scheduling.repositories.schedule_persistence_repository import (
    SchedulePersistenceRepository,
)


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

    def all(self):
        return self._values


class _Session:
    def __init__(self, values=None):
        self.values = values or []
        self.statements = []
        self.added = []
        self.deleted = []
        self.flush_count = 0

    async def execute(self, statement):
        self.statements.append(statement)
        return _Result(self.values)

    def add(self, item):
        self.added.append(item)

    async def delete(self, item):
        self.deleted.append(item)

    async def flush(self):
        self.flush_count += 1


def _schedule(plan_id=None, *, status="Draft", is_active=False) -> SchedulePilotSchedule:
    return SchedulePilotSchedule(
        schedule_id=uuid.uuid4(),
        plan_id=plan_id or uuid.uuid4(),
        created_at=datetime(2026, 6, 1, 9, 0),
        updated_at=datetime(2026, 6, 1, 9, 0),
        total_credits=3,
        status=status,
        source="system_generated",
        is_active=is_active,
        is_favorite=False,
        metrics_snapshot={},
        conflicts_snapshot=[],
        warnings_snapshot=[],
        tradeoffs_snapshot=[],
        explanation_snapshot={},
        generation_metadata={"notes": "Saved schedule"},
    )


def test_repository_creates_schedule_without_committing():
    repository = SchedulePersistenceRepository()
    session = _Session()
    plan_id = uuid.uuid4()

    schedule = asyncio.run(
        repository.create_schedule(
            session,
            plan_id=plan_id,
            total_credits=6,
            status="Final",
            schedule_name="Candidate A",
            generation_metadata={"notes": "Saved schedule"},
        )
    )

    assert schedule.plan_id == plan_id
    assert schedule.total_credits == 6
    assert schedule.status == "Final"
    assert schedule.schedule_name == "Candidate A"
    assert session.added == [schedule]
    assert session.flush_count == 1


def test_repository_reads_updates_deletes_and_lists_schedules():
    plan_id = uuid.uuid4()
    schedule = _schedule(plan_id)
    repository = SchedulePersistenceRepository()
    session = _Session([schedule])

    read_schedule = asyncio.run(repository.get_schedule(session, schedule_id=schedule.schedule_id))
    schedules = asyncio.run(repository.list_plan_schedules(session, plan_id=plan_id))
    updated = asyncio.run(
        repository.update_schedule(
            schedule,
            total_credits=9,
            status="Archived",
            schedule_name=None,
            update_schedule_name=True,
        )
    )
    asyncio.run(repository.delete_schedule(session, schedule))

    assert read_schedule == schedule
    assert schedules == [schedule]
    assert updated.total_credits == 9
    assert updated.status == "Archived"
    assert updated.schedule_name is None
    assert session.deleted == [schedule]
    assert session.flush_count == 1
    assert len(session.statements) == 2


def test_repository_activates_and_deactivates_active_schedule():
    plan_id = uuid.uuid4()
    active = _schedule(plan_id, status="Active", is_active=True)
    target = _schedule(plan_id, status="Final")
    repository = SchedulePersistenceRepository()
    session = _Session([active])

    deactivated = asyncio.run(
        repository.deactivate_plan_schedules(
            session,
            plan_id=plan_id,
            except_schedule_id=target.schedule_id,
        )
    )
    activated = asyncio.run(repository.activate_schedule(target))

    assert deactivated == [active]
    assert active.status == "Archived"
    assert active.is_active is False
    assert activated.status == "Active"
    assert activated.is_active is True


def test_repository_replaces_schedule_sections_for_schedule():
    repository = SchedulePersistenceRepository()
    session = _Session()
    schedule_id = uuid.uuid4()
    section_ids = [uuid.uuid4(), uuid.uuid4()]
    sections = [
        {
            "section_id": str(section_id),
            "course_id_snapshot": str(uuid.uuid4()),
            "section_number_snapshot": "001",
            "crn_snapshot": f"crn-{index}",
            "instruction_method_snapshot": "In Person",
            "meeting_snapshot": [{"meeting_id": f"meeting-{index}"}],
        }
        for index, section_id in enumerate(section_ids)
    ]

    schedule_sections = asyncio.run(
        repository.replace_schedule_sections(
            session,
            schedule_id=schedule_id,
            sections=sections,
            notes="source_option_id=option-1",
        )
    )

    assert [item.schedule_id for item in schedule_sections] == [schedule_id, schedule_id]
    assert [item.section_id for item in schedule_sections] == section_ids
    assert all(isinstance(item, SchedulePilotScheduleSection) for item in schedule_sections)
    assert [item.display_order for item in schedule_sections] == [0, 1]
    assert schedule_sections[0].meeting_snapshot == [{"meeting_id": "meeting-0"}]
    assert len(session.added) == 2
    assert len(session.statements) == 1
    assert session.flush_count == 2


def test_repository_legacy_plan_section_helpers_remain_available():
    repository = SchedulePersistenceRepository()
    session = _Session()
    plan_id = uuid.uuid4()
    section_ids = [uuid.uuid4()]

    plan_sections = asyncio.run(
        repository.replace_selected_sections(
            session,
            plan_id=plan_id,
            section_ids=section_ids,
            notes="legacy",
        )
    )

    assert plan_sections[0].plan_id == plan_id
    assert plan_sections[0].section_id == section_ids[0]
