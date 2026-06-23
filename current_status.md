# Current System Analysis Report

Generated: 2026-06-23

Scope: Student Platform backend under `fastapi_backend/app`, supporting docs under `docs`, and backend tests under `fastapi_backend/tests`.

Note: `development_plan.md` was requested as the comparison target, but no file with that name exists in the repository. This review compares the backend against the planned module architecture documented in `docs/orchestrator_module_developer_guide.md`, `docs/domain_map.md`, `docs/domain_boundary_review.md`, and related planning docs.

## Executive Summary

The backend is a FastAPI application with a domain-oriented structure. The strongest implemented areas are catalog discovery, normalized academic planning, validation, graduation audit, scheduling catalog lookup, auth, onboarding intake, and a generic orchestrator framework.

Academic Planning is the most complete planned module. It has normalized plan CRUD, plan-course CRUD, deterministic validation, graduation audit, tests, and a thin tool layer.

Scheduling is partial. The backend has course offerings, sections, and section meetings as read-only catalog data, plus a legacy reschedule queue. It does not generate schedules, select sections for a student plan, persist normalized schedules, or perform time conflict detection.

Career, Finance, Academic Success, and College Comparison are not implemented as first-class backend modules. Some supporting data exists for Career and College Comparison, but there are no dedicated student-domain APIs, services, repositories, schemas, or tools for those planned modules.

## Domain Structure

### Student Auth

Purpose: User registration, login, profile response, and disabled email-verification compatibility.

Status: Partial.

APIs:
- `POST /api/users`
- `POST /api/users/login`
- `POST /api/users/email-verification/request`
- `GET /api/users/email-verification/status`

Services:
- `student.domains.auth.services.user_service`

Repositories:
- `student.domains.auth.repositories.user_repository`

Schemas:
- `student.domains.auth.schemas.auth`

Findings:
- Registration and login are implemented.
- Email verification is explicitly disabled and returns permissive stub responses.
- The live schema docs mention `email_otps` and `login_history`, but active route behavior does not use them.

### Discovery / Catalog

Purpose: Browse universities, programs, courses, prerequisites, and corequisites.

Status: Partial to complete for current catalog browsing.

APIs:
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

Services:
- `UniversityService`
- `ProgramService`
- `CourseService`

Repositories:
- `UniversityRepository`
- `ProgramRepository`
- `CourseRepository`
- `CollegeScorecardRepository`

Schemas:
- `university.py`
- `program.py`
- `course.py`

Models:
- `University`
- `Program`
- `Course`
- `CoursePrerequisite`
- `CourseCorequisite`

Findings:
- Internal catalog browsing is implemented and tested.
- University comparison exists but is closer to catalog comparison than a complete planned College Comparison module.
- A College Scorecard client exists, but core university repository responses currently appear database-centered and several scorecard-style fields are nullable.

### Academic Planning

Purpose: Manage student education plans, selected plan courses, validation, and graduation audit.

Status: Partial, close to complete for first-version normalized planning.

APIs:
- `GET /api/plans`
- `POST /api/plans`
- `GET /api/plans/{plan_id}`
- `PATCH /api/plans/{plan_id}`
- `DELETE /api/plans/{plan_id}`
- `GET /api/plans/{plan_id}/courses`
- `POST /api/plans/{plan_id}/courses`
- `PATCH /api/plans/{plan_id}/courses/{course_id}`
- `DELETE /api/plans/{plan_id}/courses/{course_id}`
- `POST /api/plans/{plan_id}/validate`
- `POST /api/plans/{plan_id}/validate-course`
- `GET /api/plans/{plan_id}/audit`
- Legacy compatibility: `POST /api/users/education-plan`
- Legacy compatibility: `POST /api/users/education-plan/query`
- Legacy compatibility: `POST /api/users/education-plan/list`
- Legacy compatibility: `POST /api/users/education-plan/delete`

Services:
- `NormalizedPlanService`
- `PlanningValidationService`
- `GraduationAuditService`
- `education_plan_service` legacy compatibility service

Repositories:
- `NormalizedPlanRepository`
- `PlanCourseRepository`
- `PlanningValidationRepository`
- `GraduationAuditRepository`
- `plan_repository` legacy compatibility repository
- `reschedule_repository`

Schemas:
- `normalized_plan.py`
- `planning_validation.py`
- `graduation_audit.py`
- `education.py` legacy compatibility schemas

Models:
- `EdPlan`
- `PlanCourse`
- Legacy shared models: `EducationPlan`, `ProgramCourse`, `CourseSchedule`, `CourseReschedule`

