# New Mexico academic-data audit — 2026-10-22

Read-only database/institution audit with partial official-catalog comparison. **No institution is certified as fully imported or academically correct.**

Expected parent institutions: 20 (7 public four-year, 9 independent public, 4 tribal). 19 keys have parent candidates; 18 have exactly one. Missing parent: dine; multiple parent candidates: unm.

Counts below are database row counts, NOT official catalog totals, distinct institutional course counts, offered sections, or verified completeness percentages.

| Key | Parent identity | Programs | Course rows | Pre/co edges | Latest source edition established | Overall |
|---|---|---:|---:|---:|---|---|
| enmu | VERIFIED | 64 | 741 | 0/0 | UG 2025-2027; graduate 2026-2028 | PARTIAL |
| nmhu | VERIFIED | 17 | 439 | 0/0 | UG and graduate 2025-2026 | PARTIAL |
| nmt | VERIFIED | 159 | 693 | 0/0 | 2026-2027 | PARTIAL |
| nmsu | VERIFIED | 6 | 245 | 97/44 | UNVERIFIED | PARTIAL |
| nnmc | VERIFIED | 67 | 1522 | 0/0 | UNVERIFIED | PARTIAL |
| unm | POSSIBLE_DUPLICATE | 12 | 490 | 99/44 | 2026-2027 | POSSIBLE_DUPLICATE |
| wnmu | VERIFIED | 1 | 16 | 0/0 | 2025-2026 | PARTIAL |
| cnm | VERIFIED | 2 | 8 | 4/0 | 2026-2027 | PARTIAL |
| ccc | VERIFIED | 40 | 675 | 0/0 | 2026-2027 | PARTIAL |
| luna | VERIFIED | 30 | 920 | 0/0 | 2026-2027 (landing label) | PARTIAL |
| mesalands | VERIFIED | 26 | 258 | 0/0 | 2025-2026 indexed; current unverified | PARTIAL |
| nmjc | VERIFIED | 33 | 330 | 0/0 | 2026-2027 | PARTIAL |
| nmmi | VERIFIED | 2 | 0 | 0/0 | UNVERIFIED | PARTIAL |
| sjc | VERIFIED | 137 | 2460 | 34/4 | UNVERIFIED | PARTIAL |
| sfcc | VERIFIED | 132 | 1735 | 366/229 | UNVERIFIED | PARTIAL |
| senmc | VERIFIED | 110 | 1090 | 0/0 | 2026-2027 | PARTIAL |
| dine | MISSING_IN_DB | 0 | 0 | 0/0 | 2026-2027 | MISSING_IN_DB |
| iaia | VERIFIED | 28 | 319 | 0/0 | 2026-2027 (landing label) | PARTIAL |
| ntu | VERIFIED | 63 | 1578 | 0/0 | UG 2026-2027; graduate 2025-2026 | PARTIAL |
| sipi | MISMATCH | 15 | 187 | 0/0 | 2026-2027 | MISMATCH |

## Safety and schema

Captured: 2026-10-22T06:15:08.307171+00:00. PostgreSQL 18.3 (Debian 18.3-1.pgdg12+1); target: remote_environment_unconfirmed; declared environment: unspecified. A dedicated read-only URL was not configured unless recorded otherwise in database-snapshot.json. Role has write privileges: True; both connection default and repeatable-read transaction were forced read-only and checked. Prefer a dedicated least-privilege audit account/read replica next time; environment ownership is not independently confirmed. No data/schema mutations or student row-content queries were issued.

Live Alembic revision 0014; local source revisions: 0001, 0002, 0003, 0004, 0005, 0006, 0007, 0008, 0009, 0010. History aligned: False. `courses.program_id` defines catalog program membership; `program_courses.education_plan_id` is a student-plan relationship, not a catalog bridge. University identity has no dedicated type/abbreviation/current-parent flag, and no normalized catalog_versions table exists. Academic provenance/year fields are audited per record, not inferred.

## Verified issues and interpretation

- UNM has two parent candidates; preserve both until saved-plan references and aliases are reviewed.
- Diné has Shiprock and Crownpoint center rows but no appropriate Tsaile parent row; no branch is counted as a parent.
- SIPI stored name uses Southwest rather than the official Southwestern; alias match does not certify spelling.
- Empty program course rosters and missing catalog-year/source provenance are enumerated in CSVs. They establish DB gaps, not invented official course counts.
- Repeated codes across different programs/institutions are legitimate possibilities. Only within-program duplicate-code groups are flagged as candidates, with version/elective review required.
- Cached WNMU same-edition program inventory and Pharmacy roster are compared separately with explicit capture dates. Other catalog visits establish editions and selected facts, not exhaustive curricula.

## Coverage limits

