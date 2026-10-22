# NMT 2026-2027: extraction and staging, not publication

Status: **partial, limited database insertion completed; academic publication blocked**.
Work is on `codex/nmt-catalog-staging`. Following the user's explicit request to
insert the data, 32 source-backed NMT departments were inserted into the existing
`catalog_departments` table, and 73 programs plus one course were stored in
`catalog_change_audit` as **review-only proposals**, not published academic rows.
No DDL, migration, plan modification, automatic deactivation, or changes to existing
programs/courses/rules were executed. The pre-existing
`ChatbotUI/src/pages/IntakeForm.jsx` edit was preserved.

## Limited database insertion: 2026-10-15

Import run: `efe05d4b-e388-56a7-9e70-86fbdebf2ca9`.

| Target | Committed result |
| --- | --- |
| `catalog_departments` | 32 new NMT departments, matched by institution + exact official department ID |
| `catalog_change_audit` | 32 applied department-insertion audit rows, 73 program review proposals, 1 course review proposal |
| `catalog_import_runs` | One completed run, explicitly marked as incomplete academic publication |
| Existing NMT programs / courses | Still 159 / 693; not overwritten or republished |
| Protected catalog, relationship and saved-plan tables | All nine before/after checksums unchanged |
| Second run | Zero departments, proposals, or import runs added; no duplicates |

The academic review records have `action='review'`, no applied timestamp and no
legacy record ID assertion. Their full normalized/raw academic evidence, source,
catalog year and checksum are retained in `proposed_new_values`. They must not be
read as active programs/courses or used to create new student plans. Unknown
department active status remains NULL, and existing department values are never
overwritten. This operation does **not** make the full NMT catalog available in the UI.

The exact batch passed five integration checks against a newly initialized,
isolated local PostgreSQL 18 cluster: atomic insert/replay, rollback on a failed
batch, preservation of conflicting existing departments, wrong-institution
rejection, and the complete cached 32-department/74-proposal batch. The test
instance was stopped; the user's existing PostgreSQL service remained running.
The 91 catalog/discovery/planning tests and new-code lint also passed.

An independently connected read-only verification confirmed committed row counts,
no duplicate department IDs, and that no review proposal was marked applied.
Artifacts are `database-before-insertion.json`,
`database-staging-apply-report.json`, `database-staging-repeat-report.json`, and
`database-staging-verification.json` under the existing ignored artifacts folder.
Earlier extraction and dry-run reports below are historical pre-insertion reports.

Implementation: `scripts/nmt_catalog/database_staging.py` and
`scripts/stage_nmt_database.py`. The latter requires the reviewed stage hash and
existing institution UUID and has only the explicit
`--apply-departments-and-review-only` mode. It uses parameterized SQL, an
institution-scoped advisory lock, a serializable transaction, deterministic IDs,
the existing unique constraint and audit tables, and checksum guards. It does not
run migrations or contain an academic publication path. Replaying the same stage
recognizes the completed run rather than creating duplicate evidence.

## Verified application and database audit

The application uses Python/FastAPI, SQLAlchemy asyncio/asyncpg, PostgreSQL, and
Alembic. The React frontend calls existing discovery, comparison, planning, saved
plan, and scheduling routes. No frontend or API contract was changed for this task.

Read-only inspection of the configured database found:

| Area | Observed baseline |
| --- | --- |
| Database environment | Non-local host; `ENVIRONMENT` unspecified. Not approved as a test database. |
| Server | PostgreSQL 18.3 |
| Institutions | 31 |
| NMT identity | Existing university UUID `82e747e1-7543-43b4-88e1-983fe859a082`; official name, Socorro, New Mexico, nmt.edu website. Reuse after identity review. |
| Programs | 872 total, 159 already associated with NMT |
| Courses | 12,926 total; program-scoped identity |
| Prerequisites / corequisites | 600 / 321 flat pair links |
| Saved plans | 129 legacy education plans; 13 normalized plans; 192 plan-course rows |
| Integrity | 396 duplicate `(program_id, course_code)` groups; no orphan courses/programs, blank/placeholder course titles, or cross-institution prerequisite links in the checks performed |
| Migration state | Database revision `0014`; source checkout contains `0001` through `0010` only |

**Schema drift is a blocker, not permission to stamp or recreate the database.**
The live database already contains `catalog_departments`, `program_departments`,
`course_departments`, `catalog_import_runs`, and `catalog_change_audit` tables,
source identity columns, and numeric course credit/hour fields. These are missing
from parts of the checked-in migration/model history. Local course models still
declare integer credits. The baseline saves columns, constraints, indexes and
triggers; no user records or connection secrets are printed.

Current prerequisites/corequisites are unqualified pairs. Existing graduation
audits count program courses, which cannot safely mean that every alternative or
minor course is mandatory. There is no verified institution/catalog-version-aware
canonical course identity in the current code. A legacy `(university, name, degree)`
program uniqueness constraint also cannot represent repeated catalog versions.
Student plans reference existing courses/programs, so overwriting master records
could silently change historical plans. These are reasons to gate publication.

