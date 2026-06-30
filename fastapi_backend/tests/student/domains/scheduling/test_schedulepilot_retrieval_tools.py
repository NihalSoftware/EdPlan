from __future__ import annotations

import pytest

from app.student.domains.scheduling.tools.registry import SCHEDULING_TOOLS
from app.student.domains.scheduling.tools.retrieval import (
    GetAvailableTermsTool,
    GetCourseOfferingsTool,
    GetCourseSectionsTool,
    GetPlanCoursesTool,
    GetSectionMeetingsTool,
    GetStudentPlanTool,
)


class _Service:
    def __init__(self):
        self.calls = []

    async def get_student_plan(self, db, *, user_id, plan_id):
        self.calls.append(("get_student_plan", db, user_id, plan_id))
        return {"plan_id": plan_id, "user_id": user_id}

    async def get_plan_courses(self, db, *, plan_id):
        self.calls.append(("get_plan_courses", db, plan_id))
        return [{"plan_id": plan_id}]

    async def get_available_terms(self, db):
        self.calls.append(("get_available_terms", db))
        return [{"term_id": "term-1"}]

    async def get_course_offerings(self, db, *, course_ids):
        self.calls.append(("get_course_offerings", db, course_ids))
        return [{"course_ids": course_ids}]

    async def get_course_sections(self, db, *, offering_ids):
        self.calls.append(("get_course_sections", db, offering_ids))
        return [{"offering_ids": offering_ids}]

    async def get_section_meetings(self, db, *, section_ids):
        self.calls.append(("get_section_meetings", db, section_ids))
        return [{"section_ids": section_ids}]


def test_schedulepilot_tool_registry_order_and_metadata():
    assert [tool.name for tool in SCHEDULING_TOOLS] == [
        "get_student_plan",
        "get_plan_courses",
        "get_available_terms",
        "get_course_offerings",
        "get_course_sections",
        "get_section_meetings",
    ]
    assert all(tool.description for tool in SCHEDULING_TOOLS)
    assert all(tool.parameters["type"] == "object" for tool in SCHEDULING_TOOLS)


@pytest.mark.asyncio
async def test_retrieval_tools_delegate_to_retrieval_service():
    service = _Service()
    db = object()

    assert await GetStudentPlanTool(service).execute(db, user_id=1, plan_id="plan-1") == {
        "plan_id": "plan-1",
        "user_id": 1,
    }
    assert await GetPlanCoursesTool(service).execute(db, plan_id="plan-1") == [
        {"plan_id": "plan-1"}
    ]
    assert await GetAvailableTermsTool(service).execute(db) == [{"term_id": "term-1"}]
    assert await GetCourseOfferingsTool(service).execute(db, course_ids=["course-1"]) == [
        {"course_ids": ["course-1"]}
    ]
    assert await GetCourseSectionsTool(service).execute(db, offering_ids=["offering-1"]) == [
        {"offering_ids": ["offering-1"]}
    ]
    assert await GetSectionMeetingsTool(service).execute(db, section_ids=["section-1"]) == [
        {"section_ids": ["section-1"]}
    ]

    assert service.calls == [
        ("get_student_plan", db, 1, "plan-1"),
        ("get_plan_courses", db, "plan-1"),
        ("get_available_terms", db),
        ("get_course_offerings", db, ["course-1"]),
        ("get_course_sections", db, ["offering-1"]),
        ("get_section_meetings", db, ["section-1"]),
    ]
