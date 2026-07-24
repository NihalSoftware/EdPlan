# Current System Analysis Report

Generated: 2026-06-23

Scope: Current merged repository state for the Student Platform backend under `fastapi_backend/app`, Alembic migrations under `fastapi_backend/alembic`, tests under `fastapi_backend/tests`, and architecture docs under `docs`.

Important note: `development_plan.md` is still not present in the repository. Architecture comparison is therefore based on the current planned-module contract in `docs/orchestrator_module_developer_guide.md`, current backend code, and the official module names in `app/orchestrator/router/module_selector.py`.

## Executive Summary

The merged backend is stronger than the previous status report in three areas:

- Alembic migrations now include normalized catalog, planning, career-mapping, scheduling, and agentic tables through revision `0009`.
- SQLAlchemy metadata now imports normalized discovery, scheduling catalog, planning, legacy, onboarding, user, and agentic models.
- Orchestrator infrastructure now includes durable run tracking, workflow events, module execution tracking, deterministic memory/preference extraction, prompt registry/manager, provider-neutral LLM contracts, and an OpenRouter provider stub.

The main implementation reality has not changed as much as the data model. Academic Planning remains the only planned product module with a real tool layer. Scheduling has catalog lookup but not schedule generation. Career, Finance, Academic Success, and College Comparison have routing/prompt labels but no production domain modules or tool registries.

## Merge Impact Analysis

### Newly Added Or Now Present Components

APIs:
- No new student product API surface was found beyond the existing auth, discovery, scheduling catalog, planning, graduation audit, reschedule, notifications, onboarding, and global data endpoints.

Services:
- Orchestrator service layer is present through `StudentOrchestrator`.
- Durable orchestrator helpers are present: `RunTracker`, `WorkflowTracker`, and `MemoryManager`.
- Provider/prompt services are present: `PromptManager`, `PromptRegistry`, `OpenRouterProvider`.

Repositories:
- No new product-domain repositories were found for Career, Finance, Academic Success, College Comparison, or true Scheduling.
- Existing repositories remain centered on Discovery, Scheduling Catalog, Planning, Auth, Onboarding, and legacy reschedule/plan persistence.

Schemas:
- Provider-neutral LLM schemas exist: `LLMMessage`, `LLMRequest`, `LLMResponse`, `LLMUsage`, `LLMHealthCheck`.
- Orchestrator schemas exist for intent results, module responses, student context, workflow events, and orchestrator state.
- Agentic SQLAlchemy models exist for run/memory/observability persistence.

Modules:
- `app/models/agentic.py` now defines agentic persistence models.
- `app/orchestrator/*` contains a full orchestration scaffold.
- `student.domains.planning.module` exposes Planning module metadata and tools.

Tool layers:
- Academic Planning tool registry exists with 9 tools.
- No Scheduling, Career, Finance, Academic Success, or College Comparison tool registry exists.

Provider integrations:
- OpenRouter provider abstraction exists as a stub.
- Network calls are intentionally disabled.
- Health check returns configured/stub status.

Database/migrations:
- Migrations now run from `0001` through `0009`.
- `0005` creates normalized catalog/planning/career/scheduling tables.
- `0006` links normalized plans to legacy education plans.
- `0007` and `0008` adjust active plan schedule behavior.
- `0009` creates the `agentic` schema with orchestrator run, workflow, module execution, student preference, and conversation memory tables.

### Modified Components

Database metadata:
- `app/models/__init__.py` now imports normalized discovery, scheduling, planning, legacy, onboarding, user, and agentic models.
- This is a material improvement over the earlier state where migration/metadata coverage was incomplete.

Orchestrator:
- `StudentOrchestrator` now wires graph execution, durable run tracking, workflow events, module execution traces, and memory update hooks.
- `ModuleSelector` recognizes official planned modules.
- `IntentRouter` has deterministic rules for Academic Planning, Scheduling, Career, Finance, Academic Success, and College Comparison.

