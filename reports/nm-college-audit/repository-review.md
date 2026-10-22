# Repository and schema review (read-only)

## Implementation and mappings

- Frontend: React 18/Vite/Tailwind in `ChatbotUI`; backend: Python/FastAPI, SQLAlchemy asyncio/asyncpg, Pydantic and Alembic in `fastapi_backend`. Existing catalog scripts use official HTML/PDF fixture extraction; no new dependency or framework was added for this audit.
- `universities.university_id -> programs.university_id -> courses.program_id` is the catalog chain. Courses repeat across programs, so global code uniqueness would be unsafe. `program_courses.education_plan_id` is a student-plan table, NOT a catalog membership bridge; its contents were not read.
- Flat `course_prerequisites` and `course_corequisites` contain directional course UUID edges. Department identity and bridge tables exist; counts/constraints/indexes/column definitions are preserved in `database-snapshot.json` and `schema-evidence.json`.
- No normalized `catalog_versions` table; institution type/abbreviation/active-parent fields unavailable. Current/historical flags inside JSON are not a universal lifecycle contract. No database triggers were returned by schema discovery. DB revision 0014 is not represented by the available local migration files through 0010.
- Live academic rows have `official_source_id`, `official_source_url`, `source_retrieved_at`; JSON also carries mixed import formats/partial-planning flags. A missing dedicated provenance column is reported as a storage gap, not proof that every JSON narrative is unsourced.

## Verified code limitations (no app code changed)

1. `ChatbotUI/src/components/education/EducationPlanEditor.jsx:112` extracts known code substrings from narrative text. It cannot preserve general AND/OR logic or grade/permission/placement semantics; unknown codes may be omitted. Lines 180-225 validate sequencing, 797-817 guard additions and 905-940 guard removals. These guard paths were inspected, not runtime-tested with real student plans.
2. `fastapi_backend/app/student/domains/planning/services/planning_validation_service.py` validates flat prerequisite/corequisite edges and term credits. Passing those checks cannot prove a complex narrative is fulfilled. Existing service tests use fake repositories; see quality-verification.md for the actual run result.
3. `fastapi_backend/app/student/domains/planning/services/graduation_audit_service.py:45` counts planned courses as completed (lines 51-62), treats all program-linked courses as required, and sets graduation_ready from roster/credit coverage (line 88), without completed status or requirement-choice evaluation. This can overstate readiness or require all alternatives.
4. `fastapi_backend/app/student/domains/discovery/schemas/course.py:15` declares integer credits; the course model in `models/program.py` also uses Integer while live PostgreSQL stores numeric credits. Fractional/range values need a contract review; no API/model changes were made.

## Likely causes — hypotheses unless noted above

Mixed older seed/import formats, absent catalog-version identity, partial rosters, uniform default credits and mismatched live/local migration history are consistent with the observed gaps. This audit does not establish who introduced a value or when; transaction logs/import history would be needed to prove causation. Unsupported pricing/eligibility fields were not validated as academic requirements.

## Reproduction

From `fastapi_backend`, use the existing `.venv/Scripts/python.exe -m scripts.audit_nm_colleges --report` for offline report generation. `--collect --report` additionally performs bounded SELECT/SHOW in a repeatable-read, forced-read-only transaction using READ_ONLY_DATABASE_URL if set, otherwise the existing DATABASE_URL. Do not pass secrets on the command line. The script has no apply/write-to-database mode.

The source-evidence file is a manually curated observation log, not a crawler result claiming full inventories. Offline regression tests require no network or database. CSVs use UTF-8 BOM, serialize structured evidence as JSON, and prefix formula-like text with an apostrophe for safe spreadsheet viewing; unchanged raw values remain in the academic JSON snapshot. Difference counts include metadata gaps and review suggestions, NOT only proven academic errors.
