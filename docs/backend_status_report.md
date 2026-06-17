# Backend Status Report

Generated: 2026-06-17

## Current Architecture Overview

The backend is a FastAPI application under `fastapi_backend/app`. `app/main.py` creates the FastAPI app, configures CORS, creates database tables from SQLAlchemy metadata on startup, and mounts the student and global API routers.

The active backend shape is domain-oriented:

- API route modules receive HTTP requests and return response envelopes.
- Service modules own validation, orchestration, error handling, commits, and user-facing behavior.
- Repository modules own database reads and writes through `AsyncSession`.
- SQLAlchemy models define the live relational entities used by the route/service/repository stack.
- Pydantic schemas define request and response contracts.

The main student workflow is built around catalog discovery, normalized education plans, validation, and graduation audit. Older `/users/education-plan` routes still exist for compatibility with existing frontend payloads.

## Domain Structure

Primary implemented domains:

- `student.domains.discovery`: universities, programs, courses, prerequisites, and corequisites.
- `student.domains.scheduling`: academic terms, offerings, sections, and meetings as catalog reads only.
- `student.domains.planning`: normalized plans, plan courses, validation, graduation audit, and legacy plan compatibility routes.
- `student.domains.auth`: user registration, login, and disabled email-verification stubs.
- `student.domains.onboarding`: intake submission persistence.
- `student.domains.notifications`: advisor email notification handoff.
- `api.routes.global_data`: country and state lookup endpoints.

Empty package placeholders exist for agents, career, finance, academics, institution roles, plugins, and shared contracts. They are not implemented feature layers.

## Route -> Service -> Repository Pattern

The current pattern is consistent in the main backend domains:

- Routes live in `api/*.py` modules and depend on `get_db`.
- Routes call a domain service singleton or service function.
- Services validate UUIDs and request invariants, raise `HTTPException`, and coordinate commits/rollbacks for writes.
- Repositories compose SQLAlchemy queries and translate ORM models into response dictionaries.

Examples:

- `GET /api/universities` -> `UniversityService.search_universities` -> `UniversityRepository.list_universities` -> `universities`.
- `GET /api/programs/{program_id}` -> `ProgramService.get_program_by_id` -> `ProgramRepository.get_program_by_id` -> `programs`, `universities`, `courses`.
- `POST /api/plans` -> `NormalizedPlanService.create_plan` -> `NormalizedPlanRepository.create_plan` -> `ed_plans`.
- `POST /api/plans/{plan_id}/validate` -> `PlanningValidationService.validate_plan` -> `PlanningValidationRepository` -> `ed_plans`, `plan_courses`, `courses`, `course_prerequisites`, `course_corequisites`, `academic_terms`.
- `GET /api/plans/{plan_id}/audit` -> `GraduationAuditService.get_audit` -> `GraduationAuditRepository` -> `ed_plans`, `plan_courses`, `programs`, `courses`.

## Live PostgreSQL Tables Currently Used

Tables actively referenced by implemented backend code:

- Identity and support: `users`, `customers`, `countries`, `states`, `intake_submissions`.
- Legacy planning compatibility: `education_plans`, `program_courses`, `course_schedules`, `course_reschedules`.
- Catalog discovery: `universities`, `programs`, `courses`, `course_prerequisites`, `course_corequisites`.
- Scheduling catalog: `academic_terms`, `course_offerings`, `sections`, `section_meetings`.
- Normalized planning: `ed_plans`, `plan_courses`.

Tables documented in the live database schema but not currently wired to implemented route behavior include career mapping tables and future schedule/section planning tables such as `careers`, `program_careers`, `course_careers`, `plan_sections`, `plan_schedules`, `login_history`, and `email_otps`.

## API Inventory By Domain

Discovery:

- `GET /api/universities`
- `GET /api/universities/{unit_id}`
- `POST /api/universities/compare`
- `GET /api/programs`
- `GET /api/programs/{program_id}`
- `GET /api/programs/{program_id}/courses`
- `GET /api/courses`
- `GET /api/courses/{course_id}`
- `GET /api/courses/{course_id}/prerequisites`
- `GET /api/courses/{course_id}/corequisites`
- `GET /api/global/countries`
- `GET /api/global/states/{country_id}`

