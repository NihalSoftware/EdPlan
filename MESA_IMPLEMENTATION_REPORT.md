# Mesa AI implementation report

Mesa is the student-facing assistant at /mesa. Bookmarks under /edplan-nexus redirect to Mesa. The old Nexus chat API returns HTTP 410 and directs callers to the new workspace. College comparison, career exploration, onboarding, financial aid, Education Planner, Saved Plans, Schedule Generator, and What-If Analysis retain their own entry points.

## What is implemented

- Answer-first conversation with context-aware question chips, program and plan choices, typed replies, citations, readable tables, an editable preferences panel, and keyboard-friendly controls.
- Optional sign-in. Guest and non-retained sessions expire after 24 hours. Signed-in users may opt in to 30 days of history, revoke retention, or delete a conversation. The cleanup command physically purges expired data. Scenario records share their conversation's retention window.
- Server-issued choices, stale-choice rejection, idempotent turn and confirmation requests, conversation ownership, and server-side ownership checks for normalized plans and graduation audits.
- Existing catalog, institution comparisons, College Scorecard, recorded course requirements, course sequence preview, plan validation, graduation audit, and the public program handoff to Education Planner.
- Deterministic credit-load lower bounds and GPA projections. What-If assumptions remain separate from stated preferences. Signed-in users can preview and explicitly confirm saving a scenario.
- Anonymous daily counts by intent and outcome. Optional model routing is disabled by default. When enabled, it can classify unfamiliar public discovery questions using a limited set of taxonomy keywords. Raw prompts, tokens, private plans, and transcripts stay outside that request.

## Intent coverage

| Spec intents | Implemented behavior and remaining data needs |
| --- | --- |
| M01–M03 | Orientation, conversation profile, and catalog-backed career exploration |
| M04–M06 | New Mexico college and credential search, program detail, and career and program exploration |
| M07–M08 | Published institutional sources and available catalog information; official admissions, accessibility policies, services, and current deadlines require institutional confirmation |
| M09–M11 | Institution comparison, degree and budget filters, and published tuition; personalized fees, international rates, online delivery, and drive-time verification depend on additional data |
| M12–M15 | Financial aid workflow and sources, career mapping and published institution outcomes, and official campus resources; awards, occupation-specific earnings, and personal cost or commute estimates are limited by available data |
| M16–M18 | Preview catalog sequencing and recorded prerequisites, open the chosen program in Education Planner, or continue in Schedule Generator to work with available sections |
| M19–M20 | Transfer and prior-credit guidance and official resources; a formal equivalency evaluation requires institutional records |
| M21–M22 | Authenticated saved-plan preview, rule validation, and graduation audit; advisor preparation uses the existing saved-plan PDF. Sending requires verified advisor identity and a safe delivery integration |
| M23–M25 | Employer, vicinity, and vacancy intents resolve to a clear data limitation and a state job portal. Verified workplaces, drive times, internships, and openings need feeds |
| M26 | Existing program-to-career mappings and related guidance |
| M27, M31, M34 | Credit-load lower bounds and GPA projections, with explicit confirmation for saving. A verified term-by-term optimizer requires course-offering, substitution, and fee data |
| M28–M30, M32–M33 | Scoped What-If guidance and separate assumptions. Retake policies, major changes, travel/work constraints, tuition and aid effects, and lifetime earnings need verified inputs |
| M35–M38 | Key definitions, correction and reset, ambiguity handling, and sensitive-request escalation |

## Local setup and verification

For a database using the migration chain in this checkout, apply the Alembic head migration before opening Mesa. Revision 0011 adds the session, scenario, and aggregate metrics tables and backfills missing nullable catalog columns where needed. Downgrade removes the Mesa tables and preserves the catalog columns and data.

From fastapi_backend, run the normal migrations and FastAPI startup. From ChatbotUI, start the existing Vite development server. The project defaults use ports 8000 and 5173. For a separately hosted local API, set VITE_API_BASE_URL to the API origin with its /api suffix. Run the cleanup task with the same database configuration at a regular interval in the target environment.

    python -m alembic upgrade head
    python -m uvicorn app.main:app --reload
    python -m app.mesa.purge

The Mesa tests replay all 190 authored utterances, exercise separate rule examples, and run the 15-turn nursing walkthrough and nine extended examples. PostgreSQL integration tests require MESA_TEST_DISPOSABLE_DB=1 and a migrated disposable database. They use synthetic catalog and Scorecard fixtures. The 190 authored utterances are registered examples, so their routing score measures supported examples and does not estimate unfamiliar-question accuracy. The integration tests also cover access control, consent, expiry, idempotency, and confirmed scenario saving.

The initial rollout used a disposable local database.

The backend regression run reproduced the same 16 failures on the clean MESA baseline. Those tests cover the pre-existing orchestrator, comparison route introspection, and SchedulePilot. The updated run added 209 passing Mesa checks. Frontend lint and the production build passed.

Desktop and mobile Edge smoke tests passed using the isolated preview. They exercised the legacy redirect, guest questions and follow-ups, a multi-turn credit-load scenario, preference review, the collapsible sidebar, and entry to six standalone routes.

## Databases managed by a different revision chain

The configured development database uses Alembic revision 0014 from a separate migration chain and already has the catalog fields Mesa uses. Missing Mesa tables caused conversation creation to return HTTP 500. The career lookup now reads the career_description catalog field and supports the description alias. Running the Mesa schema installer created only the three Mesa tables and preserved the existing Alembic revision.

For another authorized PostgreSQL database with the same prerequisite EdPlan catalog and users schema, run this from fastapi_backend with the intended database configuration:

    python -m app.mesa.install_schema

The installer checks whether its tables already exist, so it can be rerun. It uses the Mesa models to create the tables and does not stamp Alembic revisions.