# WNMU catalog 8 — scoped insertion and review inventory

Update: the user subsequently explicitly approved nullable teaching-hours fields
and verified academic batch insertion. The separate publisher described below
can publish the Pharmacy Technician roster; the original index importer remains
review-only. Do not confuse roster verification with prerequisite verification.

Source: https://catalog.wnmu.edu/content.php?catoid=8&navoid=612

The selected public catalog is **2025–2026**, not 2026–2027. The institution
already exists as `a98d490e-bd5e-4ba9-973a-e5ea7ad53ed5`. At the read-only
2026-10-16 baseline it had zero programs and zero courses.

## What this importer does

`scripts/wnmu_catalog.py` is an **offline, review-only academic inventory importer**.
It inserts the twelve department/school entities explicitly named in the index
into the existing `catalog_departments` table. It stores the 234 distinct official
program IDs, titles, categories and parent academic-unit IDs as review proposals
in `catalog_change_audit`. This includes degrees, certificates, minors, teaching
fields and the general education requirements program. These are not 234 degrees.

It does **not** insert into `programs` or `courses`, publish a curriculum, flatten
course alternatives, infer credit totals/durations, assign unknown active status,
delete/deactivate missing rows, modify plans, or run migrations. It does not claim
that WNMU is ready to use in the student planner.

Administrative Academic Affairs and the College of Education are preserved as
academic-unit context but not mislabeled as departments. Official heading IDs
are scoped to `catoid=8`, e.g. `catoid=8:ent302`. They are source entity IDs, not
invented department codes. Four separately sourced Sustainable Development B.A.
entries retain their distinct official IDs and department relationships.

## Evidence and website limitations

`tests/scripts/fixtures/wnmu/catalog-index.json` is a compact **visible browser DOM
projection**, not a raw HTML download or a full catalog PDF. All 234 program links
were observed to use its stored URL template; there were 234 unique `poid` values.
The transferred projection was checked against the browser: 11,979 characters,
FNV-1a32 `cc257b03`. This is a transfer check only, not proof of authenticity.
The importer separately records the saved snapshot's SHA-256 and retrieval time.
Exact official wording, including “Pending Approval” and spelling, is retained.

The public Graphic Design A.A. detail page was also manually inspected: it
specifies 63 total credits, 31 general education credits, a 31-credit core, and a
one-credit studio elective. That demonstrates why the index alone is insufficient
to publish complete programs. It was not generalized into other programs.

An identifying HTTP request used
`EdPlan-WNMU-Catalog-Importer/1.0 (public academic catalog verification; conservative rate limited)`.
`robots.txt` returned HTTP 200 and specifies **crawl-delay: 120** for the general
user agent. A catalog request returned HTTP 202 with an empty body, so automated
retrieval was not continued. The initial probe used a two-second interval before
the policy was interpreted; future automated retrieval must respect the full
120-second delay. Do not substitute a browser bulk crawler or private `/ajax/`
endpoint to evade restrictions. Ordinary user-browser inspection was used for
the public index and one representative detail only.

A complete permitted catalog export/PDF, or a compliant cached detail crawl,
is needed for remaining program totals, course descriptions, prerequisites,
corequisites, elective alternatives and general-education requirements. A
future fetcher must enforce the official-domain allowlist, redirects, robots,
descriptive user agent, 120-second minimum interval, timeouts/backoff, a cache
and an access-stop policy. This offline tool makes no network requests and
therefore cannot accidentally ignore that policy.

## Database safeguards

One serializable transaction, institution-scoped advisory lock, five-second lock
timeout and thirty-second statement timeout. The institutional ID/name/city/state/
website must exactly match the reviewed target. Existing department matches use
stable scoped identity or source URL; name-only/conflicting matches are reviewed
without overwriting. UUIDs derive deterministically from institution and source.
Foreign keys and existing unique constraints remain enforced. Each department
operation and program proposal has provenance, old/proposed values, confidence,
match method, import run and timestamp in the audit table.

The stage checksum is required to apply. A repeated completed stage produces no
new rows. Fingerprints of all existing programs, courses, prerequisite/corequisite
links, department relationships and student-plan tables must remain identical
inside the transaction or the entire batch rolls back. No user plan content or
database credentials are printed. Existing valid data is never replaced by nulls.

The refreshed baseline still reports database revision `0014` without matching
local migration source and 396 duplicate program/course-code groups elsewhere.
Those are pre-existing issues, not WNMU records; this importer does not change them.

Academic publication also needs an explicitly reviewed mapping for catalog
versions, same-title/different-department programs and prerequisite alternatives.
The legacy unique `(university_id, program_name, degree)` key cannot preserve
every distinct official program simply by copying names, and the existing flat
prerequisite links cannot faithfully represent every AND/OR rule. This batch does
not disguise those limitations with renamed titles or missing requirements.

## Commands (from fastapi_backend)

```powershell
.\.venv\Scripts\python.exe -m scripts.wnmu_catalog
# Review artifacts/wnmu/catalog-8/staged-catalog.json and the printed stage hash.
.\.venv\Scripts\python.exe -m scripts.wnmu_catalog `
  --expected-stage-hash <reviewed-hash> --apply-departments-and-review-only
```

Reads `DATABASE_URL` from existing `.env`/environment without exposing it. Reports
go to ignored `artifacts/wnmu/catalog-8/`. There is no general academic `--apply`.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest tests/scripts/test_wnmu_catalog.py -q
```

