from app.student.domains.planning.tools.registry import PLANNING_TOOLS

MODULE_NAME = "academic_planning"

MODULE_DESCRIPTION = "Manage student education plans and graduation pathways."


def get_tools():
    return PLANNING_TOOLS