Read-only before/after aggregate fingerprints matched for NNMC programs/courses
and all three saved-plan tables. They do not imply that an import has been tested.

## Sources and extraction strategy

Approved origin: `https://catalog.nmt.edu` only. The public `robots.txt` returned
`Allow: /`; its advertised sitemap returned 404 during inspection. No private API,
authentication bypass, anti-bot workaround, or undocumented Coursedog endpoint
was used.

The public HTML has Nuxt SSR JSON in `__NUXT_DATA__`. The decoder reads that data
without evaluating JavaScript. This provides actual program IDs, official codes,
requirements, sample maps, department relations and source text. Program hrefs
are followed even when their link labels say only `program`. Repeated program
tab URLs are not treated as new programs. `/programs` and `/courses` have
client-rendered listings; their completeness has **not** been established.

Requests use an identifying user agent, >=1.5 seconds between requests, 30-second
timeouts, bounded retries/backoff for transient failures, same-origin validated
redirects, robots checking and persistent checksum-verified caching. Access
responses 401/403/405/429 stop further uncached retrieval. Do not delete failure
markers or change clients/identities to work around a source restriction.

The initial live crawl encountered repeated HTTP 405 responses. Further live
retrieval stopped. The fail-closed circuit breaker was added and tested; remaining
validation used cached data only. Missing pages remain unresolved, not deleted.

The supplied PDF has 818 PDF pages, printed 83-900 of 900. All 818 footer page
numbers were extracted individually, with no assumed +82 offset. The source
SHA-256 is `261034f35c9cb54ccff289573f0af761e0aa464004f22dd943a977991ee412dd`.
Raw page text and source metadata are saved as JSONL. PDF course headings are
**discovery candidates**, not proof of a complete or current course record.

The catalog's home-page transcription/errata warning is preserved as a review
requirement. Errata has not been independently located/approved. Merely finding
a title/code on a PDF page is not counted as field-level source agreement.

### Current extraction results

| Item | Staged or accounted for |
| --- | --- |
| Degrees Offered actual program links | 143 |
| Parsed programs | 73, all awaiting review |
| Department records | 32, staged only |
| PDF course-code candidates | 1,622 |
| Live course records | 1 (`BIOL2110L`), staged only |
| Official sample maps in parsed records | 34, unverified and not cloned into student plans |
| Review inventory | 1,691 pending records; 74 staged academic records |
| Source-field discrepancies | 10 retained; not automatically resolved |
| Academic program/course rows inserted / updated / deleted | 0 / 0 / 0; see limited insertion above for departments and audit evidence |

The crawl was intentionally limited to 20 attempted course pages after program
discovery; access failures prevented more than one cached course record. Other
categories and records remain in the inventory rather than being silently omitted.
All discovered links are accounted for, **not all discoverable catalog programs**.

Parsed degree designations: 1 Associate of General Studies, 1 Associate of Science,
7 BA, 1 Bachelor of General Studies, 22 BS, 13 PhD, 3 Graduate Certificates,
2 Master of Engineering, 1 Master of Engr Management, 18 MS, 1 Master of Science
Teaching, 2 Professional Master, 1 Undergraduate Certificate. Degree designations
are copied from source fields, not inferred from URL codes or headings. Categories
are independently retained; unknown categories remain unknown. Minors and
accelerated pathways are not converted to bachelor degrees.

Examples needing review:

- BS Biology has an explicit 120-credit minimum in the HTML and printed PDF page
  94. An additional Biology rule says **13 credits** in visible text/PDF while its
  embedded numeric field says **12**. Both values remain in the conflict report.
- Some `information` and `policies` source fields differ. Neither is selected as a
  resolved policy when they differ; both variants are preserved.
- BIOL2110L's visible structured rule requires concurrent BIOL2110. Its official
  title spelling is preserved, not silently corrected.
- BIOL2610L's live page was not retrieved; printed PDF page 106 states a
  pre-or-corequisite involving BIOL2110L and a corequisite involving BIOL2610.
  Do not claim dual-source verification of this example.
- Course-set IDs and generic elective placeholders remain distinct from courses.
  No opaque ID or `Untitled Course Set` is accepted as a course code.

## Files and boundaries

- `scripts/nmt_catalog/sources.py`: safe retrieval, cache, public SSR decoding.
- `pdf_evidence.py`: PDF hash, page provenance, layout-preserving text extraction.
- `normalize.py`: identities, numeric ranges, source variants, supported rule AST;
  unsupported nodes retain raw source and require review.
- `evaluate.py`: three-valued QA evaluator for a limited supported subset; **not**
  connected to the production planner. Unknown rules do not become a passing audit.
- `pipeline.py`: deterministic staging, complete discovered-link inventory,
  relationships, unresolved references and conflict reporting.
- `baseline.py`: read-only schema/integrity/aggregate fingerprint inspection.
- `matching.py`: institution+catalog-scoped conservative dry-run proposals;
  duplicate identity matches and legacy/unversioned matches go to review.
