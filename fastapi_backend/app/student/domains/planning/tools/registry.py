from app.student.domains.planning.tools.audit import AuditPlanTool
from app.student.domains.planning.tools.courses import (
    AddCourseTool,
    MoveCourseTool,
    RemoveCourseTool,
)
from app.student.domains.planning.tools.plans import (
    CreatePlanTool,
    DeletePlanTool,
    GetPlanTool,
    UpdatePlanTool,
)
from app.student.domains.planning.tools.read import (
    GetAvailableTermsTool,
    GetCorequisitesTool,
    GetCourseDetailsTool,
    GetPrerequisitesTool,
    GetProgramRequirementsTool,
    GetRemainingCoursesTool,
)
from app.student.domains.planning.tools.validation import ValidatePlanTool

PLANNING_TOOLS = [
    CreatePlanTool(),
    UpdatePlanTool(),
    DeletePlanTool(),
    GetPlanTool(),
    AddCourseTool(),
    RemoveCourseTool(),
    MoveCourseTool(),
    ValidatePlanTool(),
    AuditPlanTool(),
    GetRemainingCoursesTool(),
    GetCourseDetailsTool(),
    GetPrerequisitesTool(),
    GetCorequisitesTool(),
    GetProgramRequirementsTool(),
    GetAvailableTermsTool(),
]
