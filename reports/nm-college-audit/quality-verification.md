# Quality verification — read-only audit

## Passed

- Live academic snapshot: forced read-only startup and repeatable-read transaction; `transaction_read_only` returned `on` at both ends. Bounded table inventories matched count queries: 31 institutions, 944 programs, 13,706 course rows, 600 prerequisite edges and 321 corequisite edges. No database mutations; no student row contents accessed.
- All 20 required directory keys are included, with the exact 7/9/4 category split. Nine excluded branch records and two Diné centers are separately reported and preserved.
- Offline audit plus targeted existing planner tests: **25 passed**. Command from `fastapi_backend`:

  ```powershell
  .\.venv\Scripts\python.exe -m pytest tests/scripts/test_nm_college_audit.py tests/student/domains/planning/test_planning_validation_service.py tests/student/domains/planning/test_graduation_audit_service.py -q
  ```

- Tests cover branch/parent separation, UNM duplicate candidates, SIPI alias/spelling, exact scope, credit precision and missing values, cyclic groups, metadata whitelisting, JSON provenance, safe CSV export and read-only collector structure. A synthetic test reproduces the observed planned-versus-completed graduation limitation; its passing result is not approval of that behavior.
- Ruff formatting applied only to the three new audit Python files. Ruff checks pass with **E501 excluded** because embedded Markdown/SQL report strings exceed the configured line length. The unrestricted check does not pass line-length rules; no project lint configuration was changed. Existing deprecated Ruff-setting warning remains.

## Not claimed / remaining verification

- No exhaustive 20-institution academic inventory comparison. WNMU's cached 234-entry program/credential index and 16-course Pharmacy roster, NMJC's 15-entry associate subset, and selected SIPI/CNM facts are explicitly scoped. Five passing field checks do not certify five programs or any institution.
- No fresh independent retrieval of WNMU's individual course prerequisite rules. Missing rules are not interpreted as no prerequisites.
- No full application build, full backend suite, frontend/browser regression, production planner execution, or student-data inspection: application code was not changed. Existing fake-repository planner tests do not establish full narrative-rule correctness.
- No visual PDF QA claimed. Browser initialization failed with a kernel-assets path error; web text/PDF extraction was used. Blocked official sources were not bypassed.
- A dedicated read-only DB role was unavailable; the existing role has write privileges, but this session was forced read-only. Remote environment ownership remains unconfirmed. The initial sandbox network attempt failed; approved read-only collection succeeded afterward.
- Catalog year, institution type/abbreviation/active-parent fields and exact retrieval timestamps cannot be invented where the DB/schema/source tool does not supply them.
- No import, schema repair, identity merge, deletion, deployment, or backend behavior change was performed. All remediation is proposal-only.

See `reproducibility-check.json` for input/output hashes from two offline report runs. Machine-readable CSV finding totals include provenance gaps, candidate duplicates and review suggestions; they are not counts of confirmed wrong academic values.
