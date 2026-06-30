from app.student.domains.comparison.tools.programs import (
    CompareCareerPathsTool,
    CompareProgramsTool,
    SearchProgramsTool,
)
from app.student.domains.comparison.tools.universities import (
    CompareUniversitiesTool,
    SearchUniversitiesTool,
)

COMPARISON_TOOLS = [
    SearchUniversitiesTool(),
    CompareUniversitiesTool(),
    SearchProgramsTool(),
    CompareProgramsTool(),
    CompareCareerPathsTool(),
]