LLM infrastructure:
- Provider-neutral contracts and prompt registry are present.
- `OpenRouterProvider` is a tested stub, not a live API client.

Academic Planning:
- Tool registry and module metadata are present and tested.
- Normalized planning APIs/services/repositories remain the most complete domain implementation.

Database schema:
- Career and normalized scheduling tables are now included in migrations, but still not implemented as active product services/routes.

### Deleted Components

No deleted first-party backend components were identified from the current tree. Empty package placeholders still exist for `career`, `finance`, and `academics`.

## Current Domain Inventory

### Auth

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

Models/tables:
- `users`
- `customers`
- `email_otps` exists in migration `0003` but active email verification is disabled.
- `login_history` exists in migration `0005` but is not actively used by login routes.

Findings:
- Registration and login are implemented.
- Email verification remains a permissive disabled stub.
- Login history persistence is not wired to auth service behavior.

### Discovery / Catalog

Status: Partial to strong for internal catalog browsing.

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

Models/tables:
- `universities`
- `programs`
- `courses`
- `course_prerequisites`
- `course_corequisites`

Findings:
- Discovery is the primary read interface for academic catalog data.
- College Scorecard client/repository code exists, but the production comparison endpoint is still a simple university comparison endpoint rather than a full College Comparison module.

### Academic Planning

Status: Partial, highest-readiness planned module.

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
- Legacy: `POST /api/users/education-plan`
- Legacy: `POST /api/users/education-plan/query`
- Legacy: `POST /api/users/education-plan/list`
- Legacy: `POST /api/users/education-plan/delete`

Services:
- `NormalizedPlanService`
- `PlanningValidationService`
- `GraduationAuditService`
- `education_plan_service`

Repositories:
- `NormalizedPlanRepository`
- `PlanCourseRepository`
- `PlanningValidationRepository`
- `GraduationAuditRepository`
- `plan_repository`
- `reschedule_repository`

Schemas:
- `normalized_plan.py`
- `planning_validation.py`
- `graduation_audit.py`
- `education.py`

Models/tables:
- `ed_plans`
- `plan_courses`
- `education_plans`
- `program_courses`
- `course_schedules`
- `course_reschedules`

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

Validation:
- Duplicate course detection.
- Prerequisite validation by term order.
- Corequisite same-term validation.
- Term credit limit check using `MAX_TERM_CREDITS = 18`.

Graduation audit:
- Calculates planned credits, required credits, remaining credits, missing catalog courses, completion percentages, and readiness flag.

Limitations:
- Validation reports issues but does not block plan-course writes.
- Audit treats planned courses as completed because there is no transcript/completed-course source of truth.
- No transfer credits, substitutions, waivers, minimum grade rules, grouped prerequisites, advisor overrides, or persisted audit history.
- Planning tools are not yet wrapped as an official `BaseModule` named `Academic Planning` for orchestrator execution.

Completion estimate: 75%.

### Scheduling

Status: Partial.

APIs:
- `GET /api/terms`
- `GET /api/terms/{id}`
- `GET /api/courses/{id}/offerings`
- `GET /api/offerings/{id}`
- `GET /api/offerings/{id}/sections`
- `GET /api/sections/{id}`
- `GET /api/sections/{id}/meetings`
- Legacy: `POST /api/users/education-plan/reschedule`

Services:
- `TermService`
- `CourseOfferingService`
- `SectionService`
- `SectionMeetingService`
- Legacy reschedule behavior through `education_plan_service`

Repositories:
- `TermRepository`
- `CourseOfferingRepository`
- `SectionRepository`
- `SectionMeetingRepository`
- `reschedule_repository`

Schemas:
- `scheduling.schemas.catalog`
- Legacy reschedule schema in `planning.schemas.education`

Models/tables:
- Active models: `AcademicTerm`, `CourseOffering`, `Section`, `SectionMeeting`, `CourseReschedule`, legacy `CourseSchedule`.
- Migrated but not modeled/serviced: `plan_sections`, `plan_schedules`.

