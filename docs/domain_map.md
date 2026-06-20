# Domain Map

Generated: 2026-06-17

## Catalog

Catalog owns the institution and course data used by planning, validation, and audit.

Owned tables:

- `universities`: school identity and location.
- `programs`: degree programs attached to universities.
- `courses`: catalog courses attached to programs.
- `course_prerequisites`: course-to-course prerequisite requirements.
- `course_corequisites`: course-to-course same-term requirements.
- `academic_terms`: academic calendar terms.
- `course_offerings`: course availability by term.
- `sections`: scheduled sections for an offering.
- `section_meetings`: meeting times and locations for sections.

Implemented API surfaces:

- Discovery APIs expose universities, programs, courses, prerequisites, and corequisites.
- Scheduling catalog APIs expose terms, offerings, sections, and meetings.

Catalog does not own student plans, validation decisions, graduation readiness, or generated schedules.

## Planning

Planning owns student education plans and the course choices inside each plan.

Owned normalized tables:

- `ed_plans`: one student plan for a selected university and program.
- `plan_courses`: selected catalog courses in a plan, with optional term, status, and notes.

Legacy compatibility tables:

- `education_plans`: JSON-backed legacy plan payloads.
- `program_courses`: denormalized course rows copied from legacy payloads.
- `course_schedules`: legacy schedule data attached to legacy plan courses.
- `course_reschedules`: queued legacy reschedule requests.

Planning is responsible for create, read, update, deactivate, add-course, update-course, and remove-course operations. It does not generate schedules or infer course recommendations.

## Validation

Validation owns deterministic checks against a proposed plan state.

Implemented checks:

- Duplicate detection: flags the same course appearing more than once in a validation candidate set.
- Prerequisite validation: requires prerequisite courses to end before the dependent course starts.
- Corequisite validation: requires corequisite courses in the same planned term.
- Credit validation: flags terms exceeding `MAX_TERM_CREDITS`, currently 18.

Tables read:

- `ed_plans`
- `plan_courses`
- `courses`
- `course_prerequisites`
- `course_corequisites`
- `academic_terms`

Validation reports issues; it does not currently prevent plan-course writes.

## Audit

Audit owns graduation-progress reporting for a plan.

Implemented outputs:

- Graduation progress.
- Missing courses.
- Readiness boolean.
- Planned, required, and remaining credits.
- Course completion percentage.

Tables read:

- `ed_plans`
- `plan_courses`
- `programs`
- `courses`

Current behavior treats planned courses as completed because there is no transcript or completed-course source of truth yet.

## Scheduling

Scheduling is future work for generated schedules.

Currently implemented:

- Read-only catalog endpoints for terms, offerings, sections, and section meetings.
- Legacy reschedule request persistence under `/api/users/education-plan/reschedule`.

Not implemented:

- Schedule generation.
- Conflict resolution.
- Section selection in normalized plans.
- User schedule persistence against sections.

## Agents

Agents are future work only.

Current state:

- Agent package placeholders exist.
- No agent orchestration is implemented.
- No AI functionality is implemented.
- No recommendation engine is implemented.

Agents should not own source-of-truth academic rules. Future agent features should call deterministic catalog, planning, validation, and audit services.
