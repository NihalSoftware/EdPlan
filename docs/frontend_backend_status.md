# Frontend ↔ Backend Integration Status

Audit date: 2026-06-29

Scope: `ChatbotUI` React/Vite frontend and `fastapi_backend` FastAPI backend. This is an audit only; no application code was changed.

## Executive Summary

The frontend is partially connected to the current FastAPI backend.

- Frontend shell loads from Vite at `http://127.0.0.1:5173/`.
- Backend root responds at `http://127.0.0.1:8000/`.
- Vite proxies `/api` to `http://localhost:8000`.
- Discovery/catalog endpoints used by Find University and Education Plan catalog loading are connected.
- Legacy saved-plan endpoints under `/api/users/education-plan...` are connected, but the main planning UI does not use the newer normalized `/api/plans` CRUD/course/validation/audit APIs.
- College comparison UI uses legacy discovery endpoints, not the completed `/api/comparison/...` module.
- Program comparison and career comparison backend endpoints exist but are unused by the frontend and currently fail at runtime against the configured database because the code queries `careers.description`, a column missing from the live DB.
- Schedule Generator calls frontend service endpoints that are not exposed by the backend: `/api/plans/{plan_id}/generated-schedules`.
- Career Program page prefers static JSON assets and only falls back to backend data if static files fail.
- Advisor chat UI exists but is not connected to Academic Planning Advisor/Qwen/tool-call flow.

## Runtime Setup Findings

Backend startup initially failed using the checked-in `.env`:

```text
ValidationError: DEBUG input should be a valid boolean; input_value='release'
```

For audit probes only, FastAPI was started with a process override:

```text
DEBUG=true venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend started successfully:

```text
npm run dev -- --host 127.0.0.1 --port 5173
```

Browser console/network inspection could not be completed because `agent-browser` is not installed on PATH and no equivalent browser automation tool was available. HTTP-level probes were completed against Vite and FastAPI.

## Frontend Structure Audit

### Routes

Defined in `ChatbotUI/src/App.jsx`:

| Route | Page | Status |
| --- | --- | --- |
| `/home` | `HomePage` | Static/home, no backend calls |
| `/intake` | `IntakeForm` | Connected to `/api/intake` |
| `/chatbot` | `ChatbotPage` | Local NLP + university APIs; not advisor/Qwen |
| `/educationplan` | `EducationPlanEditPage` | Catalog-connected; plan operations mostly local/legacy |
| `/career` | `CareerProgramPage` | Static JSON first; backend fallback |
| `/schedule-generator` | `ScheduleGenerator` | Calls missing generated-schedule endpoints |
| `/view` | `ViewEducationPlanPage` | Legacy saved-plan API + local storage |
| `/uni` | `FindUniversityPage` | Connected to discovery/catalog APIs |
| `/compare` | `CollegeComparePage` | Connected to discovery compare API; fabricates some fallback metrics |
| `/college/:unitId` | `CollegeDetailPage` | Connected to discovery compare/detail APIs |
| `/login` | `LoginPage` | Connected to FastAPI auth |
| `/signup` | `SignupPage` | Connected to FastAPI auth |

### Components

- Layout: `components/layout/AppLayout.jsx`, `Navigation.jsx`
- Education: `EducationPlanEditor.jsx`, `ViewEducationPlan.jsx`
- University: `FindUniversity.jsx`, `CollegeCompare.jsx`, `CollegeDetail.jsx`
- Scheduling: `GeneratedSchedulesList.jsx`, `ScheduleCard.jsx`, `WeeklyCalendar.jsx`
- Chatbot: `Chatbot.jsx`

### API Layer

- `apiBaseUrl.js`: `VITE_API_BASE_URL` or dev fallback `http://localhost:8000/api`; production fallback `${origin}/api`.
- `authService.js`: shared axios client with bearer token interceptor; auth and legacy education-plan endpoints.
- `universityService.js`: discovery university search/detail/compare endpoints.
- `catalogService.js`: programs/courses/universities and a missing `/careers` call.
- `educationPlanService.js`: transforms program/course catalog responses for the UI; not normalized plan CRUD.
- `scheduleService.js`: generated-schedule endpoints that are missing in backend routing.
- `chatbotService.js`: local query handling backed by university search/compare only.
- `nlpService.js`: client-side `compromise` parsing.