Capability status:

| Capability | Status | Finding |
| --- | --- | --- |
| Course Offerings | Implemented | Read-only model/repository/service/API exists. |
| Sections | Implemented | Read-only model/repository/service/API exists. |
| Section Meetings | Implemented | Read-only model/repository/service/API exists. |
| Schedule Models | Partial | Legacy `CourseSchedule` exists; `plan_sections` and `plan_schedules` are migrated but not represented in active models/services/routes. |
| Conflict Detection | Missing | Only a DB index exists on section meeting time fields. No service/API/tool performs conflict checks. |
| Schedule Generation | Missing | No timetable generation, section selection, scoring, or persistence workflow. |

Completion estimate: 25%.

### Career

Status: Missing as a product module; partial data model exists in migrations.

APIs: None found.

Services: None found.

Repositories: None found.

Schemas: None found.

Tool layer: None found.

Models/tables:
- Migrated tables: `careers`, `program_careers`, `course_careers`.
- No checked-in SQLAlchemy model classes for these tables.

Data sources:
- Backend has migrated career mapping tables.
- Frontend static career assets exist outside backend.
- No backend career API/data-source service is implemented.

Completion estimate: 10%.

### Finance

Status: Missing.

APIs: None found.

Services: None found.

Repositories: None found.

Schemas: None found.

Tool layer: None found.

Capabilities:
- Scholarships: Missing.
- Aid data: Missing as a Finance module.
- Tuition data: Missing.
- Cost estimation: Missing.

Related data:
- University/College Scorecard mapping includes some cost/debt-style fields, but no Finance domain exists.

Completion estimate: 0%.

### Academic Success

Status: Missing.

APIs: None found.

Services: None found.

Repositories: None found.

Schemas: None found.

Capabilities:
- Risk detection: Missing.
- Intervention logic: Missing.
- Retention logic: Missing.
- Success metrics: Missing.

Related data:
- College Scorecard client maps institution-level retention fields.
- No student-level success/risk/intervention workflow exists.

Completion estimate: 0%.

### College Comparison

Status: Partial.

Implemented:
- `POST /api/universities/compare` compares selected universities.
- College Scorecard client/repository exists.
- University schema has cost/debt/outcome-style optional fields.

Missing:
- No official `College Comparison` orchestrator module implementation.
- No tool registry.
- No program comparison workflow.
- No formal outcome comparison service.
- No formal cost comparison service.

Capability status:

| Capability | Status | Finding |
| --- | --- | --- |
| University Comparison | Partial | API exists, but comparison logic is basic and catalog-oriented. |
| Program Comparison | Missing | No dedicated API/service. |
| Outcome Comparison | Partial | Scorecard-style fields exist, but no comparison service contract. |
| Cost Comparison | Partial | Some fields exist, but no Finance/Cost service. |

Completion estimate: 25%.

### Onboarding

Status: Partial.

API:
- `POST /api/intake`

Service:
- `intake_service.save_submission`

Repository:
- `intake_repository`

Model/table:
- `intake_submissions`

Finding:
- Persistence exists, but request body is raw `dict`; no typed request schema is present.

### Notifications

Status: Partial.

API:
- `POST /api/users/email-advisor`

Service:
- `notification_service.notify_advisor`

Finding:
- Minimal advisor notification handoff exists.
- No typed request schema or persisted notification record.

### Global Data

Status: Implemented for current lookup needs.

APIs:
- `GET /api/global/countries`
- `GET /api/global/states/{country_id}`

Service:
- `global_service`

Models/tables:
- `countries`
- `states`

## Agent Architecture Review

### Implemented Orchestrator Components

