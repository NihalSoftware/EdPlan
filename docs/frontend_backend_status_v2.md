`# Frontend ↔ Backend Integration Status V2

Audit date: 2026-06-29

Scope: latest `ChatbotUI` React/Vite frontend and `fastapi_backend` FastAPI backend. This is an audit-only report. No application code was modified.

## Executive Summary

The frontend is still partially integrated with the current FastAPI backend. The newest frontend commit added an EdPlan Nexus chat/workspace surface and a shared authenticated API client, but most Student beta workflows still use legacy endpoints, static data, localStorage, or frontend-only logic.

Current runtime status:

- Frontend loads through Vite at `http://127.0.0.1:5173/`.
- FastAPI responds at `http://127.0.0.1:8000/` when started with `DEBUG=true`.
- Vite proxies `/api` to `http://localhost:8000`.
- Discovery/catalog APIs used by Find University, College Detail, university compare, programs, courses, terms, normalized plans, validation, and graduation audit respond successfully.
- Normal backend startup is still blocked by invalid configuration: `DEBUG=release` is interpreted as a non-boolean value.
- The completed comparison module exists in backend source but is not mounted in `app/student/api/router.py`; `/api/comparison/*` returns `404`.
- New frontend Nexus chat calls `/api/nexus/chat`, but no matching backend route is mounted; the endpoint returns `404`.
- Frontend scheduling still calls old generated-schedule URLs, while backend now exposes `/api/schedulepilot/*`; frontend scheduling is disconnected. The new SchedulePilot list route also returned a runtime `500` in this environment.
- Planning UI is not wired to normalized plan CRUD/course/validation/audit APIs.

## 1. Frontend Changes Since Previous Audit

### New pages and routes

Defined in `ChatbotUI/src/App.jsx`:

| Route | Page | Status |
| --- | --- | --- |
| `/edplan-nexus` | `EdPlanNexusPage.jsx` | New shell page for Nexus |
| `/edplan-nexus/workspace` | `EdPlanNexusWorkspacePage.jsx` | New Nexus workspace/chat page |

Existing routes remain:

| Route | Page |
| --- | --- |
| `/home` | `HomePage.jsx` |
| `/intake` | `IntakeForm.jsx` |
| `/chatbot` | `ChatbotPage.jsx` |
| `/educationplan` | `EducationPlanEditPage.jsx` |
| `/career` | `CareerProgramPage.jsx` |
| `/schedule-generator` | `ScheduleGenerator.jsx` |
| `/view` | `ViewEducationPlanPage.jsx` |
| `/uni` | `FindUniversityPage.jsx` |
| `/compare` | `CollegeComparePage.jsx` |
| `/college/:unitId` | `CollegeDetailPage.jsx` |
| `/login` | `LoginPage.jsx` |
| `/signup` | `SignupPage.jsx` |

### New components, hooks, services, and types

| File | Purpose | Integration Status |
| --- | --- | --- |
| `components/chat/NexusChat.jsx` | New Nexus chat UI | UI exists, backend endpoint missing |
| `hooks/useNexusChat.js` | Nexus chat state and request flow | Calls missing `/api/nexus/chat` |
| `services/nexusService.js` | Nexus API wrapper | Broken: endpoint returns `404` |
| `services/apiClient.js` | Shared axios client with auth token interceptor | New and useful; not adopted by all services |
| `types/nexusChatTypes.js` | Nexus message helpers/types | UI-only |

### Modified API layer

- `authService.js` now uses the shared `apiClient`.
- `apiClient.js` injects `Authorization: Bearer <AuthToken>` from localStorage.
- `apiBaseUrl.js` still resolves `VITE_API_BASE_URL`, falling back to `http://localhost:8000/api` during Vite dev and `${origin}/api` in production.

### Removed components/services

No removed frontend components or services were identified in the current source tree. Legacy services are still present.

### Updated navigation

`Navigation.jsx` now includes an `EdPlan Nexus` navigation item with a `NEW` badge. The older chatbot page still exists at `/chatbot`, but it is no longer the primary navigation chat entry.

## 2. Backend Connectivity

### Frontend configuration

| Item | Current Value | Status |
| --- | --- | --- |
| Vite proxy | `/api` -> `http://localhost:8000` | Correct for local FastAPI |
| API base URL | `VITE_API_BASE_URL` or dev fallback `http://localhost:8000/api` | Correct |
| Auth token source | localStorage `AuthToken` | Present |
| Shared client | `services/apiClient.js` | Present |
| Auth header | `Authorization: Bearer <token>` | Present in shared client |