- `fixtures.py`: offline academically relevant fixture generation from cache.
- `scripts/import_nmt_catalog.py`: extraction/dry-run CLI. `--apply` deliberately
  refuses **before a connection**; it is not an implemented PostgreSQL publisher.
- `scripts/validate_nmt_catalog.py`: offline stage identity/hash verification.
- `tests/scripts/test_nmt_catalog.py` and `fixtures/nmt`: offline tests and sources.

Generated artifacts are under `fastapi_backend/artifacts/nmt/2026-2027/`, ignored
by Git to avoid committing large cached pages or database schema reports:

- `staged-catalog.json`, `validation-report.json`, `source-conflicts.json`
- `dry-run-report.json`, `repeatability-report.json`
- `database-baseline.json`, `database-baseline-after.json`
- `protected-record-verification.json`
- `pdf-manifest.json`, `pdf-pages.jsonl`, cached source HTML/metadata

### Repeatable commands (PowerShell, from fastapi_backend)

```powershell
# Optional catalog dependency; no application dependency upgrades required.
.\.venv\Scripts\python.exe -m pip install -e '.[catalog,dev]'

# Or use the Codex bundled Python containing pypdf for this PDF-only step.
.\.venv\Scripts\python.exe -m scripts.nmt_catalog.pdf_evidence `
  --pdf 'C:\Users\ALOK\Downloads\2026-2027 NMT Catalog.pdf' `
  --output artifacts/nmt/2026-2027

# Reproduce the current partial stage without accessing the source or database.
.\.venv\Scripts\python.exe -m scripts.import_nmt_catalog `
  --catalog-year 2026-2027 --max-courses 20 --offline --dry-run
.\.venv\Scripts\python.exe -m scripts.validate_nmt_catalog --catalog-year 2026-2027

# Runs against fixtures/mocks only.
.\.venv\Scripts\python.exe -m pytest tests/scripts/test_nmt_catalog.py `
  tests/student/domains/discovery tests/student/domains/planning -q
```

Do not resume the unrestricted online crawl until the official source access
issue has been reviewed. `--database-baseline` explicitly enables read-only DB
inspection; normal offline validation does not connect to PostgreSQL. Never share
the `.env` contents or paste a DSN into reports.

## Validation and outstanding acceptance criteria

23 catalog unit/fixture tests and 68 existing discovery/planning tests passed
together (91 checks). The broader backend suite produced **255 passed, 1 failed**:
`test_comparison_api_routes_are_registered` assumes every FastAPI router entry has
a `.path`; this installed version exposes an `_IncludedRouter` entry without it.
The affected comparison test and application router were not changed in this task.
This existing compatibility failure was not hidden or fixed as part of a catalog import.

Catalog tests cover allowlist/redirect/robots/cache/retry safety,
access-stop behavior, missing/variable credits, placeholder rejection, exact
matching/isolation, non-empty merge protection, AND/OR alternatives, corequisite
timing, supported credit pools, permission/restriction review, source conflicts,
official Biology sample semesters and `--apply` refusal.

File staging repeatability compares deterministic hashes from two cached runs.
The limited department/review-only PostgreSQL insertion has now also passed
repeat-run and rollback tests in the isolated database. No full academic
publication migration or program/course upsert has been tested. Full program-category
coverage, prerequisite graph resolution, cross-source field verification,
specialization dependencies, generalized credit sharing, complete sample-plan
validation and end-to-end NMT frontend/advisor/PDF workflows are not complete.

Computer Use screenshot recovery initially failed with
`FrameArrived timed out: timed out waiting on channel`. On the insertion turn,
accessibility-only inspection of pgAdmin succeeded and showed `edplan_db` in its
object explorer. No SQL was typed into pgAdmin. The tested code-based operation
used the project's configured database connection; no credentials were displayed.

## Required next decisions before database publication

1. Restore/review the real migration sources for revisions `0011`-`0014`; reconcile
   models with the live schema. Do not stamp, reset or rewrite history.
2. Identify a disposable development/test PostgreSQL database with explicit scope.
3. Obtain an accessible official export or resolve public-page HTTP 405 responses
   without bypassing controls; independently verify errata and index completeness.
4. Review a minimal additive schema: institution/catalog versions, canonical
   institution+version+external-ID courses/programs, program-course membership,
   scoped departments, raw+structured requirement groups, immutable official
   sample maps, source/evidence/conflict metadata and links to legacy rows.
5. Implement and test a reviewed publication bridge. Do not flatten alternatives
   into legacy mandatory-course lists. Pin saved-plan academic snapshots/versions;
   do not repoint existing NNMC or student rows during catalog synchronization.
6. Reuse the existing import-run/change-audit tables after inspecting their full
   contract; every approved update must include old/proposed values, record ID,
   source, match method, confidence, run ID and timestamp inside one transaction.
7. Verify institution/version isolation, foreign keys, duplicate prevention, two
   import runs, rollback, NNMC protection, and supported UI flows in the test DB.
8. Request explicit production approval only after those checks and a fresh
   reviewed dry-run report pass. No production approval is requested now because
   the implementation is not ready to publish.