- `StudentOrchestrator`
- `StudentGraph`
- `build_student_graph`
- `ContextLoader`
- `IntentRouter`
- `ModuleSelector`
- `ModuleExecutor`
- `ResponseComposer`
- `MemoryManager`
- `RunTracker`
- `WorkflowTracker`
- `ModuleRegistry`
- `BaseModule`
- `ExampleModule`
- `PromptRegistry`
- `PromptManager`
- `BaseLLMProvider`
- `OpenRouterProvider`
- LLM request/response/health schemas

### Agentic Persistence

Migration `0009` creates:
- `agentic.orchestrator_runs`
- `agentic.workflow_events`
- `agentic.module_executions`
- `agentic.student_preferences`
- `agentic.conversation_memory`

Models in `app/models/agentic.py` map these tables.

### OpenRouter Integration

Status: Partial.

Findings:
- `BaseLLMProvider` abstraction exists.
- `OpenRouterProvider` exists.
- Request payload construction exists.
- Response parsing exists.
- Health check exists.
- Tests cover payload construction and stub responses.
- Network calls are disabled by design.
- API key handling/live OpenRouter calls are not implemented.

### Routing and Selection

Status: Partial.

Findings:
- Deterministic routing rules exist for all official planned modules.
- Module selection validates official module names.
- Module executor returns `"Module not yet implemented"` for unregistered selected modules.
- Only `ExampleModule` exists as a `BaseModule` implementation.
- Academic Planning has tools but not a production `BaseModule` wrapper named `Academic Planning`.

### Architecture Alignment

Modules already matching planned architecture:
- Orchestrator framework components match the documented workflow.
- Academic Planning domain has service-backed tools.
- Discovery/Catalog supports Planning and College Comparison foundations.
- Scheduling Catalog supports future Scheduling inputs.

Modules requiring refactoring:
- Academic Planning needs an official `BaseModule` adapter for orchestrator execution.
- Scheduling package currently owns catalog/reference data and should eventually split true Scheduling from Catalog.
- Context loading mixes normalized `EdPlan` with legacy `EducationPlan`; this may need simplification before production orchestration.
- College Comparison should become a first-class service/module instead of only a university endpoint.

Missing planned modules:
- Scheduling production module.
- Career module.
- Finance module.
- Academic Success module.
- College Comparison module.

Orchestrator readiness: Partial.

Reason: The framework, durable tracking, prompt scaffolding, memory, routing, and provider contracts exist. Production module implementations, live LLM calls, tool selection/execution over domain tools, and API exposure for orchestrated conversations are still missing.

## Tool Layer Audit

### Academic Planning Tools

| Tool | Exists | Service Connected | Tested |
| --- | --- | --- | --- |
| `create_plan` | Yes | Yes, `NormalizedPlanService.create_plan` | Yes, checked-in delegation test. |
| `update_plan` | Yes | Yes, `NormalizedPlanService.update_plan` | Yes, checked-in delegation test. |
| `delete_plan` | Yes | Yes, `NormalizedPlanService.deactivate_plan` | Yes, checked-in delegation test. |
| `get_plan` | Yes | Yes, `NormalizedPlanService.get_plan_by_id` | Yes, checked-in delegation test. |
| `add_course` | Yes | Yes, `NormalizedPlanService.add_plan_course` | Yes, checked-in delegation test. |
| `remove_course` | Yes | Yes, `NormalizedPlanService.delete_plan_course` | Yes, checked-in delegation test. |
| `move_course` | Yes | Yes, `NormalizedPlanService.update_plan_course` | Yes, checked-in delegation test. |
| `validate_plan` | Yes | Yes, `PlanningValidationService.validate_plan` | Yes, checked-in delegation test. |
| `audit_plan` | Yes | Yes, `GraduationAuditService.get_audit` | Yes, checked-in delegation test. |

### Other Tool Registries

| Module | Tool Registry Exists | Service Connected | Tested |
| --- | --- | --- | --- |
| Scheduling | No | No | No |
| Career | No | No | No |
| Finance | No | No | No |
| Academic Success | No | No | No |
| College Comparison | No | No | No |