The PostgreSQL tests reuse the guarded disposable test-cluster fixture from
`test_nmt_database_staging.py`. Set `NMT_TEST_DATABASE_URL` to the explicitly
disposable local cluster and `NMT_TEST_PGDATA` to its exact directory. Tests verify
`SHOW data_directory` before creating their random, isolated test schema and only
drop that schema afterward. Never point tests at the application database.

```powershell
.\.venv\Scripts\python.exe -m pytest tests/scripts/test_wnmu_database_staging.py -q
```

Verification: 13 offline tests and 4 real PostgreSQL tests passed before applying
the batch. Tested atomic rollback after department insertion, replay, target/hash
rejection, conflict preservation, distinct same-title programs, official hierarchy,
source URL restrictions and unknown-value preservation.

## Approved academic roster publisher

`scripts/publish_wnmu_batch.py` prepares one deliberately narrow, reviewed batch
from `tests/scripts/fixtures/wnmu/pharmacy-technician.json`. It publishes the exact
Pharmacy Technician Certificate title, Certificate qualification, 46 total credits,
and all 16 courses named in the program's supporting/core sections. Course credits
reconcile to the official subtotals of 13 supporting + 33 core credits. Source
course IDs come from the public course-control attributes; they are never guessed
from course numbers. The program source URL is stored for membership/name/credit
evidence, not falsely described as sixteen separately retrieved course pages.

The roster transfer matches the browser projection: 1,526 characters and FNV-1a32
`8c11e2d9`. SHA-256 of the UTF-8 fixture and the official index fixture are recorded
in every published row's provenance. PT 1011 additionally retains the inspected
official description and UG level. Other descriptions and levels remain unknown.
Course ownership by department is not inferred from program membership; only the
explicit program-to-department link is inserted.

The batch does **not** certify course prerequisites/corequisites, course eligibility,
intake, active status, semester availability or a recommended academic sequence.
`course_rules_verified=false`, `course_rules_status=not_fully_retrieved` and related
metadata retain these limitations. Recommended year/semester remain NULL and the
existing `default_plan_eligible` property is false. No prerequisite/corequisite
edges, elective placeholders or artificial semester placements are created.
Students/advisors must still consult the official course descriptions for rules.
The other 233 index entries remain review-only; this is not a full WNMU import.

### Nullable contact hours and migration-history exception

The user approved allowing unknown lecture/lab hours. In the same transaction as
the batch, only `courses.lecture_hours` and `courses.lab_hours` lose NOT NULL and
their implicit zero defaults. Their existing NUMERIC types and nonnegative check
constraint stay intact. Every existing row value, including legitimate zero and
fractional hours, is preserved. ORM fields now use nullable Decimal/Numeric;
discovery and scheduling API schemas accept numeric values or JSON null.

The live database is at revision 0014, but the repository lacks migrations
0011–0014. Therefore this explicitly approved, auditable schema patch does not
stamp/reset Alembic, invent missing revisions, or attempt an unsafe upgrade/head
operation. Its exact DDL is version-controlled in the publisher and its before/
after column definitions are recorded in the import audit. Recover the missing
migration sources and reconcile this patch before a future migration rollout.
A fresh install using only old migrations also needs this approved patch; model
metadata alone does not migrate an existing database.

One serializable transaction covers DDL, one program, sixteen courses, one
department link, nineteen audit records and its run ledger. Any late failure
rolls all of them back, including column changes. Existing academic and student
rows are fingerprinted before/after, excluding only the deterministic batch row
IDs. Conflicting existing programs stop for review without overwriting. Replays
verify actual rows, metadata, timestamps, department link, nullable schema and
audit count before reporting zero new inserts.

```powershell
.\.venv\Scripts\python.exe -m scripts.publish_wnmu_batch
.\.venv\Scripts\python.exe -m scripts.publish_wnmu_batch `
  --apply --approved-nullable-hours --expected-batch-hash <reviewed-hash>
```

Reports and the prepared batch are saved under ignored
`artifacts/wnmu/catalog-8/pharmacy-technician/`. No network requests are made by
this publisher. Tests use the same guarded, disposable PostgreSQL fixture as
the index importer and never the application database.

Validation before application: ten new source/model tests plus four real
PostgreSQL tests passed, including ORM -> repository -> API serialization of
all sixteen NULL-hours courses. The broader student/catalog run had 200 passes
and the previously observed comparison-router `_IncludedRouter.path` failure;
that unrelated test was not changed.

Applied and independently verified on 2026-10-16:

- Run: `00f6b6b3-06c9-5f46-88f2-05a71c43c405`.
- Program: `5da3371f-6cde-57e9-ab83-8c69a4b2faae`.
- One program, sixteen courses (46 credits), one department link and nineteen
  audits committed. Both contact-hours columns are nullable NUMERIC without a
  default; all sixteen imported contact-hour pairs are NULL.
- Replay verified the complete committed batch and inserted zero rows.
- Independent live ORM/repository/API-model validation returned all sixteen
  courses successfully. Saved plans and NNMC fingerprints, aggregate integrity
  results, existing-row fingerprints and Alembic revision were unchanged.
- Seventy-two orchestration tests also passed. No local servers were listening
  on ports 8000/5173 during verification, so this is not a browser/HTTP runtime
  verification. Start/reload the backend to load the updated API code.
- Detailed evidence: `pharmacy-technician/independent-verification.json`,
  `apply-report.json`, `repeat-report.json` and before/after database reports
  beneath the ignored catalog artifact folder.