Every required source landing was attempted. See source-log.md for inaccessible pages, dynamic-only content, PDF availability and exact editions. PDF sources were inspected selectively, not exhaustively parsed into full course/requirement datasets. No missing edition was fabricated. Unknown DB catalog years prevent reliable like-for-like curriculum mismatch claims. No row-count comparison alone proves an import complete. Header-only or sparse differences do NOT mean zero source discrepancies.

## Planner code review (not a student-data/runtime test)

The editor extracts recognized course codes from text and checks prior-term prerequisites and same-term corequisites, including removal guards. It does not encode all narrative alternatives, minimum grades, placement or permission conditions. The graduation audit treats every linked catalog course as required and counts planned course IDs as completed; planned credits alone cannot prove graduation eligibility. These are verified implementation limitations, not a fresh end-to-end workflow pass. See repository-review.md for exact paths and line references.

## Findings counts

```json
{
  "expected": 20,
  "parent_keys_with_candidates": 19,
  "unambiguous_parent_keys": 18,
  "missing_parent_keys": [
    "dine"
  ],
  "duplicate_parent_keys": [
    "unm"
  ],
  "extra_related_records": 11,
  "full_curriculum_verifications": 0,
  "program_findings": {
    "NO_LINKED_CATALOG_COURSES": 179,
    "SOURCE_OR_CATALOG_YEAR_UNRECORDED": 877,
    "OFFICIAL_ID_NOT_MATCHED_CACHED_PROGRAM_INDEX": 233,
    "PUBLISHED_CREDENTIAL_WITHOUT_MATCHING_PROGRAM": 1,
    "OFFICIAL_SOURCE_INTERNAL_CREDIT_CONFLICT": 1,
    "CANDIDATE_PROGRAM_VERSION_TITLE_CREDIT_REVIEW": 1,
    "SUSPICIOUS_UNIFORM_CREDIT_DEFAULT": 122,
    "NMJC_ASSOCIATE_ENTRY_YEAR_CREDENTIAL_REVIEW": 15
  },
  "course_findings": {
    "SOURCE_OR_CATALOG_YEAR_UNRECORDED": 12505,
    "POSSIBLE_DUPLICATE_WITHIN_PROGRAM_CODE": 398
  },
  "dependency_findings": {
    "COMPLEX_NARRATIVE_REQUIRES_RULE_REVIEW": 1370,
    "SOURCE_RULES_NOT_FULLY_RETRIEVED": 16,
    "CONCURRENT_GROUP_REVIEW": 149,
    "OFFICIAL_SOURCE_INTERNAL_CODE_CONFLICT": 1,
    "SOURCE_ALTERNATIVE_NOT_FLAT_ALL_REQUIRED": 1
  },
  "database_mutations": 0,
  "student_row_contents_accessed": false,
  "database_counts": {
    "catalog_departments": 53,
    "course_corequisites": 321,
    "course_departments": 0,
    "course_prerequisites": 600,
    "courses": 13706,
    "program_departments": 1,
    "programs": 944,
    "universities": 31
  },
  "programs_without_catalog_year": 806,
  "programs_explicitly_partial_import": 71,
  "courses_explicitly_partial_import": 764,
  "courses_without_catalog_year": 11741,
  "programs_without_official_source_url": 877,
  "programs_without_any_recorded_source_url": 877,
  "courses_without_official_source_url": 12448,
  "courses_without_any_recorded_source_url": 12448,
  "department_bridge_issues": [],
  "orphan_program_rows": 0,
  "orphan_course_rows": 0,
  "dangling_dependency_edges": 0,
  "excluded_branch_rows": 9,
  "dine_center_rows": 2,
  "fractional_course_credit_rows": 14,
  "zero_credit_course_rows_review_not_automatically_invalid": 264,
  "cycle_components": {
    "prerequisite": 0,
    "corequisite": 149
  },
  "nmt_program_credit_distribution": {
    "120": 159
  },
  "selected_field_verifications": 5,
  "source_status_counts": {
    "PARTIAL": 14,
    "SOURCE_UNVERIFIED": 1,
    "SOURCE_BLOCKED": 5
  }
}
```

## Priorities and measured gaps

Programs without stored catalog year: 806/944; course rows without year: 11741/13706. Selected field matches: 5; full curriculum verifications: 0. See verified-samples.csv; passing one field does not certify a program.

Priorities: Diné/UNM identity reconciliation, version/provenance recovery, approved official-source inventory completion, then planner dependency/choice semantics. Source-blocked institutions: nmmi, nmsu, nnmc, sfcc, sjc. Mesalands current edition remains unverified.

Snapshot SHA-256: `acb148b9044548dab9ee9bbde8f81bdcda1295cb3caadbcd079e7d7bf7f83b3b`. See remediation-plan.md and quality-verification.md.
