# SIPI catalog import

Completed: 2026-10-17.

## Result

Added **15 programs and 187 program-linked course records** to Render **edplan-db**, PostgreSQL **edplan_db**, in the previously confirmed **Nihal Software** workspace.

The existing SIPI college record was reused: `2ccda41e-a690-401b-8442-34b19df9aa23`, Albuquerque, New Mexico.

Its existing name, **Southwest Indian Polytechnic Institute**, was preserved. The PDF uses **Southwestern Indian Polytechnic Institute**; that source name and the SIPI abbreviation were saved in metadata without creating a duplicate college.

| Program | Credential | Credits | Course rows added | Source printed pages |
|---|---|---:|---:|---|
| Accounting | Certificate | 33 | 8 | 68 |
| Business Administration | Associate of Science | 68 | 20 | 70, 71 |
| Business Administration | Associate of Applied Science | 63 | 19 | 73, 74 |
| Business Administration | Certificate | 33 | 7 | 76 |
| Computer Aided Drafting and Design | Certificate | 38 | 10 | 77, 78 |
| Conservation and Resource Protection | Certificate of Achievement | 12 | 4 | 80 |
| Culinary Arts & Sciences | Associate of Applied Science | 60 | 23 | 82, 83 |
| Early Childhood Education | Associate of Arts | 63 | 18 | 87, 88 |
| Early Childhood Education | Certificate of Achievement | 28 | 10 | 90 |
| Geospatial Information Technology | Associate of Applied Science | 60 | 15 | 96, 97 |
| Geospatial Information Technology | Certificate | 25 | 7 | 98 |
| Natural Resources Management | Associate of Applied Science | 60 | 12 | 103, 104 |
| Network Management | Associate of Applied Science | 61 | 12 | 106, 107 |
| Pre-Engineering | Associate of Science | 61 | 13 | 109, 110, 111 |
| Optical Laboratory Technology | Certificate of Completion | 34 | 9 | 116, 117 |

Course counts are program-linked records. A course used by two programs has one record under each program; these are not counts of unique institution-wide codes.

## Source

- Supplied PDF: `C:\Users\hp\Downloads\SOUTHWESTERN INDIAN POLYTECHNIC INSTITUTE.pdf`.
- Catalog edition: **2026-2027**.
- Supplied excerpt: **57 PDF pages**, printed **61-117**. Printed page = PDF page + 60.
- SHA-256: `6eaf3f400e5424ff5dfd9414a3b36f7304b932f0915d18b20041f08af938a205`.
- Digital text and tables were extracted locally. Program tables and ambiguous rows were visually reviewed.

Some word coordinates and detected table borders overlap total labels or omit continued rows. The final extraction uses preserved logical PDF text, page references and visual review instead of silently accepting unreliable table-cell positions.

## Scope and planning limitations

- Preserved source identifiers, including lower-case ACCT 2110x/2110y suffixes and explicit combined lecture/lab identifiers such as CHEM 1215/L.
- For a printed combined lecture/lab row such as `3/1`, the combined identifier has 4 total credits. The raw split remains in metadata; no new lab identifier or contact-hour values were invented.
- The culinary credit annotation `T` is preserved without assigning it an inferred meaning.
- Unknown lecture/lab contact hours and recommended semester/year fields remain NULL.
- Prerequisite/corequisite text is retained in metadata; no inferred prerequisite graph was created.
- Preserved the Natural Resources lab requirement as **choose two of three**, with the three course records marked as options.
- Generic electives and ambiguous multi-course alternatives remain in complete source requirements. No placeholder courses were invented.
- Early Childhood Education AA background-check/practicum requirements from printed page 87 are retained as non-course requirements.
- Programs carry `course_import_is_partial=true` and `planning_ready=false` metadata. No automatic semester schedules or student plans were created. These indicators do not introduce an application-level planning gate.
- Developmental/adult-basic-education/high-school-equivalency material was not inserted as college degree programs.

## Five programs pending clarification

| Program | Credential | Printed pages | Reason | Specific question |
|---|---|---|---|---|
| Accounting | Associate of Applied Science | 65, 66, 67 | The curriculum states 60 credits, but the suggested sequence explicitly states Total Program Credits: 63. | Is the Accounting AAS total 60 or 63, and which course list is authoritative? |
| Culinary Arts | Certificate | 85 | No program total is stated in the supplied certificate section. | What is the approved certificate total and complete curriculum? |
| Environmental Sciences | Associate of Applied Science | 91, 92, 93, 94 | Program total is 61-62 and ENVS 2996 is 3-4 credits; programs.total_credit_hours accepts one integer, not a range. | Which approved fixed-credit pathway should be imported? |
| Liberal Arts | Associate of Arts | 99, 100, 101 | The listed general education and program-specific requirements appear to sum to 76 credits, while the declared degree total is 63; overlap/substitution rules are not specified. | Which requirements overlap or substitute, so the 63-credit degree can be represented accurately? |
| Vision Care Technology | Associate of Applied Science | 113, 114, 115, 116 | The listed curriculum appears to sum to 71 credits against a declared total of 70; suggested semester totals and displayed rows also disagree. | Provide the corrected 70-credit curriculum, including math and elective requirements. |

No fractional totals were rounded and no database schema was changed. The earlier preference to leave unsupported credit totals pending remains in effect.

## Course details needing clarification

