# Academic Planning

## Purpose

Academic Planning manages student education plans, plan-course operations, validation, catalog context, and graduation readiness for the Student Platform.

## Tools

The tool registry is the public tool surface for the Academic Planning orchestrator module. Tool order is stable and covered by tests.

- `create_plan`
- `update_plan`
- `delete_plan`
- `get_plan`
- `add_course`
- `remove_course`
- `move_course`
- `validate_plan`
- `audit_plan`
- `get_remaining_courses`
- `get_course_details`
- `get_prerequisites`
- `get_corequisites`
- `get_program_requirements`
- `get_available_terms`

## Current Capabilities

- Create, update, deactivate, and retrieve education plans.
- Add courses to plans, remove courses from plans, and move courses between terms.
- Validate planned courses for duplicate, prerequisite, corequisite, and credit-limit issues.
- Audit a plan against graduation requirements.
- Read catalog course, prerequisite, corequisite, program requirement, and term context for advising workflows.

## Orchestrator Integration Notes

`AcademicPlanningModule` adapts the tool registry to the student orchestrator. The tool layer is a thin wrapper over existing planning, discovery, and scheduling services. Tools do not contain business logic and do not know about FastAPI routes.

```python
from app.student.domains.planning.module import get_tools

tools = get_tools()
```

Each tool exposes:

- `name`
- `description`
- `parameters`
- `async execute(...)`

The orchestrator provides the database session and validated tool arguments.