Tool layer:
- `create_plan`
- `update_plan`
- `delete_plan`
- `get_plan`
- `add_course`
- `remove_course`
- `move_course`
- `validate_plan`
- `audit_plan`

Implemented features:
- Normalized plan list/create/read/update/deactivate.
- Plan-course list/add/update/delete.
- Course move through plan-course update.
- Deterministic validation for duplicate courses, prerequisites, corequisites, and 18-credit term limit.
- Candidate course validation for add/update style checks.
- Graduation audit against program catalog courses.
- Legacy JSON plan persistence for existing frontend compatibility.

Partial or missing behavior:
- Validation reports issues but does not block plan-course writes.
- `MAX_TERM_CREDITS = 18` is hard-coded.
- Graduation audit treats planned courses as completed because no transcript or completed-course source of truth exists.
- No transcript, transfer credit, substitutions, waivers, advisor approval, or persisted audit history.
- Future planning tools listed in the module README are not implemented: `generate_plan`, `optimize_plan`, `forecast_graduation`.

### Scheduling Catalog

Purpose: Expose academic terms, course offerings, sections, and section meetings.

Status: Partial. Catalog lookup exists; true scheduling does not.

APIs:
- `GET /api/terms`
- `GET /api/terms/{id}`
- `GET /api/courses/{id}/offerings`
- `GET /api/offerings/{id}`
- `GET /api/offerings/{id}/sections`
- `GET /api/sections/{id}`
- `GET /api/sections/{id}/meetings`
- Legacy compatibility: `POST /api/users/education-plan/reschedule`

Services:
- `TermService`
- `CourseOfferingService`
- `SectionService`
- `SectionMeetingService`
- Legacy reschedule behavior is routed through `education_plan_service.save_reschedule_for_request`

Repositories:
- `TermRepository`
- `CourseOfferingRepository`
- `SectionRepository`
- `SectionMeetingRepository`
- `reschedule_repository`

Schemas:
- `scheduling.schemas.catalog`
- Legacy reschedule schema in `planning.schemas.education`

Models:
- `AcademicTerm`
- `CourseOffering`
- `Section`
- `SectionMeeting`
- Legacy `CourseReschedule`

Findings:
- Course offerings, sections, and section meetings exist as read-only catalog/reference data.
- `section_meetings` has a conflict-lookup index, but no conflict-detection service uses it.
- `plan_sections` and `plan_schedules` are documented in the live schema but have no checked-in SQLAlchemy models, repositories, services, routes, or tests.
- The scheduling package currently contains catalog data, which is a known boundary mismatch documented in `docs/domain_boundary_review.md`.

### Onboarding

Purpose: Persist intake form submissions.

Status: Partial.

APIs:
- `POST /api/intake`

Services:
- `intake_service.save_submission`

Repositories:
- `intake_repository`

Schemas:
- No explicit Pydantic request schema; the route accepts raw `dict`.

Models:
- `IntakeSubmission`

Findings:
- Intake persistence exists.
- Contract is loose because request data is untyped.

### Notifications

Purpose: Notify an advisor by email handoff.

Status: Partial.

APIs:
- `POST /api/users/email-advisor`

Services:
- `notification_service.notify_advisor`

Repositories:
- None found.

Schemas:
- None found; route accepts raw `dict`.

Findings:
- Endpoint validates minimal fields and delegates to a notification service.
- There is no persisted notification record or typed request contract.

### Global Data

Purpose: Country and state lookup.

Status: Complete for current lookup needs.

APIs:
- `GET /api/global/countries`
- `GET /api/global/states/{country_id}`

Services:
- `global_service.list_countries`
- `global_service.list_states`

Repositories:
- Direct SQLAlchemy selects in service layer.

Schemas:
- `global_data.py`

Models:
- `Country`
- `State`

### Orchestrator

Purpose: Provide generic student-agent workflow coordination.

Status: Partial framework; production modules not registered/implemented.

Implemented components:
- `ContextLoader`
- `IntentRouter`
- `ModuleSelector`
- `ModuleExecutor`
- `ResponseComposer`
- `MemoryManager`
- `RunTracker`
- `WorkflowTracker`
- `StudentOrchestrator`
- `ModuleRegistry`
- `BaseModule`
- `ExampleModule`
- OpenRouter provider abstraction and prompt registry

Official planned modules:
- `Academic Planning`
- `Scheduling`
- `Career`
- `Finance`
- `Academic Success`
- `College Comparison`