| Scope | Printed pages | Source issue | Question |
|---|---|---|---|
| Accounting Certificate; Business AS/AAS/Certificate | 68, 70, 71, 73, 74, 76 | Required lists use ENGL 1110 Composition I, while suggested sequences use ENGL 2110 Composition I; elsewhere ENGL 2110 is Professional and Technical Communication. | Confirm the correct English code for each program. |
| Business Administration AAS | 74, 75 | Small Business Management appears as ENTR 2210 in requirements and ENTR 2110 in the suggested sequence. | Which ENTR code is correct? |
| Business Administration Certificate | 76 | Business Math appears as BUED 125 versus BUSA 1180; Human Relations in Business appears as BUSA 2230 versus BUSA 2320. | Confirm these two code/title pairs. |
| Business Administration AS | 71, 72 | The suggested semester totals sum to 65, but both stated program totals and the required curriculum total 68. | Which three credits are missing from the suggested schedule? The 68-credit program total is retained; no schedule is assigned. |
| Culinary Arts & Sciences AAS | 82, 83, 84 | Public Speaking is ENGL 1130 here versus COMM 1130 in other curricula; Applied Fundamentals of Baking is CULN 1235L versus CULN 1235; Introduction to Business is BUSA 1110 versus BUSN 1110. CULN 2520L names prerequisite CULN 2410L, whereas the listed course is CULN 2410C. | Confirm the speech, baking, business and food/culture prerequisite codes. |
| Geospatial Information Technology AAS; Network Management AAS | 97, 107, 108 | COSC 145 is titled Intro to UNIV/Linux in one program and Introduction to UNIX Administration in another. | What is the authoritative COSC 145 title? |
| Optical Laboratory Technology Certificate | 117 | The required/elective list names HLED 1120 without credits; the sequence names HLED 1110 for 2 credits. | Which first-aid course code and credit value is correct? |
| Combined math sequence | 77, 78 | MATH 118/119 is a two-course sequence with 2/2 credits, not one identified course. | Confirm individual course titles/codes if separate course records are required. The sequence remains in source requirements. |
| SPAN 1110 | 71, 82, 110 | Spanish I is listed as 3 credits in Business AS and 4 credits in Culinary/Pre-Engineering. | What is the correct credit value and language course code? |
| Early Childhood Education AA biology identifier | 87 | The source prints BIOL/L1110 rather than the BIOL 1110/L layout elsewhere. | Confirm the canonical biology-plus-laboratory identifier before importing this row. |

The dataset retains **52 withheld source fragments** under `held_course_rows`: ambiguous identities, choices, missing credit cells and wrapped elective-pool fragments. This is not a count of distinct omitted courses. Generic choices also remain under `unresolved_requirement_slots` and in full source text.

## Validation and results

- Extraction validation: passed for 15 programs and 187 course records.
- Source-page and raw-line provenance: checked for every inserted course.
- Source-layout regression checks: passed for wrapped identifiers, generic elective boundaries, culinary credit annotations, combined lecture/lab credits, admissions text and choice groups.
- Natural-key uniqueness and cross-program credit consistency: passed.
- Explicit anchors: Conservation certificate 4 courses / 12 credits; Early Childhood certificate 10 / 28; circuit analysis combined row 4 credits.
- Python syntax parsing for all package scripts: passed.
- Rollback-only database dry run: passed, proposing 15 programs and 187 course records.
- Atomic import: committed successfully after dry-run validation.
- Independent read-only comparison: exact titles, codes, credits, source sequences and metadata matched for all 15 programs and 187 course records.
- Original college name, city, state, website and pre-existing profile keys: preserved.
- Other colleges academic-row fingerprints: unchanged.
- Previous imports preserved: IAIA 28 programs / 319 course rows; Mesalands 26 / 258; NMMI 2 / 0.
- Render read-only connector independently confirmed per-program totals, course counts and source hash.
- Final rerun dry run: **0 new programs, 0 new course records**.

No application source files or dependencies were changed. Full application tests and the application linter were not run; UI behavior and end-to-end plan generation were not tested. No student, account, application or education-plan tables were queried or changed.

## Commands

Run from this package directory:

```powershell
$importPython = 'C:\Users\hp\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $importPython -X utf8 .\extract_sipi.py
& $importPython -X utf8 .\import_sipi.py          # rollback-only by default
& $importPython -X utf8 .\import_sipi.py --apply  # already applied; repeat adds no duplicates
& $importPython -X utf8 .\verify_sipi.py
& $importPython -X utf8 .\import_sipi.py          # final duplicate check
```

The importer validates the PDF hash, confirmed Render host, TLS and database name. It reads only DATABASE_URL internally from the existing backend environment file and never prints it. Writes use a serializable transaction, institution-specific advisory lock, pre-import academic snapshot, parameterized SQL and conflict checks that refuse to overwrite divergent data.

## Package evidence

- `sipi-before-import.json`: original college academic snapshot.
- `initial-dry-run.json`: reviewed rollback-only validation.
- `applied.json`: committed IDs and other-college academic fingerprints.
- `verification.json`: exact readback checks.
- `dry-run.json`: final zero-insert rerun.
- `extraction-config.json`, `extract_sipi.py`, `sipi-import-data.json`: reproducible extraction, source decisions and dataset.
- `catalog-pages.json`, `catalog.txt`, `catalog-tables.json`, `catalog-words.json`, `source.json`: source extraction and fingerprint.
- `import_sipi.py`, `verify_sipi.py`: self-contained importer and read-only verification.

Computer Use initialization returned a local kernel-assets error. The import was completed using local PDF extraction, the existing database connection and the Render read-only connector.

No Git commits or pushes were made.
