# Domain Boundary Review

Generated on: 2026-06-10

Source references:

- Live schema documentation: `docs/live_database_schema.md`
- Current backend modules under `fastapi_backend/app/student/domains`
- Product direction: Discovery -> Planning -> Scheduling -> Agents

This review is intentionally documentation-only. It does not move files, rename packages,
change routes, change imports, alter frontend code, or implement new features.

## Current State

The backend currently separates student-facing work into domain folders:

- `discovery`: universities, programs, courses, prerequisites, and corequisites.
- `planning`: legacy education plan persistence and plan course payload handling.
- `scheduling`: reschedule request handling plus recently added catalog endpoints for terms,
  offerings, sections, and section meetings.

The recent Scheduling Catalog implementation added these tables under
`fastapi_backend/app/student/domains/scheduling`:

- `academic_terms`
- `course_offerings`
- `sections`
- `section_meetings`

Those tables support future scheduling workflows, but their current behavior is read-only
institution catalog/reference lookup. They do not model student availability, work constraints,
timetable generation, conflict resolution, attendance optimization, or schedule scoring.

Therefore, the current placement is understandable as a near-term implementation choice, but
the domain name is broader than the behavior implemented there. These resources are catalog data,
not the Scheduling feature itself.

## Intended Product Boundaries

The intended product flow is:

1. Discovery: browse institutional catalog data and understand available academic options.
2. Planning: build and validate a student academic plan against program requirements.
3. Scheduling: turn planned courses into feasible term schedules using student constraints and
   live section availability.
4. Agents: orchestrate or assist across discovery, planning, and scheduling workflows.

The live database currently contains both catalog entities and future planning/scheduling
entities. The backend should keep those concepts distinct even when one table is useful to
another domain.

## Catalog Domain

Catalog data is institution-owned reference data. It describes what exists before any student
chooses it.

Catalog includes:

- Universities
- Programs
- Courses
- Course prerequisites
- Course corequisites
- Academic terms
- Course offerings
- Sections
- Section meetings

Current implemented catalog modules:

| Resource | Current Module Area | Boundary Assessment |
| --- | --- | --- |
| Universities | `student/domains/discovery` | Correct for current milestone. |
| Programs | `student/domains/discovery` | Correct for current milestone. |
| Courses | `student/domains/discovery` | Correct for current milestone. |
| Course prerequisites | `student/domains/discovery` | Correct for current milestone. |
| Course corequisites | `student/domains/discovery` | Correct for current milestone. |
| Academic terms | `student/domains/scheduling` | Catalog/reference data currently placed under Scheduling. |
| Course offerings | `student/domains/scheduling` | Catalog/reference data currently placed under Scheduling. |
| Sections | `student/domains/scheduling` | Catalog/reference data currently placed under Scheduling. |
| Section meetings | `student/domains/scheduling` | Catalog/reference data currently placed under Scheduling. |

Recommended future placement:

- A dedicated catalog domain, such as `student/domains/catalog`, would be the clean long-term
  home for all institution catalog/reference data.
- Discovery can then become a product experience that consumes catalog data rather than owning
  all catalog persistence directly.
- Scheduling can consume catalog sections and meetings without owning them.

Refactor recommendation now:

- Defer folder restructuring.
- Keep the existing routes and imports stable for this milestone.
- Add future refactor work only after Planning consumes the catalog consistently and before
  implementing true Scheduling features.

## Planning Domain

Planning data is student-owned academic intent. It records what a student plans to complete and
supports validation or audit logic.

Planning includes:

- Ed Plans
- Plan Courses
- Validation
- Graduation Audit

Live schema planning entities include:

- `ed_plans`
- `plan_courses`
- legacy `education_plans`
- legacy `program_courses`

Current backend planning modules remain centered on legacy plan JSON and legacy generated plan
courses. That is separate from the catalog domain. Catalog entities may be referenced by planning,
but planning owns the student's selected academic path and audit state.

Important distinction:

- `courses` is catalog data.
- `plan_courses` is planning data.
- Course prerequisites/corequisites are catalog rules.
- Validation and graduation audit belong in Planning because they evaluate a student's plan
  against catalog requirements.

## Scheduling Domain

