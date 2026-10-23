# NMMI catalog import

Completed: 2026-10-17.

## Result

Imported into Render **edplan-db**, PostgreSQL **edplan_db**, in the previously confirmed **Nihal Software** workspace.

The existing New Mexico Military Institute record in Roswell, New Mexico was reused:
`d1cb699c-5d75-4055-8334-e042c99557a2`.

| Program | Degree | Minimum credits | Concentrations stored in metadata | Course rows inserted |
|---|---|---:|---:|---:|
| Associate in Arts | Associate of Arts | 60 | 10 | 0 |
| Associate in Science | Associate of Science | 60 | 9 | 0 |

Concentrations are optional pathways inside the two degrees, not separate credentials. The database stores the catalog's category requirements, graduation/residency requirements, general education framework, source text and page references. Category requirements are stored as minimums, without inferred maximum caps. Only the explicitly stated Military Science/Leadership range retains a 2-to-12-credit range.

All imported program metadata has `planning_ready=false`, `requires_catalog_course_details=true`, and `course_credit_values_available=false`. These are data completeness indicators; no application behavior was changed to enforce a new planning gate.

## Source and scope

- Supplied PDF: `C:\Users\hp\Documents\NMMI catalog.pdf`.
- Catalog: New Mexico Military Institute Academic Catalog 2026-27.
- 20 scanned PDF pages, printed pages 19-38.
- Junior-college curriculum and requirements: printed pages 30-37.
- SHA-256: `a3e1f115ca7318e3a9966147a3d6824689c59b6637eae4052420eaa32a56ac3e`.
- Page mapping: printed page = PDF page + 18.
- Relevant PDF pages 12-19 were visually reviewed alongside local OCR.
- Source text fields deliberately retain OCR output; structured degree headings, credit totals, graduation requirements and concentration names were visually checked.

The excerpt contains academic policies, high school requirements, and junior-college requirements. High school courses, honors, conduct policies and non-degree activities were not inserted as college programs.

## Concentrations

**Associate in Arts:** Art; Aviation Technical Management; Business Administration; Communications; Criminal Justice; English; History; Philosophy; Political Science; Social Science.

**Associate in Science:** Athletic Training; Biological Sciences; Computer Science; Mathematics; Physical Sciences; Pre-Engineering; Pre-Kinesiology; Pre-Medicine/Dental/Veterinary; Pre-Nursing.

Each concentration includes its scoped source text, PDF/printed page references and a flag identifying it as part of the parent degree. Required, optional, recommended and alternative choices remain in their source text; they were not flattened into a list of mandatory courses.

## Pending data and questions

| Item | Source printed pages | Reason / specific question |
|---|---|---|
| Individual course records | 32-37 | This excerpt lists course choices and category requirements but no individual course-credit values. The database requires a credit value for each course. Supply the 2026-27 course-description/credit pages to complete course import. No zero or guessed credits were inserted. |
| COMM 1130 | 32, 34 | The same code is printed as both Introduction to Communication and Public Speaking. Which code/title pairing is authoritative for each? |
| Forensic Science I | 32, 35 | Printed as PHSC 1120 in the AA list and PHYS 1120 in the AS list. Which department prefix is correct? |
| Social Science concentration | 34 | The text requires at least four courses from a list containing only three. Which course or selection rule is missing? |
| Pre-Nursing total and pathway | 37 | The catalog says this concentration may exceed the 60-credit AS minimum and depends on the receiving university. Which receiving-university pathway and complete requirement list applies? It was retained as AS metadata, without inventing a separate 60-credit degree. |

No fractional program totals were encountered for the two base degrees. The user's earlier preference to leave fractional-total programs pending remains unchanged.

## Validation

- Reproducible extraction from preserved OCR and configuration: passed.
- Python syntax parsing for the package: passed.
- Rollback-only database dry run: passed; two proposed program inserts, zero course inserts.
- Atomic import: committed successfully.
- Final read-only comparison: exact metadata match for both programs and all 19 concentration entries.
- Source hash, source pages and original college name, location, website and profile: verified.
- Fingerprints of other colleges' university, program and course records: unchanged.
- Earlier imports preserved: IAIA 28 programs / 319 course rows; Mesalands 26 programs / 258 course rows.
- Rerun dry run: zero new program rows and zero new course rows.
- No application source files, dependencies, authentication, access controls, student records or education plans were modified.
- Full application test suite and application linter were not run because this is an academic-data import with no application changes. UI and end-to-end planning remain unverified; complete course-credit pages are required before a full NMMI course catalog can be supplied.

Final metadata review removed inferred fixed-category maximums from only the two newly imported records. That bounded correction and its checks are recorded in `requirement-metadata-review.json`.

## Commands and evidence

Run from this directory with the existing bundled Python runtime:

```powershell
$importPython = 'C:\Users\hp\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $importPython -X utf8 .\extract_nmmi.py
& $importPython -X utf8 .\import_nmmi.py          # rolls back by default
& $importPython -X utf8 .\import_nmmi.py --apply  # already applied; rerun inserts nothing
& $importPython -X utf8 .\verify_nmmi.py
& $importPython -X utf8 .\import_nmmi.py          # final idempotence check
```

The importer reads only DATABASE_URL internally from the existing backend environment file and never prints credentials. It verifies the confirmed Render host, TLS and database name. Writes use a serializable transaction, an institution-specific advisory lock, conflict checks, source validation and a pre-import academic-record snapshot.

Evidence files:

- `nmmi-before-import.json`: original NMMI academic snapshot.
- `initial-dry-run.json`: first rollback-only validation.
- `applied.json`: successful import and academic fingerprints.
- `verification.json`: final exact readback and preservation checks.
- `dry-run.json`: final rerun, zero duplicate inserts.
- `nmmi-import-data.json`, `extraction-config.json`, `extract_nmmi.py`: reproducible structured dataset.
- `ocr/`, `catalog-ocr.txt`, `source.json`: local OCR evidence and source fingerprint.
- `import_nmmi.py`, `verify_nmmi.py`: safe importer and read-only verification.

Computer Use initialization returned a local kernel-assets error. The import was completed with the PDF tools, existing database connection and Render read-only connector instead.

No Git commits or pushes were made.