Remaining issues:

- `catalogService.js`, `universityService.js`, `scheduleService.js`, and some older service code still create their own axios clients instead of using `apiClient`.
- Normal backend startup failed unless `DEBUG=true` was supplied at process startup.
- The frontend now points Nexus chat at `/api/nexus/chat`, but backend does not expose that route.
- The frontend still points scheduling at legacy generated-schedule URLs instead of `/api/schedulepilot`.

### Backend router status

`fastapi_backend/app/student/api/router.py` imports the comparison API module but does not mount it:

```text
from app.student.domains.comparison.api import comparison
```

There is no active:

```text
router.include_router(comparison.router, prefix="/api")
```

Result: `/api/comparison/universities/search`, `/api/comparison/universities/compare`, `/api/comparison/programs/search`, `/api/comparison/programs/compare`, and `/api/comparison/careers/compare` all return `404`.

## 3. Student Module Coverage

### Academic Planning

| Capability | Backend | Frontend | Integration |
| --- | --- | --- | --- |
| Create Plan | `POST /api/plans` exists | Uses legacy `/api/users/education-plan` and local state | Partial |
| Update Plan | `PATCH /api/plans/{plan_id}` exists | Edit flow rehydrates local/legacy payloads | Partial |
| Delete Plan | `DELETE /api/plans/{plan_id}` exists | Uses legacy delete/localStorage fallback | Partial |
| View Plans | `GET /api/plans` exists and works | View page uses legacy list + `LocalSavedPlans` | Partial |
| Add Course | `POST /api/plans/{plan_id}/courses` exists | Component state only | Missing integration |
| Remove Course | `DELETE /api/plans/{plan_id}/courses/{course_id}` exists | Component state only | Missing integration |
| Move Course | `PATCH /api/plans/{plan_id}/courses/{course_id}` exists | Local term assignment only | Missing integration |
| Validate Plan | `POST /api/plans/{plan_id}/validate` exists and works | Duplicate client validation in editor | Missing integration |
| Graduation Audit | `GET /api/plans/{plan_id}/audit` exists and works | No UI/API usage found | Missing integration |
| Advisor | Backend has advisor/email route only; no `/nexus/chat` | Nexus UI exists | Broken |

Runtime planning probes:

| Probe | Result |
| --- | --- |
| `GET /api/plans` | `200 OK`, returned one test plan |
| `GET /api/plans/{plan_id}/courses` | `200 OK`, returned planned course data |
| `POST /api/plans/{plan_id}/validate` | `200 OK`, returned a corequisite validation issue |
| `GET /api/plans/{plan_id}/audit` | `200 OK`, returned graduation audit data |

Academic Planning backend is substantially present, but the frontend still operates mostly through the older plan model.

### College Comparison

| Capability | Backend | Frontend | Integration |
| --- | --- | --- | --- |
| Search Universities | Discovery `GET /api/universities` works; comparison search route source exists but is unmounted | Uses discovery search | Partial |
| Compare Universities | Discovery `POST /api/universities/compare` works; comparison compare route source exists but is unmounted | Uses discovery compare | Partial |
| Search Programs | `GET /api/programs` works; comparison program search source exists but is unmounted | Career/planning catalog uses programs; comparison UI does not use comparison search | Partial |
| Compare Programs | Source exists under `/api/comparison/programs/compare`, but route is unmounted | No frontend integration found | Missing/Broken |
| Compare Career Paths | Source exists under `/api/comparison/careers/compare`, but route is unmounted | No frontend integration found | Missing/Broken |

Runtime comparison probes:

| Probe | Result |
| --- | --- |
| `GET /api/universities?state=New Mexico&per_page=3` | `200 OK` |
| `POST /api/universities/compare` with `{ unit_ids: [...] }` | `200 OK` |
| `GET /api/programs?search=Accounting` | `200 OK` |
| `POST /api/comparison/universities/compare` | `404 Not Found` |
| `POST /api/comparison/programs/search` | `404 Not Found` |

Important data integrity issue:

- `CollegeCompare.jsx` and `CollegeDetail.jsx` still synthesize fallback metrics when backend fields are absent. This conflicts with the requirement to display only backend-provided data.

### Scheduling