Catalog:

- `GET /api/terms`
- `GET /api/terms/{id}`
- `GET /api/courses/{id}/offerings`
- `GET /api/offerings/{id}`
- `GET /api/offerings/{id}/sections`
- `GET /api/sections/{id}`
- `GET /api/sections/{id}/meetings`

Planning:

- `GET /api/plans`
- `POST /api/plans`
- `GET /api/plans/{plan_id}`
- `PATCH /api/plans/{plan_id}`
- `DELETE /api/plans/{plan_id}`
- `GET /api/plans/{plan_id}/courses`
- `POST /api/plans/{plan_id}/courses`
- `PATCH /api/plans/{plan_id}/courses/{course_id}`
- `DELETE /api/plans/{plan_id}/courses/{course_id}`
- Legacy compatibility: `POST /api/users/education-plan`, `/query`, `/list`, `/delete`, `/reschedule`

Validation:

- `POST /api/plans/{plan_id}/validate`
- `POST /api/plans/{plan_id}/validate-course`

Graduation audit:

- `GET /api/plans/{plan_id}/audit`

Supporting user/onboarding endpoints:

- `GET /`
- `POST /api/users`
- `POST /api/users/login`
- `POST /api/users/email-verification/request`
- `GET /api/users/email-verification/status`
- `POST /api/users/email-advisor`
- `POST /api/intake`

## Current Student Workflow

1. University
   - Search or browse universities with `GET /api/universities`.
   - Select a university by `university_id`.

2. Program
   - List programs with `GET /api/programs?university_id={university_id}`.
   - Select a program by `program_id`.

3. Courses
   - List program courses with `GET /api/programs/{program_id}/courses` or `GET /api/courses?program_id={program_id}`.
   - Inspect prerequisites and corequisites with the course relationship endpoints.

4. Create Plan
   - Create a normalized plan with `POST /api/plans`.
   - Required IDs are `user_id`, `university_id`, and `program_id`.

5. Add Courses
   - Add catalog courses with `POST /api/plans/{plan_id}/courses`.
   - Optional `planned_term_id` can link a course to an academic term.

6. Validate Plan
   - Validate the full plan with `POST /api/plans/{plan_id}/validate`.
   - Validate a candidate add/update with `POST /api/plans/{plan_id}/validate-course`.

7. Graduation Audit
   - Audit progress with `GET /api/plans/{plan_id}/audit`.
   - The audit compares planned courses against the selected program catalog.

## Current Test Counts

Available from the repository:

- Test files under `fastapi_backend/tests`: 17.
- Static test function count from `rg "^def test_|^async def test_"`: 70.

Pytest collection could not be run in this environment because `pytest` is not installed in the bundled backend virtualenv.

## Known Limitations

- The 18-credit limit is temporary and centralized as `MAX_TERM_CREDITS`.
- Add/update plan-course endpoints expose the credit limit but do not block saves; validation reports credit-limit issues.
- Graduation audit treats planned courses as completed for progress calculations.
- There is no transcript system.
- There is no transfer credit system.
- There are no substitutions or waivers.
- There is no schedule generation.
- There is no implemented agent layer.
- There is no recommendation engine or AI functionality.
- Email verification is disabled and returns permissive stub responses.
- Legacy `/users/education-plan` routes persist JSON payloads and do not use the normalized plan model.
- Scheduling catalog endpoints are read-only catalog data; they do not build a student schedule.

## Future Roadmap Items

- Transcript ingestion and completed-course tracking.
- Transfer credit, substitutions, waivers, and exception handling.
- Degree-rule model beyond catalog course membership.
- Enforced credit policies at write time once product rules are finalized.
- Schedule generation using terms, offerings, sections, and meetings.
- Section selection and conflict detection for actual student schedules.
- Advisor review workflow and graduation readiness approvals.
- Agent layer only after deterministic workflows are stable.
- Recommendation engine only after catalog, audit, and transcript foundations are complete.