### State Management

No central store. State is managed with React component state plus `localStorage` through `utils/storage.js`.

Important localStorage keys:

- `AuthToken`, `UserEmail`, `UserProfile`
- `University`, `UniversityUnitId`, `UniversityState`
- `Programname`, `Programnameview`, `ProgramDegree`, `SelectedProgram`, `SelectedDegreeLevel`
- `CompareQueue`, `LastCollegeDetail`
- `LocalSavedPlans`, `EditingPlan`, `EditingPlanActive`

## Backend Connection Audit

Configured backend:

- Frontend dev fallback: `http://localhost:8000/api`
- Vite proxy: `/api` -> `http://localhost:8000`
- Backend app mounts routers under `/api`.
- CORS includes local frontend origins.

Observed:

- `GET /` on FastAPI: `200 OK`
- `GET /openapi.json`: `200 OK`
- `GET /` on Vite: `200 OK`
- `GET /src/main.jsx` on Vite: `200 OK`
- `GET /uni` on Vite: `200 OK` and returns app shell

Connection caveat:

- Backend `.env` currently prevents normal startup because `DEBUG=release` is invalid for a boolean setting.

## API Usage Audit

| Frontend Function | Backend Endpoint | Status |
| --- | --- | --- |
| `login` | `POST /api/users/login` | Connected |
| `register` | `POST /api/users` | Connected |
| `addEducationPlan` | `POST /api/users/education-plan` | Partial: legacy endpoint, requires existing user, not normalized plan API |
| `getEducationPlanList` | `POST /api/users/education-plan/list` | Connected to legacy endpoint |
| `deleteEducationPlan` | `POST /api/users/education-plan/delete` | Connected to legacy endpoint |
| `searchUniversities` | `GET /api/universities` | Connected |
| `getUniversityById` | `GET /api/universities/{unit_id}` | Connected |
| `compareUniversitiesByIds` | `POST /api/universities/compare` | Connected |
| `getCatalogUniversities` | `GET /api/universities` | Connected |
| `getCatalogPrograms` | `GET /api/programs` | Connected |
| `getCatalogCourses` | `GET /api/programs/{program_id}/courses` | Connected |
| `getCareers` | `GET /api/careers` | Broken: backend returns 404 |
| `getGeneratedSchedules` | `GET /api/plans/{plan_id}/generated-schedules` | Broken: backend returns 404 |
| `getGeneratedSchedule` | `GET /api/plans/{plan_id}/generated-schedules/{schedule_id}` | Broken: no backend route found |
| `activateGeneratedSchedule` | `POST /api/plans/{plan_id}/generated-schedules/{schedule_id}/activate` | Broken: no backend route found |
| `IntakeForm` submit | `POST /api/intake` | Connected |
| `CareerProgramPage` static catalog | `/assets/career_program_data.json`, `/assets/career_employers.json` | Mock/static-first |
| `Chatbot` query | local NLP + discovery university APIs | Partial; not Academic Planning Advisor |

Backend APIs that exist but frontend does not use:

| Backend Endpoint | Frontend Status |
| --- | --- |
| `GET /api/plans` | Unused by planning UI |
| `POST /api/plans` | Unused |
| `GET /api/plans/{plan_id}` | Unused |
| `PATCH /api/plans/{plan_id}` | Unused |
| `DELETE /api/plans/{plan_id}` | Unused |
| `GET /api/plans/{plan_id}/courses` | Unused by planning UI |
| `POST /api/plans/{plan_id}/courses` | Unused |
| `PATCH /api/plans/{plan_id}/courses/{course_id}` | Unused; would support move/update |
| `DELETE /api/plans/{plan_id}/courses/{course_id}` | Unused |
| `POST /api/plans/{plan_id}/validate` | Unused by planning UI |
| `POST /api/plans/{plan_id}/validate-course` | Unused |
| `GET /api/plans/{plan_id}/audit` | Unused |
| `POST /api/comparison/universities/search` | Unused |
| `POST /api/comparison/universities/compare` | Unused by comparison UI |
| `POST /api/comparison/programs/search` | Unused |
| `POST /api/comparison/programs/compare` | Unused and currently runtime-broken |
| `POST /api/comparison/careers/compare` | Unused and currently runtime-broken |
| `GET /api/terms` and scheduling catalog endpoints | Mostly unused by frontend |

