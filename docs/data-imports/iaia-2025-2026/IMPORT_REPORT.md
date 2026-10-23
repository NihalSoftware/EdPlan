# IAIA catalog import

Status: APPLIED to Render edplan_db / public. Verified on 2026-10-17.

Source: iaiacatalog.pdf, supplied by the user.
Catalog edition: 2025-2026; 95 PDF pages corresponding to printed pages 110-204.

## Scope

- Existing college record: Institute of American Indian Arts, Santa Fe, New Mexico.
- 28 degree, certificate and minor records.
- 319 course rows with explicit numeric codes and same-row credit cells.
- 195 ambiguous OCR course rows held out of the import.
- Course coverage is partial. Every program and course records that fact in metadata.
- Unknown lecture/lab hours, prerequisites, meeting times and semester assignments are left unset.
- Detailed requirement text is retained with PDF and printed-page references. Elective alternatives are not treated as required scheduled courses.
- The source is labeled 2025-2026, not the current academic year.

## Programs

| Program | Degree | Credits | Printed pages | Imported course rows |
| --- | --- | ---: | --- | ---: |
| Broadcast Journalism | Certificate | 24 | 120 | 6 |
| Business and Entrepreneurship | Certificate | 24 | 123 | 10 |
| Cinematic Arts and Technology | Associate of Fine Arts | 60 | 129 | 7 |
| Cinematic Arts and Technology | Bachelor of Fine Arts | 120 | 130 | 16 |
| Cinematic Arts and Technology | Minor | 24 | 131 | 6 |
| Computer Science | Certificate | 30 | 138 | 6 |
| Computer Science | Associate of Science | 60 | 138 | 7 |
| Computer Science | Bachelor of Science | 120 | 139 | 17 |
| Creative Writing | Associate of Fine Arts | 60 | 143 | 10 |
| Creative Writing | Bachelor of Fine Arts | 120 | 143, 144, 145 | 15 |
| Native American Studies | Associate of Arts | 60 | 149 | 6 |
| Indigenous Liberal Studies | Bachelor of Arts | 120 | 149, 150 | 13 |
| Indigenous Liberal Studies | Minor | 24 | 150 | 3 |
| Museum Studies | Associate of Fine Arts | 60 | 155 | 14 |
| Museum Studies | Bachelor of Fine Arts | 120 | 156 | 13 |
| Museum Studies | Certificate | 30 | 157 | 15 |
| Museum Studies | Minor | 24 | 157 | 12 |
| Native American Art History | Certificate | 30 | 161 | 14 |
| Native American Art History | Minor | 24 | 161 | 4 |
| Native American Art History | Bachelor of Arts | 120 | 162 | 26 |
| Performing Arts | Minor | 24 | 167 | 15 |
| Performing Arts | Associate of Fine Arts | 60 | 168 | 21 |
| Performing Arts | Bachelor of Fine Arts | 120 | 169, 170 | 35 |
| Studio Arts | Associate of Fine Arts | 60 | 175 | 4 |
| Studio Arts | Bachelor of Fine Arts | 120 | 176 | 10 |
| Studio Arts | Minor | 24 | 177 | 11 |
| Creative Writing | Master of Fine Arts | 48 | 194 | 3 |
| Cultural Administration | Master of Fine Arts | 46 | 196 | 0 |

## Needs clarification

- Creative Writing | Minor (printed page 145): Heading says 21 credits, departmental subtotal says 24 credits; excluded until authoritative clarification.
- Interactive Arts and Game Design | Minor (printed page 131): Section heading names Interactive Arts and Game Design, but subtitle names Cinematic Arts and Technology; excluded until program naming is confirmed.
- Studio Arts | Master of Fine Arts (printed page 196): Mentioned, but no degree credit total or curriculum is provided in this PDF excerpt.
- Art History and Community Wellness | Minor (printed page 113): Mentioned in the overview, but complete unambiguous standalone requirements are absent in this excerpt.

## Files and execution

- iaia-import-data.json: structured data, source SHA-256, page references, and every held OCR row.
- catalog-ocr.txt: searchable OCR of all 95 supplied pages; compare uncertain text against the original PDF.
- import_iaia.py: dry-run by default; requires --apply to commit.
- iaia-before-import.json: the original IAIA catalog record and its pre-import program/course records.
- dry-run.json / applied.json: execution evidence, including inserted record IDs.

The importer reads DATABASE_URL internally from the existing EdPlan environment file. Credentials are never stored in these artifacts.
It uses a single transaction, an IAIA-specific advisory lock, natural-key checks, and fingerprints to verify that other colleges remain unchanged.
No student, applicant, user, education-plan, or authentication records are read or modified.
No source changes are committed or pushed.

## Validation

- Dataset checks: 28 distinct program natural keys, positive credits, unique program/course pairs, source-page bounds, and explicit credit-row evidence.
- Anchor checks: CINE105 / 3 credits, CSAT202 / 3 credits, BUSN120 / 3 credits.
- Importer syntax: Python py_compile passed.
- Database transaction dry runs: both the row-wise and batched importer passed and rolled back cleanly.
- Applied row verification: all 28 programs and 319 course rows match the dataset; no duplicate program/course pairs.
- Repeat-run idempotency: zero new programs and zero new courses; trial transaction rolled back.
- Original IAIA profile: preserved, with catalog import metadata added under a separate key.
- Other college records: fingerprints unchanged.
- Source PDF SHA-256: independently rechecked.
- Student records: never accessed.

## Commands run

All Python commands used the bundled Codex Python runtime.

- python -m py_compile import_iaia.py
- python import_iaia.py (rolled-back validation, twice before application)
- python import_iaia.py --apply
- python import_iaia.py (post-import idempotency dry run: zero inserts)
- Independent read-only SQL verification of every IAIA program/course value and the original college profile.

Application source files were not changed. A full application test suite was not run; validation focused on the database import, source evidence, constraints, preservation, and idempotency.
