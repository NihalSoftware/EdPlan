# Mesalands catalog import

Status: APPLIED to Render instance edplan-db, PostgreSQL edplan_db / public. Verified on 2026-10-17.

## Source and scope

- Source: the user-supplied catalog.pdf; original PDF unchanged.
- PDF Title metadata identifies the 2025-2026 catalog. The supplied excerpt contains 37 scanned pages, corresponding to printed pages 50-86.
- Source SHA-256: 5c3deb40eeb8b38aaf55e929decb06508d593166ce902eaa012bc27b9049d35a
- Existing college record: Mesalands Community College, Tucumcari, New Mexico.
- Added 26 programs and 258 program-specific course rows. Course rows may repeat the same course across different programs.
- Course coverage is partial: 14 uncertain/conflicting course rows were withheld.
- Generic electives, alternatives, conditional FYEX requirements and experiential-credit slots remain in source requirements; no course codes were invented.
- Catalog semester/year labels and prerequisite wording are retained as source metadata. No automatic semester assignments, course offerings, meeting times, lecture/lab hours or student plans were invented.
- The catalog is labeled 2025-2026, not the current academic year.
- The existing college profile and website were preserved; import metadata was added under mesalands_catalog_import.

## Programs imported

| Program | Credential | Credits | Printed page | Course rows |
| --- | --- | ---: | ---: | ---: |
| Education - Bilingual Option | Associate of Arts | 60 | 58 | 15 |
| Education - Early Childhood Option | Associate of Arts | 62 | 59 | 19 |
| Education - Elementary Education Option | Associate of Arts | 60 | 60 | 13 |
| Education - Secondary Education Option | Associate of Arts | 60 | 61 | 13 |
| Fine Arts - Digital Media Arts Option | Associate of Arts | 60 | 62 | 11 |
| Fine Arts - Studio Art Option | Associate of Arts | 60 | 63 | 10 |
| Fine Arts - Studio Art Proficiency | Occupational Certificate | 18 | 64 | 3 |
| Fine Arts - Comic Illustration and Character Design | Occupational Certificate | 15 | 65 | 4 |
| Fine Arts - Animation and Game Art | Occupational Certificate | 19 | 66 | 6 |
| Fine Arts - Bronze Metal Casting | Occupational Certificate | 18 | 67 | 4 |
| General Studies - Occupational/Experiential Learning | Associate of Arts | 60 | 68 | 7 |
| Human Services - Social Services | Certificate | 16 | 69 | 13 |
| Human Services - Social Work Option | Associate of Arts | 60 | 70 | 13 |
| Liberal Arts - University Studies Option | Associate of Arts | 60 | 71 | 9 |
| Natural Sciences - Geology Option | Associate of Arts | 60 | 72 | 14 |
| Natural Sciences - Paleontology Option | Associate of Arts | 60 | 73 | 13 |
| Nursing | Associate of Applied Science | 78 | 75 | 20 |
| Cowboy Arts - Western Artistic Silversmithing and Fabrication | Associate of Applied Science | 60 | 78 | 14 |
| Artistic Silversmithing | Applied Science Certificate | 33 | 79 | 5 |
| Artistic Silversmithing | Occupational Certificate | 15 | 79 | 3 |
| Business Administration - General Option | Associate of Applied Science | 60 | 80 | 11 |
| Farrier Science | Associate of Applied Science | 60 | 81 | 16 |
| Farrier Science | Occupational Certificate | 18 | 82 | 4 |
| General Studies - Occupational/Experiential Learning | Associate of Applied Science | 60 | 83 | 7 |
| Technical and Professional Writing | Occupational Certificate | 19 | 84 | 5 |
| Wind Energy Technology | Occupational Certificate | 15 | 86 | 6 |

## Pending programs

The user explicitly requested: Leave fractional-credit programs pending. The database/application were not migrated, and totals were never rounded.

- Agri-Business | Associate of Applied Science (printed page 74): Semester totals 15+15+12+14 add to 56, but the catalog states 60 degree credits. Program held; authoritative total/curriculum needed.
- Nurse’s Assistant | Certificate (printed page 76): Fractional program total cannot fit integer database column; user requested to leave pending.
- Phlebotomy | Certificate (printed page 77): Fractional program total cannot fit integer database column; user requested to leave pending.
- Wind Energy Technology | Associate of Applied Science (printed page 85): Fractional program total cannot fit integer database column; user requested to leave pending.
- Wind Energy Technology | Applied Science Certificate (printed page 86): Fractional program total cannot fit integer database column; user requested to leave pending.
- General Business (AA), Animal Science (AAS), Public Administration/Law Enforcement (AAS) (printed page 57): Overview names these options, but their complete curricula and specific totals are absent from the supplied excerpt.

## Withheld course rows

These rows were not inserted. The original table text remains available in the program source metadata and OCR files.

