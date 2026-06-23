# Academic Planning

## Purpose

Academic Planning manages student education plans and graduation pathways for the Student Platform.

## Tools

- `create_plan`
- `update_plan`
- `delete_plan`
- `get_plan`
- `add_course`
- `remove_course`
- `move_course`
- `validate_plan`
- `audit_plan`

## Current Capabilities

- Create, update, deactivate, and retrieve education plans.
- Add courses to plans, remove courses from plans, and move courses between terms.
- Validate planned courses for duplicate, prerequisite, corequisite, and credit-limit issues.
- Audit a plan against graduation requirements.

## Future Capabilities

The Development Plan reserves these future tools. They are not implemented in this module:

- `generate_plan`
- `optimize_plan`
- `forecast_graduation`

## Orchestrator Integration Notes

The tool layer is a thin wrapper over existing planning services. Tools do not contain business logic and do not know about FastAPI routes.

A future Student Orchestrator can load this module with:

```python
from app.student.domains.planning.module import get_tools

tools = get_tools()
```

Each tool exposes:

- `name`
- `description`
- `async execute(...)`

The orchestrator remains responsible for providing the database session and validated tool arguments.