## Student Module Coverage

### Academic Planning

| Capability | Backend | Frontend | Integration |
| --- | --- | --- | --- |
| Plan CRUD | New `/api/plans` and legacy `/api/users/education-plan` exist | Uses legacy save/list/delete; no normalized plan CRUD UI | Partial |
| Create Plan | Exists | Save Plan posts legacy payload or localStorage | Partial |
| View Plans | Exists | View page uses legacy list + local storage | Partial |
| Update Plan | Exists via `PATCH /api/plans/{plan_id}` | Edit reloads local/legacy course payload then re-saves | Partial/disconnected from normalized update |
| Delete Plan | Exists | Uses legacy delete or localStorage delete | Partial |
| Add Course | Exists via normalized route | Component-only state update | Disconnected |
| Remove Course | Exists via normalized route | Component-only state update | Disconnected |
| Move Course | Possible via normalized course patch | No direct backend call; only local term assignment | Disconnected |
| Validation | Exists | Client-side prerequisite/corequisite/credit validation | Disconnected |
| Graduation Audit | Exists | No UI/API call found | Disconnected |

Observed backend probes:

- `GET /api/plans`: `200 OK`, returned one active test plan.
- `GET /api/plans/{plan_id}/courses`: `200 OK`.
- `POST /api/plans/{plan_id}/validate`: `200 OK`, returned a corequisite issue.
- `GET /api/plans/{plan_id}/audit`: `200 OK`, returned graduation audit data.

### College Comparison

| Capability | Backend | Frontend | Integration |
| --- | --- | --- | --- |
| Search Universities | `/api/comparison/universities/search` and `/api/universities` | Uses `GET /api/universities` | Partial; not comparison module |
| Compare Universities | `/api/comparison/universities/compare` and `/api/universities/compare` | Uses `POST /api/universities/compare` | Partial; not comparison module |
| Search Programs | `/api/comparison/programs/search` | Frontend program filtering uses `GET /api/programs`; comparison UI does not use program search | Partial/unused |
| Compare Programs | `/api/comparison/programs/compare` | No UI call found | Missing frontend; backend runtime issue |
| Compare Career Paths | `/api/comparison/careers/compare` | No UI call found | Missing frontend; backend runtime issue |

Observed backend probes:

- `POST /api/comparison/universities/compare`: `200 OK`.
- `POST /api/comparison/programs/search`: `200 OK`.
- `POST /api/comparison/programs/compare`: `500`, database mismatch: `column c.description does not exist`.
- `POST /api/comparison/careers/compare`: `500`, same database mismatch.

Important frontend issue:

- `CollegeCompare.jsx` synthesizes fallback values for metrics such as faculty count, research funding, campus visits, placement rate, rank, and international students when API fields are absent. This means the comparison UI does not strictly display only backend-provided data.

### Scheduling

| Capability | Backend | Frontend | Integration |
| --- | --- | --- | --- |
| Terms | `GET /api/terms` | Not generally wired into planner | Exists but mostly unused |
| Offerings/sections/meetings | `/api/courses/{id}/offerings`, `/api/offerings/{id}/sections`, `/api/sections/{id}/meetings` | No broad integration found | Exists but unused |
| Generated schedules | No mounted route found for frontend URLs | `ScheduleGenerator` calls `/api/plans/{plan_id}/generated-schedules` | Broken |
| Activate schedule | No mounted route found for frontend URL | Calls missing activate endpoint | Broken |