| Capability | Backend | Frontend | Integration |
| --- | --- | --- | --- |
| Terms | `GET /api/terms` exists and works | Mostly unused by schedule UI | Partial |
| Schedule generation | `POST /api/schedulepilot/generate` exists | Frontend does not call it | Missing |
| Schedule session flow | `/api/schedulepilot/session/*` exists | No integration found | Missing |
| Saved schedules | `/api/schedulepilot/plans/{plan_id}/schedules` exists | Frontend calls old `/api/plans/{plan_id}/generated-schedules` | Broken |
| Activate schedule | `/api/schedulepilot/schedules/{schedule_id}/activate` exists | Frontend calls old generated-schedule activate URL | Broken |

Runtime scheduling probes:

| Probe | Result |
| --- | --- |
| `GET /api/terms` | `200 OK` |
| `GET /api/plans/{plan_id}/generated-schedules` | `404 Not Found` |
| `GET /api/schedulepilot/plans/{plan_id}/schedules?user_id=1` | `500 Internal Server Error` |

SchedulePilot runtime error observed:

```text
AttributeError: module 'sniffio' has no attribute 'current_async_library'
AttributeError: module 'sniffio' has no attribute 'AsyncLibraryNotFoundError'
```

This appears during FastAPI dependency resolution/threadpool execution in the current environment.

## 4. Legacy Usage

| File | Legacy Item | Reason | Recommended Replacement |
| --- | --- | --- | --- |
| `services/authService.js` | `/users/education-plan`, `/users/education-plan/list`, `/users/education-plan/delete` | Legacy plan persistence model | Use normalized `/plans` CRUD APIs |
| `components/education/EducationPlanEditor.jsx` | `LocalSavedPlans` and local plan assembly | Local persistence diverges from normalized backend | Persist plan and courses through `/plans` and `/plans/{id}/courses` |
| `components/education/EducationPlanEditor.jsx` | `validatePlan` client-side prerequisite/corequisite checks | Duplicates backend validation logic | Use `/plans/{plan_id}/validate` and `/validate-course` |
| `components/education/ViewEducationPlan.jsx` | `LocalSavedPlans` fallback | Local state can disagree with backend | Use `/plans` list/detail/delete |
| `services/scheduleService.js` | `/plans/{plan_id}/generated-schedules` URLs | Backend now exposes `/schedulepilot` routes | Replace with `/schedulepilot/plans/{plan_id}/schedules`, `/schedulepilot/generate`, and activate/archive routes |
| `services/catalogService.js` | `GET /careers` | Backend returns `404` | Add backend route or remove call; use comparison career-path APIs once mounted |
| `pages/CareerProgramPage.jsx` | Static `/assets/career_program_data.json` and `/assets/career_employers.json` first | Static/mock-first behavior | Use backend program/career data; show unavailable fields as unavailable |
| `components/university/CollegeCompare.jsx` | Synthesized metrics | Fabricates rankings/statistics | Display only API fields or explicit unavailable states |
| `components/university/CollegeDetail.jsx` | Synthesized metrics | Fabricates rankings/statistics | Display only API fields or explicit unavailable states |
| `services/universityService.js` | Separate axios client | Duplicate request setup | Consider shared `apiClient` for consistent auth/errors |
| `services/catalogService.js` | Separate axios client | Duplicate request setup | Consider shared `apiClient` |
| `services/nexusService.js` | `/nexus/chat` endpoint assumption | Backend route missing | Mount/implement backend Nexus route or update wrapper to actual advisor/orchestrator route |
| `components/chatbot/Chatbot.jsx` and `services/nlpService.js` | Local NLP assistant behavior | Not the Academic Planning Advisor/Qwen flow | Connect existing UI to backend advisor only if intended; otherwise mark as legacy |

## 5. API Matrix