Verification note:
- Attempted selected pytest run using bundled venv.
- Collection failed because `langgraph` is missing from the local venv, even though `requirements.txt` and `pyproject.toml` declare `langgraph>=0.2.60`.
- Command attempted: `./venv/bin/python -m pytest tests/orchestrator/test_llm_infrastructure.py tests/student/domains/planning/test_academic_planning_module.py tests/student/domains/scheduling/test_catalog_service.py`.

## Database Audit (Latest)

Source: Read-only live database inspection using the configured `DATABASE_URL` from `fastapi_backend/.env`.

Connection note:
- The app settings object currently fails to load `.env` because `DEBUG` has a non-boolean value and `OPENROUTER_API_KEY` is not declared on `Settings`.
- The audit connected by reading only `DATABASE_URL` directly and did not print secrets.

### Schemas

Schemas visible in the database:
- `agentic`
- `information_schema`
- `pg_catalog`
- `public`

Application schemas:
- `public`
- `agentic`

### Tables And Row Counts

| Schema | Table | Row Count |
| --- | --- | ---: |
| `agentic` | `conversation_memory` | 0 |
| `agentic` | `module_executions` | 0 |
| `agentic` | `orchestrator_runs` | 0 |
| `agentic` | `student_preferences` | 0 |
| `agentic` | `workflow_events` | 0 |
| `public` | `academic_terms` | 2 |
| `public` | `alembic_version` | 1 |
| `public` | `careers` | 10 |
| `public` | `countries` | 0 |
| `public` | `course_careers` | 10 |
| `public` | `course_corequisites` | 611 |
| `public` | `course_offerings` | 8 |
| `public` | `course_prerequisites` | 1169 |
| `public` | `course_reschedules` | 1 |
| `public` | `course_schedules` | 0 |
| `public` | `courses` | 6157 |
| `public` | `customers` | 0 |
| `public` | `ed_plans` | 1 |
| `public` | `education_plans` | 28 |
| `public` | `email_otps` | 0 |
| `public` | `intake_submissions` | 65 |
| `public` | `login_history` | 0 |
| `public` | `plan_courses` | 1 |
| `public` | `plan_schedules` | 0 |
| `public` | `plan_sections` | 0 |
| `public` | `program_careers` | 10 |
| `public` | `program_courses` | 750 |
| `public` | `programs` | 363 |
| `public` | `section_meetings` | 18 |
| `public` | `sections` | 10 |
| `public` | `states` | 0 |
| `public` | `universities` | 6 |
| `public` | `users` | 39 |

### Empty Tables

Completely empty:
- `agentic.conversation_memory`
- `agentic.module_executions`
- `agentic.orchestrator_runs`
- `agentic.student_preferences`
- `agentic.workflow_events`
- `public.countries`
- `public.course_schedules`
- `public.customers`
- `public.email_otps`
- `public.login_history`
- `public.plan_schedules`
- `public.plan_sections`
- `public.states`

Nearly empty:
- `public.ed_plans`: 1 row.
- `public.plan_courses`: 1 row.
- `public.course_reschedules`: 1 row.
- `public.academic_terms`: 2 rows.
- `public.course_offerings`: 8 rows.
- `public.sections`: 10 rows.
- `public.section_meetings`: 18 rows.

Likely seeded/demo-only data:
- Many UUIDs use obvious repeated patterns such as `11111111`, `aaaaaaaa`, `bbbbbbbb`, `cccccccc`, `dddddddd`, `eeeeeeee`, `ffffffff`, and `99999999`.
- Sample plan name is `Rudra Test Plan`.
- Scheduling data contains only Fall 2026 and Spring 2027, 8 offerings, 10 sections, and 18 meetings.
- Career data has 10 broad sample careers and 20 total mapping rows.

### Student Module Data Readiness