Findings:
- Intent routing recognizes all planned module categories.
- Module selection validates official names.
- Missing registry modules are returned as `"Module not yet implemented"`.
- The implemented planning tool layer is not yet wrapped as an orchestrator `BaseModule`.

### Career

Purpose: Planned career guidance, career mappings, outcomes, internships, and related recommendations.

Status: Missing as a backend module.

APIs: None found.

Services: None found.

Repositories: None found.

Schemas: None found.

Models:
- No checked-in SQLAlchemy models in `student.domains.career`.
- Live schema docs list `careers`, `program_careers`, and `course_careers`.

Findings:
- Career data structures exist in the live schema documentation only.
- No career API, service, repository, tool, or orchestrator module is implemented.

### Finance

Purpose: Planned finance guidance, scholarships, financial aid, tuition data, and cost estimation.

Status: Missing.

APIs: None found.

Services: None found.

Repositories: None found.

Schemas: None found.

Models: None found.

Findings:
- Discovery university schemas include some financial fields such as debt/cost-style values, but this is not a Finance module.
- No scholarship, financial aid, tuition, or cost-estimation domain exists.

### Academic Success

Purpose: Planned risk detection, intervention logic, retention logic, and success metrics.

Status: Missing.

APIs: None found.

Services: None found.

Repositories: None found.

Schemas: None found.

Models: None found.

Findings:
- No GPA, grade, attendance, risk, intervention, retention, or success metric workflow exists.
- College Scorecard retention data may be mapped for universities, but that is institutional comparison data, not student success logic.

## Academic Planning Module

### Existing Features

Plan CRUD: Partial.
- Normalized plan list/create/read/update/deactivate exists.
- Delete is implemented as deactivation.
- Legacy JSON-backed plan add/query/list/delete still exists.

Plan Courses: Partial.
- Add/list/update/delete courses in a normalized plan exists.
- Move course exists through `move_course` tool and `PATCH /api/plans/{plan_id}/courses/{course_id}`.
- No section-level selection or transcript status source exists.

Validation: Partial.
- Implemented checks: duplicates, prerequisites, corequisites, term credit limit.
- Validation can run for full plan or candidate course.
- Validation does not enforce writes.
- No grouped prerequisites, minimum grade rules, transfer rules, substitution/waiver handling, or section meeting conflicts.

Graduation Audit: Partial.
- Calculates planned credits, required credits, remaining credits, completion percentage, missing courses, and graduation readiness.
- Treats planned courses as completed.
- Does not use transcript, transfer credit, substitutions, waivers, or advisor approval state.

### Existing APIs

- `GET /api/plans`
- `POST /api/plans`
- `GET /api/plans/{plan_id}`
- `PATCH /api/plans/{plan_id}`
- `DELETE /api/plans/{plan_id}`
- `GET /api/plans/{plan_id}/courses`
- `POST /api/plans/{plan_id}/courses`
- `PATCH /api/plans/{plan_id}/courses/{course_id}`
- `DELETE /api/plans/{plan_id}/courses/{course_id}`
- `POST /api/plans/{plan_id}/validate`
- `POST /api/plans/{plan_id}/validate-course`
- `GET /api/plans/{plan_id}/audit`
- Legacy routes under `/api/users/education-plan`

### Existing Services

- `NormalizedPlanService`
- `PlanningValidationService`
- `GraduationAuditService`
- `education_plan_service`

### Existing Repositories

- `NormalizedPlanRepository`
- `PlanCourseRepository`
- `PlanningValidationRepository`
- `GraduationAuditRepository`
- `plan_repository`
- `reschedule_repository`

### Existing Tool Layer

- `create_plan`: Ready.
- `update_plan`: Ready.
- `delete_plan`: Ready, implemented as deactivation.
- `get_plan`: Ready.
- `add_course`: Ready.
- `remove_course`: Ready.
- `move_course`: Ready.
- `validate_plan`: Ready.
- `audit_plan`: Ready.

### Status

Partial.

Reason: The module has strong first-version CRUD, validation, audit, tests, and tools, but lacks transcript-aware audit, enforcement of validation at write time, generated/optimized plans, forecasting, and advanced degree-rule features.

## Scheduling Capabilities

| Capability | Finding | Status |
| --- | --- | --- |
| Course Offerings | `CourseOffering` model, repository, service, schema, and read APIs exist. | Partial |
| Sections | `Section` model, repository, service, schema, and read APIs exist. | Partial |
| Section Meetings | `SectionMeeting` model, repository, service, schema, and read APIs exist. | Partial |
| Schedule Models | Legacy `CourseSchedule` exists; live schema docs mention `plan_schedules`; no normalized checked-in model or API. | Partial |
| Conflict Detection | No service or API; only a `section_meetings` conflict lookup index exists. | Missing |
| Attendance Logic | No attendance, availability, commute, or attendance optimization logic found. | Missing |