| Frontend Feature | Backend Endpoint | Status | Notes |
| --- | --- | --- | --- |
| Login | `POST /api/users/login` | Connected | Uses `apiClient` |
| Signup | `POST /api/users` | Connected | Uses `apiClient` |
| Intake submit | `POST /api/intake` | Connected | Existing route retained |
| Find universities | `GET /api/universities` | Connected | Runtime `200 OK` |
| College detail | `GET /api/universities/{unit_id}` | Connected | Discovery API |
| University compare page | `POST /api/universities/compare` | Connected/Partial | Runtime `200 OK`; not the comparison module |
| Comparison module: university search | `POST /api/comparison/universities/search` | Broken | Route source exists but is not mounted |
| Comparison module: university compare | `POST /api/comparison/universities/compare` | Broken | Runtime `404` |
| Program catalog | `GET /api/programs` | Connected | Runtime `200 OK` |
| Program courses | `GET /api/programs/{program_id}/courses` | Connected | Used by education planner/catalog |
| Comparison module: program search | `POST /api/comparison/programs/search` | Broken | Runtime `404` |
| Comparison module: program compare | `POST /api/comparison/programs/compare` | Broken/Missing frontend | Route source exists but is unmounted |
| Comparison module: career compare | `POST /api/comparison/careers/compare` | Broken/Missing frontend | Route source exists but is unmounted |
| Career data | `GET /api/careers` | Broken | Runtime `404`; static assets used first |
| Legacy save plan | `POST /api/users/education-plan` | Partial | Connected to legacy API, not normalized planning |
| Legacy list plans | `POST /api/users/education-plan/list` | Partial | Runtime `200 OK`, empty for audit user |
| Legacy delete plan | `POST /api/users/education-plan/delete` | Partial | Legacy API |
| Normalized view plans | `GET /api/plans` | Backend connected, frontend missing | Runtime `200 OK` |
| Normalized create plan | `POST /api/plans` | Backend exists, frontend missing | Not used by current planning UI |
| Normalized update plan | `PATCH /api/plans/{plan_id}` | Backend exists, frontend missing | Not used by current planning UI |
| Normalized delete plan | `DELETE /api/plans/{plan_id}` | Backend exists, frontend missing | Not used by current planning UI |
| Plan courses list | `GET /api/plans/{plan_id}/courses` | Backend connected, frontend missing | Runtime `200 OK` |
| Add plan course | `POST /api/plans/{plan_id}/courses` | Backend exists, frontend missing | Needed by planner UI |
| Move/update plan course | `PATCH /api/plans/{plan_id}/courses/{course_id}` | Backend exists, frontend missing | Needed by planner UI |
| Remove plan course | `DELETE /api/plans/{plan_id}/courses/{course_id}` | Backend exists, frontend missing | Needed by planner UI |
| Validate plan | `POST /api/plans/{plan_id}/validate` | Backend connected, frontend missing | Runtime `200 OK`; frontend duplicates logic |
| Graduation audit | `GET /api/plans/{plan_id}/audit` | Backend connected, frontend missing | Runtime `200 OK` |
| Terms | `GET /api/terms` | Connected backend, mostly unused | Runtime `200 OK` |
| Schedule generated list | `GET /api/plans/{plan_id}/generated-schedules` | Broken | Runtime `404`; old URL |
| SchedulePilot list | `GET /api/schedulepilot/plans/{plan_id}/schedules` | Backend route mounted but runtime broken | Runtime `500` in current env |
| SchedulePilot generate | `POST /api/schedulepilot/generate` | Backend exists, frontend missing | Not used by schedule UI |
| SchedulePilot activate | `POST /api/schedulepilot/schedules/{schedule_id}/activate` | Backend exists, frontend missing | Frontend calls old URL |
| Nexus chat | `POST /api/nexus/chat` | Broken | Runtime `404`; UI exists |
| Legacy chatbot | Local NLP + discovery APIs | Partial | Not Academic Planning Advisor/Qwen |
| Advisor email | `POST /api/users/email-advisor` | Exists | Not the requested Academic Planning Advisor chat flow |

## 6. Runtime Verification

### Servers

Backend normal startup:

```text
venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Failed with:

```text
ValidationError: DEBUG input should be a valid boolean; input_value='release'
```

Backend audit startup:

```text
DEBUG=true venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend startup:

```text
npm run dev -- --host 127.0.0.1 --port 5173
```

### HTTP checks

| Check | Result |
| --- | --- |
| `GET http://127.0.0.1:8000/` | `200 OK` |
| `GET http://127.0.0.1:5173/` | `200 OK` |
| `GET http://127.0.0.1:5173/edplan-nexus` | `200 OK` app shell |
| `GET http://127.0.0.1:5173/edplan-nexus/workspace` | `200 OK` app shell |
| `GET /api/plans` via Vite | `200 OK` |
| `GET /api/plans/{plan_id}/courses` via Vite | `200 OK` |
| `POST /api/plans/{plan_id}/validate` via Vite | `200 OK` |
| `GET /api/plans/{plan_id}/audit` via Vite | `200 OK` |
| `GET /api/universities?state=New Mexico&per_page=3` via Vite | `200 OK` |
| `POST /api/universities/compare` via Vite | `200 OK` |
| `GET /api/programs?search=Accounting` via Vite | `200 OK` |
| `GET /api/terms` via Vite | `200 OK` |
| `POST /api/users/education-plan/list` via Vite | `200 OK` |
| `GET /api/careers` via Vite | `404 Not Found` |
| `GET /api/plans/{plan_id}/generated-schedules` via Vite | `404 Not Found` |
| `GET /api/schedulepilot/plans/{plan_id}/schedules?user_id=1` via Vite | `500 Internal Server Error` |
| `POST /api/comparison/universities/compare` via Vite | `404 Not Found` |
| `POST /api/comparison/programs/search` via Vite | `404 Not Found` |
| `POST /api/nexus/chat` via Vite | `404 Not Found` |

