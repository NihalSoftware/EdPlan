from app.student.domains.scheduling.tools.retrieval import (
    GetAvailableTermsTool,
    GetCourseOfferingsTool,
    GetCourseSectionsTool,
    GetPlanCoursesTool,
    GetSectionMeetingsTool,
    GetStudentPlanTool,
)

SCHEDULING_TOOLS = [
    GetStudentPlanTool(),
    GetPlanCoursesTool(),
    GetAvailableTermsTool(),
    GetCourseOfferingsTool(),
    GetCourseSectionsTool(),
    GetSectionMeetingsTool(),
]