Overall scheduling status: Partial.

## Career Capabilities

| Capability | Finding | Status |
| --- | --- | --- |
| Career Models | Live schema docs list `careers`, `program_careers`, `course_careers`; no checked-in student career models. | Partial |
| Career APIs | None found. | Missing |
| Career Services | None found. | Missing |
| Career Data Sources | Frontend has static career JSON assets; backend has no career data source service. | Missing |

Overall career status: Missing.

## Finance Capabilities

| Capability | Finding | Status |
| --- | --- | --- |
| Scholarships | None found. | Missing |
| Financial Aid | Some university comparison fields exist, but no finance workflow. | Missing |
| Tuition Data | No tuition table, API, or service found. | Missing |
| Cost Estimation | None found. | Missing |

Overall finance status: Missing.

## Student Success Capabilities

| Capability | Finding | Status |
| --- | --- | --- |
| Risk Detection | None found. | Missing |
| Intervention Logic | None found. | Missing |
| Retention Logic | No student-level retention logic; only possible institution retention fields in scorecard mapping. | Missing |
| Success Metrics | None found. | Missing |

Overall student success status: Missing.

## Integration Readiness Review

| Planned Module | Existing Backend Coverage | Required Work |
| --- | --- | --- |
| Academic Planning | 75% | Wrap planning tools/services as an orchestrator `BaseModule`; enforce or explicitly separate validation from writes; add transcript/completed-course source; add generated/optimized plan and graduation forecasting only after rules are stable. |
| Scheduling | 25% | Add normalized `plan_sections` and `plan_schedules` models; build schedule-generation service; implement student availability/constraints; implement conflict detection; expose scheduling APIs and tools. |
| Career | 25% | Add career SQLAlchemy models for existing live tables; create career APIs/services/repositories/schemas; define career guidance contracts; add data source strategy for internships/jobs/outcomes. |
| Finance | 0% | Define finance schema and data sources; add scholarships, aid, tuition, and cost-estimation services; expose APIs and tools. |
| Academic Success | 0% | Define student success data model; add GPA/grade/attendance inputs; implement risk, intervention, retention, and metrics services; expose APIs and tools. |
| College Comparison | 25% | Expand beyond `POST /api/universities/compare`; define comparison criteria; integrate cost/outcome/admission/retention fields; add stable data-source behavior and a module/tool contract. |

## Tool Layer Readiness

| Tool | Status | Notes |
| --- | --- | --- |
| `create_plan` | Ready | Existing normalized planning service. |
| `update_plan` | Ready | Existing normalized planning service. |
| `delete_plan` | Ready | Deactivates a plan rather than hard delete. |
| `get_plan` | Ready | Existing normalized planning service. |
| `add_course` | Ready | Existing plan-course service; validation is not enforced. |
| `remove_course` | Ready | Existing plan-course delete service. |
| `move_course` | Ready | Existing plan-course update service. |
| `validate_plan` | Ready | Existing validation service. |
| `audit_plan` | Ready | Existing graduation audit service; transcript-unaware. |
| `generate_plan` | Missing | Listed as future in planning README. |
| `optimize_plan` | Missing | Listed as future in planning README. |
| `forecast_graduation` | Missing | Listed as future in planning README. |
| `build_schedule` | Missing | No scheduling generation service. |
| `detect_conflicts` | Missing | No conflict detection service despite section meeting data. |
| `select_section` | Missing | No normalized plan-section model wired in code. |
| `internship_search` | Missing | No backend career data source or career API. |
| `career_match` | Missing | Career mapping tables are not wired to backend code. |
| `find_scholarships` | Missing | No finance module. |
| `estimate_cost` | Missing | No tuition/cost model or service. |
| `detect_risk` | Missing | No academic success module. |
| `recommend_intervention` | Missing | No intervention model or service. |
| `compare_colleges` | Partial | `POST /api/universities/compare` exists, but no dedicated tool/module contract. |

## Architecture Review

### Alignment

- The backend follows a clear route/service/repository/schema/model structure in main domains.
- Discovery, Planning, Validation, Audit, and Scheduling Catalog are separated at package level.
- The orchestrator framework matches the documented workflow: context loading, intent routing, module selection, module execution, response composition, and memory update.
- Official planned module names are defined in `ModuleSelector`.
- Planning tools are thin wrappers over domain services and do not contain route logic.
- Tests exist for orchestrator infrastructure, discovery, planning, validation, audit, and scheduling catalog metadata/service/repository behavior.