### Console and Network audit

Browser Console and Network Tab inspection could not be completed because the available environment did not have a working browser automation command on PATH. The previous `agent-browser` command was unavailable. HTTP-level probes through Vite and FastAPI were used instead.

Known runtime failures from HTTP/server output:

- Backend startup config error: invalid boolean `DEBUG=release`.
- `/api/comparison/*` returns `404` because the comparison router is not mounted.
- `/api/nexus/chat` returns `404` because no backend route is mounted.
- `/api/plans/{plan_id}/generated-schedules` returns `404` because frontend scheduling uses obsolete URLs.
- `/api/schedulepilot/plans/{plan_id}/schedules` returns `500` due the `sniffio`/`anyio` runtime error above.
- `/api/careers` returns `404`.

## Remaining Beta Integration Work

### High Priority

| Work Item | Blocking Issue | Estimated Effort |
| --- | --- | --- |
| Mount or restore comparison router | `/api/comparison/*` routes return `404`; completed comparison module is unavailable over HTTP | Small |
| Align Nexus advisor frontend with backend | New Nexus UI calls `/api/nexus/chat`, which does not exist | Medium |
| Integrate normalized planning APIs into planner UI | Planner still uses legacy/local plan model; validation/audit unused | Large |
| Replace scheduling frontend endpoints with SchedulePilot endpoints | Current schedule UI calls obsolete 404 URLs | Medium |
| Fix SchedulePilot runtime error | Mounted SchedulePilot route returns `500` in current environment | Medium |
| Fix backend startup configuration | Normal backend startup fails with `DEBUG=release` | Small |

### Medium Priority

| Work Item | Blocking Issue | Estimated Effort |
| --- | --- | --- |
| Remove synthesized university metrics | Comparison/detail pages fabricate fallback data | Small/Medium |
| Replace static career JSON-first behavior | Career page still prefers mock/static assets | Medium |
| Consolidate frontend API clients | Multiple axios clients bypass shared auth/error behavior | Small |
| Add graduation audit display path | Backend audit works but no frontend usage found | Medium |
| Add backend validation display path | Backend validation works but editor uses duplicate client validation | Medium |
| Expose or remove `/api/careers` usage | Frontend calls an endpoint that returns `404` | Small/Medium |

### Low Priority

| Work Item | Blocking Issue | Estimated Effort |
| --- | --- | --- |
| Clarify old Chatbot vs Nexus ownership | Both chat experiences exist; only Nexus attempts backend orchestration | Small |
| Add browser-level E2E regression checks | Console/network inspection is not automated in this environment | Medium |
| Tighten loading/error/empty states after API swap | Some pages have local fallbacks that can mask backend issues | Medium |
| Remove dead static schedule/program assets if confirmed unused | Static assets remain in `public/assets` | Small |

## Beta Readiness

| Module | Backend | Frontend | Integration | Score |
| --- | --- | --- | --- | --- |
| Academic Planning | Strong normalized APIs for plans/courses/validation/audit | Planner UI still legacy/local | Partial | 45% |
| College Comparison | Discovery works; comparison source exists but unmounted | University discovery compare works; program/career compare missing | Partial/Broken | 35% |
| Scheduling | SchedulePilot routes exist, but one probed route returns `500` | UI uses obsolete generated-schedule endpoints | Broken | 25% |
| Student Frontend | Loads and has new Nexus pages | Still contains legacy persistence, mocks, duplicate validation | Partial | 50% |
| Student Backend | Many Student APIs are implemented | Startup config, unmounted comparison router, missing Nexus route, SchedulePilot runtime error | Partial | 65% |
| Overall Student Platform | Core pieces exist | Final beta flows are not yet connected end-to-end | Partial | 40% |

## Bottom Line

The latest codebase is closer to a full Student beta because normalized planning, graduation audit, discovery, and SchedulePilot backend surfaces exist, and the frontend now has a Nexus UI plus a shared API client. However, the main beta blockers are integration alignment rather than UI polish: planning is not wired to normalized APIs, comparison module routes are not mounted, scheduling frontend/backend URLs diverge, Nexus chat points at a missing route, and the backend still needs a clean startup configuration.
