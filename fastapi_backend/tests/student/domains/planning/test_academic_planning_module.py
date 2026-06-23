import asyncio

from app.student.domains.planning import module
from app.student.domains.planning.schemas.normalized_plan import (
    PlanCourseCreateRequest,
    PlanCourseUpdateRequest,
    PlanCreateRequest,
    PlanUpdateRequest,
)
from app.student.domains.planning.schemas.planning_validation import PlanValidationRequest
from app.student.domains.planning.tools import (
    AddCourseTool,
    AuditPlanTool,
    CreatePlanTool,
    DeletePlanTool,
    GetPlanTool,
    MoveCourseTool,
    RemoveCourseTool,
    UpdatePlanTool,
    ValidatePlanTool,
)
from app.student.domains.planning.tools.registry import PLANNING_TOOLS


EXPECTED_TOOL_NAMES = [
    "create_plan",
    "update_plan",
    "delete_plan",
    "get_plan",
    "add_course",
    "remove_course",
    "move_course",
    "validate_plan",
    "audit_plan",
]


class _PlanningService:
    def __init__(self):
        self.calls = []

    async def create_plan(self, db, payload):
        self.calls.append(("create_plan", db, payload))
        return {"tool": "create_plan"}

    async def update_plan(self, db, plan_id, payload):
        self.calls.append(("update_plan", db, plan_id, payload))
        return {"tool": "update_plan"}

    async def deactivate_plan(self, db, plan_id):
        self.calls.append(("deactivate_plan", db, plan_id))
        return {"tool": "delete_plan"}

    async def get_plan_by_id(self, db, plan_id):
        self.calls.append(("get_plan_by_id", db, plan_id))
        return {"tool": "get_plan"}

    async def add_plan_course(self, db, plan_id, payload):
        self.calls.append(("add_plan_course", db, plan_id, payload))
        return {"tool": "add_course"}

    async def delete_plan_course(self, db, plan_id, course_id):
        self.calls.append(("delete_plan_course", db, plan_id, course_id))

    async def update_plan_course(self, db, plan_id, course_id, payload):
        self.calls.append(("update_plan_course", db, plan_id, course_id, payload))
        return {"tool": "move_course"}


class _ValidationService:
    def __init__(self):
        self.calls = []

    async def validate_plan(self, db, plan_id, payload=None):
        self.calls.append(("validate_plan", db, plan_id, payload))
        return {"tool": "validate_plan"}


class _AuditService:
    def __init__(self):
        self.calls = []

    async def get_audit(self, db, plan_id):
        self.calls.append(("get_audit", db, plan_id))
        return {"tool": "audit_plan"}


def test_planning_tool_registry_matches_development_plan_order():
    assert [tool.name for tool in PLANNING_TOOLS] == EXPECTED_TOOL_NAMES
    assert all(isinstance(tool.description, str) and tool.description for tool in PLANNING_TOOLS)
    assert all(callable(tool.execute) for tool in PLANNING_TOOLS)


def test_academic_planning_module_metadata_exposes_registry():
    assert module.MODULE_NAME == "academic_planning"
    assert module.MODULE_DESCRIPTION == "Manage student education plans and graduation pathways."
    assert module.get_tools() is PLANNING_TOOLS


def test_plan_tool_execution_delegates_to_existing_plan_service():
    service = _PlanningService()
    db = object()

    assert asyncio.run(CreatePlanTool(service).execute(db, _plan_create_payload())) == {
        "tool": "create_plan"
    }
    assert isinstance(service.calls[-1][2], PlanCreateRequest)

    assert asyncio.run(UpdatePlanTool(service).execute(db, "plan-1", {"plan_name": "Updated"})) == {
        "tool": "update_plan"
    }
    assert service.calls[-1][2] == "plan-1"
    assert isinstance(service.calls[-1][3], PlanUpdateRequest)

    assert asyncio.run(DeletePlanTool(service).execute(db, "plan-1")) == {"tool": "delete_plan"}
    assert service.calls[-1] == ("deactivate_plan", db, "plan-1")

    assert asyncio.run(GetPlanTool(service).execute(db, "plan-1")) == {"tool": "get_plan"}
    assert service.calls[-1] == ("get_plan_by_id", db, "plan-1")


def test_course_tool_execution_delegates_to_existing_plan_course_service():
    service = _PlanningService()
    db = object()

    assert asyncio.run(AddCourseTool(service).execute(db, "plan-1", {"course_id": "course-1"})) == {
        "tool": "add_course"
    }
    assert isinstance(service.calls[-1][3], PlanCourseCreateRequest)

    assert asyncio.run(RemoveCourseTool(service).execute(db, "plan-1", "course-1")) is None
    assert service.calls[-1] == ("delete_plan_course", db, "plan-1", "course-1")

    assert asyncio.run(
        MoveCourseTool(service).execute(db, "plan-1", "course-1", {"planned_term_id": None})
    ) == {"tool": "move_course"}
    assert isinstance(service.calls[-1][4], PlanCourseUpdateRequest)


def test_validation_and_audit_tools_delegate_to_existing_services():
    validation_service = _ValidationService()
    audit_service = _AuditService()
    db = object()

    assert asyncio.run(ValidatePlanTool(validation_service).execute(db, "plan-1", {})) == {
        "tool": "validate_plan"
    }
    assert isinstance(validation_service.calls[-1][3], PlanValidationRequest)

    assert asyncio.run(AuditPlanTool(audit_service).execute(db, "plan-1")) == {
        "tool": "audit_plan"
    }
    assert audit_service.calls[-1] == ("get_audit", db, "plan-1")


def _plan_create_payload():
    return {
        "user_id": 1,
        "university_id": "university-1",
        "program_id": "program-1",
        "plan_name": "Primary Plan",
    }