Academic Planning: Partial.
- `ed_plans`: exists, 1 row.
- `plan_courses`: exists, 1 row.
- `course_prerequisites`: exists, 1169 rows.
- `course_corequisites`: exists, 611 rows.
- `academic_terms`: exists, 2 rows.
- Catalog foundation is strong, but normalized student plan usage is minimal.
- Legacy planning has more data: `education_plans` has 28 rows and `program_courses` has 750 rows.

Scheduling: Partial.
- `academic_terms`: 2 rows.
- `course_offerings`: 8 rows.
- `sections`: 10 rows.
- `section_meetings`: 18 rows.
- `plan_sections`: 0 rows.
- `plan_schedules`: 0 rows.
- Catalog section data exists only as a small demo slice; student schedule persistence is empty.

Career: Partial.
- `careers`: exists, 10 rows.
- `program_careers`: exists, 10 rows.
- `course_careers`: exists, 10 rows.
- Relationships are valid with no detected orphan rows.
- Data exists but appears sample-scale and is not enough for robust recommendations.

Finance: Missing.
- No table found for `tuition`.
- No table found for `financial_aid`.
- No table found for `scholarships`.
- No table found for `cost_estimation`.
- University schemas/code may carry some cost/debt fields from College Scorecard, but the database has no first-class finance domain data.

Academic Success: Missing.
- No table found for `grades`.
- No table found for `gpa`.
- No table found for `attendance`.
- No student-level `retention` table found.
- No `interventions` table found.
- No `student_risk` table found.
- Institution-level retention fields may be available through Scorecard integration, but the live database does not contain student success data.

College Comparison: Partial.
- University comparison: supported by `universities` with 6 rows.
- Program comparison: supported by `programs` with 363 rows.
- Outcome comparison: partial; career mappings exist, but no persisted outcome metrics table was found.
- Cost comparison: missing in database; no tuition/cost/aid tables found.

### Relationship Summary

Primary academic hierarchy:

```text
University
  -> Programs
      -> Courses
          -> Course prerequisites
          -> Course corequisites
          -> Course offerings
              -> Sections
                  -> Section meetings
```

Planning hierarchy:

```text
User
  -> Ed plans
      -> Plan courses
      -> Plan sections
      -> Plan schedules

User
  -> Legacy education plans
      -> Legacy program courses
      -> Legacy course schedules
```

Career hierarchy:

```text
Career
  -> Program career mappings
  -> Course career mappings
```

Agentic hierarchy:

```text
User / Ed plan
  -> Orchestrator runs
      -> Module executions
      -> Workflow events
      -> Conversation memory
  -> Student preferences
```

Relationship health checks:
- Programs without universities: 0.
- Courses without programs: 0.
- Offerings without course or term: 0.
- Sections without offerings: 0.
- Meetings without sections: 0.
- Plan courses without plan or course: 0.
- Plan sections without plan or section: 0.
- Plan schedules without plan: 0.
- Program career mappings without parent rows: 0.
- Course career mappings without parent rows: 0.

Note: the generic FK query showed duplicate-looking lines for the composite `ed_plans(program_id, university_id)` constraint. The effective relationship is `ed_plans(program_id, university_id)` to `programs(program_id, university_id)`.

### Data Quality Review

Good data:
- `universities`: 6 New Mexico institutions.
- `programs`: 363 programs, distributed across 6 universities.
- `courses`: 6157 catalog courses.
- `course_prerequisites`: 1169 relationships.
- `course_corequisites`: 611 relationships.
- Relationship integrity checks found no orphan rows across the audited academic/catalog/career relationships.

Sample/demo data:
- `academic_terms`: only Fall 2026 and Spring 2027.
- `course_offerings`: 8 rows.
- `sections`: 10 rows, 8 open and 2 closed.
- `section_meetings`: 18 rows, 15 class meetings and 3 online async meetings.
- `careers`: 10 broad careers.
- `program_careers`: 10 mappings.
- `course_careers`: 10 mappings.
- UUID patterns and sample labels strongly indicate seeded/demo data in several tables.