Scheduling data is student-specific timetable feasibility and section selection. It starts after a
plan exists and uses both the plan and catalog section data.

Scheduling includes:

- Plan Sections
- Plan Schedules
- Student availability
- Work schedule constraints
- Attendance constraints
- Conflict resolution
- Timetable generation
- Attendance optimization

Live schema scheduling-facing entities include:

- `plan_sections`
- `plan_schedules`

The currently implemented `academic_terms`, `course_offerings`, `sections`, and
`section_meetings` endpoints are not Scheduling feature endpoints in the product sense. They are
catalog endpoints needed by future Scheduling. True Scheduling should not begin until Planning has
clear ownership of `ed_plans` and `plan_courses`.

Important distinction:

- `sections` is catalog data.
- `section_meetings` is catalog data.
- `plan_sections` is scheduling data because it records selected sections for a student's plan.
- `plan_schedules` is scheduling data because it records generated or selected timetable output.

## Misnamed Module Report

The following modules currently imply Scheduling ownership while containing catalog/reference data:

| Module | Contains | Why Name Is Misleading | Suggested Future Placement | Recommendation |
| --- | --- | --- | --- | --- |
| `fastapi_backend/app/student/domains/scheduling/models/catalog.py` | `AcademicTerm`, `CourseOffering`, `Section`, `SectionMeeting` models | These are institution catalog tables, not student scheduling behavior. | `student/domains/catalog/models` or equivalent catalog package. | Defer. Keep stable until catalog boundary refactor is planned. |
| `fastapi_backend/app/student/domains/scheduling/repositories/catalog_repository.py` | Read-only catalog queries for terms, offerings, sections, and meetings | Repository name says catalog, but package path says scheduling. | `student/domains/catalog/repositories`. | Defer. Low risk while routes are read-only. |
| `fastapi_backend/app/student/domains/scheduling/services/catalog_service.py` | Lookup services and UUID validation for catalog resources | Service does not perform scheduling logic. | `student/domains/catalog/services`. | Defer. Move before implementing timetable generation. |
| `fastapi_backend/app/student/domains/scheduling/schemas/catalog.py` | Response schemas for catalog resources | Schemas describe reference data payloads. | `student/domains/catalog/schemas`. | Defer. |
| `fastapi_backend/app/student/domains/scheduling/api/catalog.py` | `GET /api/terms`, course offering, section, and meeting lookup endpoints | API is catalog lookup, not scheduling workflow. | `student/domains/catalog/api`. Routes may remain stable. | Defer route/module move; do not change URL paths now. |

The existing `fastapi_backend/app/student/domains/scheduling/api/reschedules.py` is also not the
future Scheduling domain in the full product sense. It persists legacy reschedule requests against
`course_reschedules`, but it does represent a student action more closely than the catalog lookup
modules above.

## Recommended Next Development Order

1. Keep current module structure stable for this milestone.
2. Complete Planning ownership around normalized live tables:
   - `ed_plans`
   - `plan_courses`
   - plan validation
   - graduation audit
3. Introduce a first-class Catalog package when the next cleanup window opens:
   - move universities, programs, courses, prerequisites, corequisites, terms, offerings,
     sections, and meetings behind a single catalog boundary
   - preserve public route URLs during any move
   - update imports and tests in one focused refactor
4. Implement true Scheduling only after Planning is normalized:
   - student availability
   - work schedule constraints
   - attendance constraints
   - conflict detection
   - timetable generation
   - attendance optimization
5. Add Agents last as orchestration over stable Discovery/Catalog, Planning, and Scheduling
   service contracts.

## Expected Boundary Conclusion

Catalog:

- Universities
- Programs
- Courses
- Prerequisites
- Corequisites
- Academic Terms
- Course Offerings
- Sections
- Section Meetings

Planning:

- Ed Plans
- Plan Courses
- Validation
- Graduation Audit

Scheduling:

- Plan Sections
- Plan Schedules
- Availability Constraints
- Timetable Generation
- Attendance Optimization

No refactor is recommended immediately. The correct next step is to keep this as an explicit
architectural debt note, complete the Planning domain, and move catalog/reference modules only in a
dedicated boundary refactor.