| Printed page | Program | Code or row | Reason |
| --- | --- | --- | --- |
| 64 | Fine Arts - Studio Art Proficiency / Occupational Certificate | ARTS1610 | The same page labels ARTS1610 as both Drawing I and Drawing II. |
| 64 | Fine Arts - Studio Art Proficiency / Occupational Certificate | ARTS1610 | The same page labels ARTS1610 as both Drawing I and Drawing II. |
| 67 | Fine Arts - Bronze Metal Casting / Occupational Certificate | ARTS2850 | The program calls ARTS2850 Art Foundry I, but the general education list calls it Ceramics II. |
| 71 | Liberal Arts - University Studies Option / Associate of Arts | PSYC 11101ntroduction to Psychology (Area IV) 3 | Course code is incomplete or contains ambiguous OCR characters |
| 72 | Natural Sciences - Geology Option / Associate of Arts | GEOL1110 | The plan names Physical Geology, while the general education list names Physical Geography. |
| 72 | Natural Sciences - Geology Option / Associate of Arts | COMM1130 | The Geology plan assigns 4 credits, but the general education catalog and other plans assign 3. |
| 73 | Natural Sciences - Paleontology Option / Associate of Arts | GEOL1110 | The plan names Physical Geology, while the general education list names Physical Geography. |
| 75 | Nursing / Associate of Applied Science | MATH1155 | Source row combines alternatives rather than one unambiguous course |
| 79 | Artistic Silversmithing / Applied Science Certificate | WELD1110 | The source labels WELD1110 Composition I, conflicting with Welding Fundamentals elsewhere. |
| 80 | Business Administration - General Option / Associate of Applied Science | COMM1130 | Source row combines alternatives rather than one unambiguous course |
| 82 | Farrier Science / Occupational Certificate | ANSC1110 | ANSC1110 is Horseshoeing Theory on page 82 but Animal Science Careers on page 74. |
| 83 | General Studies - Occupational/Experiential Learning / Associate of Applied Science | ENGL2994 | The plan shows 1 credit, but the general education listing states 3 credits. |
| 83 | General Studies - Occupational/Experiential Learning / Associate of Applied Science | MATH1130 | The AAS plan assigns 3 credits, but the general education list and AA plan assign 4. |
| 84 | Technical and Professional Writing / Occupational Certificate | ARTS1520 | No single explicit numeric credit cell in the course row |

## Files

- mesalands-before-import.json: original Mesalands college/profile and its original (empty) program/course records.
- mesalands-import-data.json: imported dataset, provenance, held rows and unresolved selection slots.
- import_mesalands.py: dry-run by default; --apply commits one atomic import.
- extract_mesalands.py, extraction-config.json, table-rows.json, and ocr/: reproducible dataset preparation from retained OCR evidence.
- catalog-ocr.txt: searchable OCR of the supplied excerpt.
- applied.json: inserted IDs and successful commit evidence.
- dry-run.json: repeat-run evidence showing zero inserted programs/courses.
- verification.json: independent read-back results.

## Validation

- Python syntax checks: passed for extraction and import scripts.
- Dataset checks: unique natural keys, valid exact course codes, positive whole-number program totals, credit-cell/visual evidence, source-page bounds, and independently checked anchor courses.
- Anchor courses include Nursing NMNC1110 (3 credits), Farrier Science FASC1210L (3 credits), and ENGL2999 (1 credit). Wind Energy occupational certificate has 6 identified courses totaling 15 credits.
- Pre-import database trial: all 26 programs and 258 courses inserted successfully, then rolled back.
- Saved-record verification: all imported program totals, course codes, course names, credit values, page references and source hashes match the dataset.
- Repeat import trial: zero new programs and zero new courses; rolled back.
- Original Mesalands profile: preserved.
- Other colleges: transaction fingerprints unchanged. IAIA independently remains at 28 programs / 319 course rows.
- Student, applicant, user, education-plan and authentication records were not read or modified.
- Database writes used the previously confirmed Render instance, TLS and a serializable transaction with a college-specific advisory lock.
- No application source files, schema, dependencies, permissions or credentials were changed. Nothing was committed or pushed.

## Commands

Commands used the bundled Codex Python runtime:

- python -m py_compile import_mesalands.py extract_mesalands.py
- python import_mesalands.py (pre-import dry run / rollback)
- python import_mesalands.py --apply
- python import_mesalands.py (post-import idempotency dry run / rollback)
- Independent read-only SQL verification of every imported program and course, original profile preservation, and IAIA counts.
- git -C D:/EdPlan diff --check

A full application test suite was not run: application code was unchanged. Validation focused on source extraction, database constraints, atomicity, preservation, value accuracy and idempotency.

To rebuild the dataset from retained OCR evidence, run python extract_mesalands.py. Review the resulting JSON before applying. Credentials are read internally from the existing environment file and are not stored in this package.