Missing or empty data:
- All `agentic` tables are empty.
- `plan_sections` and `plan_schedules` are empty.
- `course_schedules` is empty.
- `countries` and `states` are empty despite global lookup APIs.
- `email_otps` and `login_history` are empty.
- `customers` is empty.
- No finance or academic success domain tables were found.

Suspicious or incomplete data:
- Normalized Planning has only 1 plan and 1 planned course, while legacy planning has 28 plans and 750 program-course rows.
- Scheduling catalog data covers only 8 offerings out of 6157 courses.
- Career mappings cover only 10 programs and 10 courses out of 363 programs and 6157 courses.
- Global country/state lookup endpoints are backed by empty tables.
- Agentic infrastructure tables exist but have no run history, preferences, workflow events, or memory.

### Data Distributions

Application catalog scope:
- Northern New Mexico College: 79 programs exposed by the dedicated site.
- Legacy records outside NNMC are excluded by repository and service filters.

Largest course counts by program:
- Nursing: 291.
- Business Administration: 240.
- Computer Science: 210.
- Elementary Education: 210.
- Biology: 146.
- Psychology: 121.
- Early Childhood Education: 114.
- Information Engineering Technology: 108.
- Mechanical Engineering: 100.
- Automotive Technology: 87.

Offerings by term:
- Fall 2026: 6.
- Spring 2027: 2.

Section status:
- Open: 8.
- Closed: 2.

Career industries:
- Cybersecurity: 2.
- Data: 2.
- Healthcare: 2.
- Technology: 2.
- Business: 1.
- Finance: 1.

### Module Readiness Based On Database

| Module | Database Readiness | Basis |
| --- | ---: | --- |
| Academic Planning | 60% | Strong catalog/rule data, but only 1 normalized plan and 1 plan course; legacy plan data is richer but separate. |
| Scheduling | 20% | Terms/offerings/sections/meetings exist but are tiny sample data; no plan sections or plan schedules. |
| Career | 25% | Career tables and relationships exist, but only 10 careers and 20 mappings total. |
| Finance | 0% | No finance-specific tables or rows. |
| Academic Success | 0% | No student performance, risk, attendance, intervention, or success metric tables. |
| College Comparison | 45% | Universities/programs/courses exist; cost/outcome comparison data is missing or not persisted. |

### Current Database Bottom Line

The database is ready for catalog browsing, basic program/course discovery, and demo-level Academic Planning validation against prerequisites/corequisites. It is not yet ready for production scheduling, finance, academic success, or robust career guidance. Normalized Planning and agentic infrastructure are structurally present but largely unused in the live data.

## Integration Risk Analysis

### Planning Module Risks

- Validation is advisory and does not block writes.
- Audit is not transcript-aware.
- Legacy and normalized planning models both remain in active use.
- Orchestrator context loading still depends on legacy `EducationPlan` for program/university/course context.
- Planning tools are not exposed through an official orchestrator `BaseModule`.

### Scheduling Module Risks

- Catalog lookup may be mistaken for schedule generation.
- `plan_sections` and `plan_schedules` are migrated but not implemented.
- No conflict detection service exists.
- No availability constraints or section scoring exist.
- No scheduling tool layer exists.

### Career Module Risks

- Career tables are migrated but not modeled or routed.
- No data-source ownership exists for internships, jobs, outcomes, or salaries beyond static/migrated fields.
- Career routing and prompts can select a module that is unavailable.

### Finance Module Risks

- No finance data model exists.
- No finance APIs/services/tools exist.
- College comparison and finance concerns may blur if cost fields remain only in university schemas.

### Academic Success Module Risks

- No student performance data source exists.
- No risk/intervention contracts exist.
- Retention data in Scorecard is institution-level, not student success logic.

### College Comparison Module Risks

- Current comparison endpoint is not an orchestrator module.
- Program/outcome/cost comparison is not contractually defined.
- External Scorecard data may be partial or nullable.

## July 4 Beta Readiness

### Ready For Beta