Observed:

- `GET /api/terms`: `200 OK`.
- `GET /api/plans/test-plan/generated-schedules`: `404 Not Found`.

## Mock Data and Hardcoded Data Audit

| Location | Type | Current Use | Backend Equivalent |
| --- | --- | --- | --- |
| `public/assets/career_program_data.json` | Static catalog/mock data | Career Program page loads this first | Partial: `/api/programs`; comparison career mapping exists, but `/api/careers` does not |
| `public/assets/career_employers.json` | Static employer data | Career Program page loads this first | No direct backend endpoint found |
| `public/assets/ScheduleNMSU.json` and related schedule JSON files | Static schedule data | Present in assets; no active import found in current source scan | Scheduling catalog endpoints exist; generated schedule endpoints missing |
| `public/assets/programdetail.json` | Static program detail data | Present in assets; no active import found in current source scan | `/api/programs`, `/api/programs/{id}/courses` |
| `EducationPlanEditor.jsx` | Client-side validation logic | Performs prerequisite/corequisite/credit checks locally | `/api/plans/{plan_id}/validate` and `/validate-course` |
| `ViewEducationPlan.jsx` | Local saved plans | Reads/writes `LocalSavedPlans` fallback | Legacy and normalized plan APIs exist |
| `FindUniversity.jsx` | Hardcoded allowed campuses | Limits display to 5 named campuses | Backend search can return more |
| `FindUniversity.jsx` | Hardcoded default state | `New Mexico` default | Backend supports state filter |
| `FindUniversity.jsx` | Hardcoded fallback crime rate | Defaults to `2.5` if missing | No equivalent confirmed |
| `CollegeCompare.jsx` | Synthesized fallback metrics | Fabricates missing values | Should be replaced by backend data or unavailable state |
| `Chatbot.jsx` | Default prompt strings and local NLP | Local assistant behavior | Academic Planning Advisor backend flow is not connected |

## End-to-End / Runtime Probe Results

HTTP-level checks completed:

| Check | Result |
| --- | --- |
| Vite frontend shell `/` | `200 OK` |
| Vite client route `/uni` | `200 OK` app shell |
| Vite module `/src/main.jsx` | `200 OK` |
| FastAPI root `/` | `200 OK` |
| FastAPI OpenAPI `/openapi.json` | `200 OK` |
| `GET /api/universities?state=New Mexico&per_page=2` via Vite | `200 OK`, live database source |
| `GET /api/programs` via Vite | `200 OK`, 363 programs |
| `POST /api/universities/compare` via Vite | `200 OK` |
| `POST /api/comparison/universities/compare` via Vite | `200 OK` |
| `POST /api/comparison/programs/search` via Vite | `200 OK` |
| `GET /api/plans` via Vite | `200 OK` |
| `GET /api/plans/{plan_id}/courses` via Vite | `200 OK` |
| `POST /api/plans/{plan_id}/validate` via Vite | `200 OK` |
| `GET /api/plans/{plan_id}/audit` via Vite | `200 OK` |
| `GET /api/careers` via Vite | `404 Not Found` |
| `GET /api/plans/{plan_id}/generated-schedules` via Vite | `404 Not Found` |
| `POST /api/comparison/programs/compare` via Vite | `500 Internal Server Error` |
| `POST /api/comparison/careers/compare` via Vite | `500 Internal Server Error` |

UI-through-browser checks:

- Not completed due missing browser automation tool in the environment.
- Console errors, React warnings, and browser Network tab failures could not be directly captured.
- HTTP probes indicate the requests from pages using discovery/catalog should reach the backend, while schedule generator and career fallback endpoints will fail.

## Console & Network Audit

Direct browser console/network inspection was blocked by tooling. Inferred network failures from source and HTTP probes:

| Page | Request | Expected Browser Network Status |
| --- | --- | --- |
| Career Program fallback path | `GET /api/careers` | `404` if static assets fail |
| Schedule Generator | `GET /api/plans/{plan_id}/generated-schedules` | `404` |
| Schedule Generator detail | `GET /api/plans/{plan_id}/generated-schedules/{schedule_id}` | `404` |
| Schedule Generator activate | `POST /api/plans/{plan_id}/generated-schedules/{schedule_id}/activate` | `404` |
| College comparison future program compare integration | `POST /api/comparison/programs/compare` | `500` until DB/backend mismatch is fixed |
| Career comparison future integration | `POST /api/comparison/careers/compare` | `500` until DB/backend mismatch is fixed |

Potential JavaScript/client issues from source:

- `LoginPage` navigates to `/eduai` after successful login, but `App.jsx` has no `/eduai` route; wildcard redirects to `/home`.
- External Chatling script is loaded in `index.html`, adding a third-party runtime dependency outside the app API layer.
- Comparison UI uses generated fallback metrics, so rendered values may not match backend-provided fields.

## Remaining Integration Work

| Frontend Page | Backend API | Estimated Effort | Blocking Issue |
| --- | --- | --- | --- |
| Education Plan editor | `/api/plans`, `/api/plans/{id}/courses`, `/validate`, `/audit` | Large | Needs data-shape mapping from current local course model to normalized plan/course IDs and terms |
| Saved Education Plans | `/api/plans` normalized list/detail/delete | Medium | Current UI expects legacy payload grouped by program/university/course arrays |
| Education Plan validation | `/api/plans/{id}/validate`, `/validate-course` | Medium | Current validation happens before backend plan/course persistence |
| Graduation audit display | `/api/plans/{id}/audit` | Medium | No existing UI section found |
| Course move/update | `PATCH /api/plans/{id}/courses/{course_id}` | Medium | UI has no persisted normalized `plan_course_id` model |
| College Compare page | `/api/comparison/universities/compare` | Small/Medium | Existing UI uses discovery compare and synthesized fallback metrics |
| Program comparison | `/api/comparison/programs/search`, `/compare` | Medium | No existing comparison UI for programs; backend compare currently 500s against live DB |
| Career path comparison | `/api/comparison/careers/compare` | Medium | No existing comparison UI; backend currently 500s against live DB |
| Career Program page | Backend program/career endpoints | Medium | Static JSON is primary source; `/api/careers` missing |
| Chatbot/advisor | Academic Planning Advisor/Qwen orchestrator endpoint | Medium/Large | Existing chat UI is local NLP; no mounted advisor chat endpoint found |
| Schedule Generator | Generated schedule persistence routes | Medium/Large | Frontend calls endpoints not mounted in FastAPI |
| Backend startup | `.env` / settings | Small | `DEBUG=release` prevents normal startup |

## Beta Readiness

| Module | Backend | Frontend | Integration |
| --- | --- | --- | --- |
| Academic Planning | Strong: normalized CRUD, courses, validation, audit are exposed and probed successfully | Existing planner UI present but uses local state + legacy endpoints | Partial, not Beta-ready on normalized backend |
| Scheduling | Catalog endpoints exist; generated schedule service code exists but routes are not mounted for frontend URLs | Schedule Generator page exists | Broken for generated schedules |
| College Comparison | Search/compare endpoints exist; university compare works; program/career compare fail with DB schema mismatch | University search/compare UI exists; program/career comparison UI missing | Partial |

## Key Mismatches

1. `.env` has invalid `DEBUG=release`, blocking normal backend startup.
2. Frontend planning uses legacy `/users/education-plan...` and local storage instead of normalized `/plans`.
3. Frontend validation duplicates backend validation logic.
4. Graduation audit backend exists but no frontend call/display exists.
5. College comparison frontend uses `/universities/compare`, not `/comparison/universities/compare`.
6. Program and career comparison backend endpoints exist but are not integrated and currently fail against the live DB.
7. Schedule Generator frontend endpoints are not mounted by the backend.
8. Career page uses static JSON as the primary data source.
9. Advisor chat UI exists but is not connected to Academic Planning Advisor/Qwen/tool calls.
10. Browser console/network audit remains unverified due missing browser automation tool.