### Gaps

- `development_plan.md` is absent.
- Production orchestrator modules are not implemented or registered.
- Academic Planning is not yet an orchestrator `BaseModule`.
- Scheduling package currently contains catalog/reference data, not true scheduling workflows.
- Career, Finance, Academic Success, and true College Comparison are missing backend domains.
- Live schema docs include tables not covered by checked-in models/routes, including career mappings and normalized scheduling tables.
- Checked-in Alembic migrations stop at `0004`, while live schema docs report Alembic live version `0008`.

### Refactoring Needs

- Introduce a dedicated Catalog boundary for universities, programs, courses, prerequisites, corequisites, terms, offerings, sections, and meetings when route stability allows.
- Keep Discovery as a product experience over Catalog rather than the owner of all catalog persistence.
- Move scheduling catalog code out of `student.domains.scheduling` before implementing true timetable generation, or clearly isolate the new true scheduling services beside the existing catalog code.
- Reconcile SQLAlchemy metadata imports and Alembic migration history with the live database.
- Add typed Pydantic schemas for raw-dict routes in onboarding and notifications.
- Decide whether validation should block writes or remain advisory, then encode that contract consistently in APIs and tools.

## Risk Assessment

### Data Risks

- Missing data sources for Finance, Career workflows, Academic Success, and internships/jobs.
- Live database contains tables not represented in checked-in migrations or models.
- Local migrations do not appear to recreate the documented live normalized schema.
- Graduation audit has no transcript or completed-course source of truth.
- Scheduling depends on offering/section/meeting completeness; no evidence of seed freshness or external sync exists.
- Career tables may exist live but are not accessible through backend code.

### Technical Risks

- Catalog/reference data is split between Discovery and Scheduling, creating future ownership ambiguity.
- Legacy planning tables and normalized planning tables both remain active.
- Validation business rules are duplicated conceptually across docs and services, and not enforced on writes.
- Hard-coded `MAX_TERM_CREDITS = 18` may not match institutional or program-specific policy.
- Raw `dict` request bodies reduce contract safety in onboarding and notifications.
- Alembic metadata appears incomplete relative to live schema, making autogenerate and fresh environment setup risky.

### Integration Risks

- Orchestrator can route to modules that are not implemented, producing unavailable module results.
- Planning tools are ready but not connected to a production orchestrator module.
- Scheduling tools cannot be implemented cleanly until normalized schedule/section selection services exist.
- Career/Finance/Academic Success tools have no backend contracts.
- College comparison has a basic university comparison endpoint but no planned module/tool abstraction.
- Frontend static assets for schedule/career may not align with backend source-of-truth APIs.

## Recommendations

### Immediate Priorities: Next 1 Week

- Create or restore the missing `development_plan.md`, or declare the existing orchestrator/planning docs as the architecture source of truth.
- Wrap Academic Planning services/tools in an orchestrator `BaseModule` and register it in a controlled test setup.
- Reconcile Alembic migrations and SQLAlchemy metadata with the documented live schema.
- Document the validation contract: advisory-only versus write-blocking.
- Add typed request schemas for intake and advisor notification endpoints.
- Preserve current route URLs while documenting the Catalog versus Scheduling boundary.

### Beta Priorities: Before July 4

- Complete first-version Academic Planning integration through the orchestrator.
- Add transcript/completed-course status model or explicitly mark audit as plan-completion audit rather than graduation completion audit.
- Implement minimum viable schedule conflict detection over existing `sections` and `section_meetings`.
- Add normalized scheduling models/services for `plan_sections` and `plan_schedules` if those tables remain part of the live schema.
- Create minimal Career read APIs if career tables are part of beta scope.
- Create a dedicated College Comparison service contract if comparison is expected in beta.

### Post-Beta Priorities: After July 4

- Refactor Catalog into a first-class domain and let Discovery/Scheduling consume it.
- Implement full schedule generation with availability, constraints, section scoring, and conflict resolution.
- Build Finance domain with tuition, aid, scholarship, and cost-estimation data sources.
- Build Academic Success domain with risk detection, interventions, retention metrics, and student outcome signals.
- Expand Career with program/course-to-career mapping, internships/jobs data source integration, and career recommendation tools.
- Add advanced planning rules: transfer credit, substitutions, waivers, minimum grades, grouped prerequisites, advisor overrides, and persisted audit history.