Features that can realistically ship with current backend behavior:
- User registration and login.
- Disabled email verification compatibility.
- University/program/course discovery using current live catalog data: 6 universities, 363 programs, and 6157 courses.
- Course prerequisite/corequisite lookup using current live relationship data: 1169 prerequisite rows and 611 corequisite rows.
- University comparison at a basic level, limited by available institution fields.
- Academic terms, offerings, sections, and meetings lookup for demo scheduling data only: 2 terms, 8 offerings, 10 sections, and 18 meetings.
- Normalized education plan CRUD, with the caveat that live normalized usage currently has only 1 plan.
- Plan-course add/update/remove, with the caveat that live normalized usage currently has only 1 plan course.
- Planning validation report against real catalog prerequisite/corequisite data.
- Graduation audit report with clear limitation that planned courses are treated as completed.
- Legacy education-plan compatibility routes.
- Intake submission persistence.
- Advisor notification handoff.
- Orchestrator infrastructure demo with `ExampleModule` if dependencies are installed.

### Partial

Features requiring additional work before beta-quality use:
- Academic Planning through orchestrator.
- OpenRouter integration beyond stubbed provider behavior.
- Schedule conflict detection, especially because `plan_sections` and `plan_schedules` are empty.
- Normalized plan section/schedule persistence.
- Career guidance from database mappings; career tables have data but only 10 careers and 20 total mapping rows.
- College comparison beyond basic university/program comparison; cost and outcome tables are missing.
- Agentic memory and run tracking in a deployed flow; all `agentic` tables are currently empty.
- Global country/state lookup APIs; `countries` and `states` are currently empty.

### Not Ready

Blocked by missing APIs, services, data, or requirements:
- Schedule generation.
- Career guidance module.
- Internship/job search.
- Finance guidance.
- Scholarship search.
- Tuition/cost estimation.
- Academic Success/risk detection.
- Student interventions.
- Transcript-aware graduation readiness.
- Production natural-language agent behavior using live LLM calls.

## Recommendations

### Work Remaining Before July 2

- Install/sync backend dependencies so tests can run, especially `langgraph`.
- Add an official `Academic Planning` orchestrator module that wraps existing planning tools/services.
- Add an API entrypoint for orchestrated student queries if beta requires agent interaction.
- Decide whether beta audit language should say “plan completion” instead of “graduation readiness” until transcript data exists.
- Add minimum conflict detection over selected sections if scheduling is in beta scope.
- Add SQLAlchemy models for `plan_sections` and `plan_schedules` if those tables will be used before beta.
- Document which modules are intentionally disabled for beta so routing does not promise unavailable functionality.

### Work Remaining Before July 4

- Run and fix the focused orchestrator/planning/scheduling test suites in a clean environment.
- Register production-ready modules only; leave missing modules unregistered with clear fallback messaging.
- Harden Planning API responses and validation behavior for the beta path.
- Seed or verify catalog data needed by the demo/beta schools, programs, courses, terms, sections, and meetings.
- Add a basic College Comparison service contract if comparison is part of the beta demo.
- Confirm OpenRouter strategy: keep stubbed responses out of production agent flows or implement live API calls safely.

### Post-Beta Work

- Build true Scheduling: availability constraints, conflict detection, section selection, schedule generation, scoring, and persistence.
- Build Career domain over `careers`, `program_careers`, and `course_careers`, then add internships/jobs/outcomes data sources.
- Build Finance domain: tuition, aid, scholarships, loans, and cost estimation.
- Build Academic Success domain: grades/GPA, attendance, risk, interventions, retention, and success metrics.
- Refactor Catalog ownership so Discovery and Scheduling consume a shared catalog boundary.
- Reconcile legacy and normalized planning context loading.
- Implement transcript, transfer credit, substitutions, waivers, minimum grade rules, advisor overrides, and persisted audit history.
- Replace OpenRouter stub with production provider calls, API key handling, retries, rate limits, structured output validation, and observability.
