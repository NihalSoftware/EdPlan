# Official-source log

Observation date: 2026-10-22. Collection: bounded public reads through the web tool; no bulk crawl, authentication bypass, or private API.
Exact HTTP retrieval timestamps are not exposed by that tool; the observation date is recorded rather than invented seconds. Cached WNMU fixtures retain their original October 16 timestamps. Browser initialization failed (kernel asset path error), so no browser visual inspection is claimed.

Blocked responses were not treated as evidence of absent programs. Sources were reused through tool references to avoid duplicate downloads; site access restrictions were not bypassed. Custom User-Agent control is not available through the web tool; the reusable audit script performs no HTTP crawl. Any future crawler must use a descriptive User-Agent, approved hosts, robots/terms review and per-host delays (WNMU previously advertised 120 seconds).

## enmu — Eastern New Mexico University

- Discovery: https://www.enmu.edu/academics/academic-resources-services/catalogs-schedules-calendars/catalogs
- Resolved source: https://www.enmu.edu/images/academics/catalogs/undergrad-catalog-19-21.pdf
- Other source URLs: https://www.enmu.edu/images/academics/catalogs/graduate-catalog.pdf
- Edition: UG 2025-2027; graduate 2026-2028
- Access/coverage: PARTIAL
- Observation: 2026-10-22; exact HTTP retrieval time not exposed by web tool
- Location: UG PDF page 1/header; graduate PDF page 32/header
- Limits: Both editions established from document contents. Old-looking UG filename is not the edition. Full program/course comparison not performed.

## nmhu — New Mexico Highlands University

- Discovery: https://www.nmhu.edu/catalog/
- Resolved source: https://its.nmhu.edu/includes/onlinedocs/display.html?quicklink=8805
- Other source URLs: https://its.nmhu.edu/includes/onlinedocs/display.html?quicklink=8806
- Edition: UG and graduate 2025-2026
- Access/coverage: PARTIAL
- Observation: 2026-10-22; exact HTTP retrieval time not exposed by web tool
- Location: Official landing page University Catalogs, 2025-2026 heading and UG/graduate PDF links
- Limits: Latest editions listed on the checked landing page. Both PDFs accessible; not exhaustively parsed.

## nmt — New Mexico Institute of Mining and Technology

- Discovery: https://catalog.nmt.edu/
- Resolved source: https://catalog.nmt.edu/
- Other source URLs: https://catalog.nmt.edu/institute-reqs/nmt-degrees
- Edition: 2026-2027
- Access/coverage: PARTIAL
- Observation: 2026-10-22; exact HTTP retrieval time not exposed by web tool
- Location: Catalog homepage edition heading; Degrees Offered page
- Limits: Programs page uses dynamic labels. Official homepage also warns about transcription/errata; do not resolve conflicts by ignoring that notice.

## nmsu — New Mexico State University

- Discovery: https://catalogs.nmsu.edu/nmsu/
- Resolved source: https://catalogs.nmsu.edu/nmsu/
- Other source URLs: none established
- Edition: UNVERIFIED
- Access/coverage: SOURCE_BLOCKED
- Observation: 2026-10-22; exact HTTP retrieval time not exposed by web tool
- Location: Requested Las Cruces catalog root
- Limits: Automated response requires JavaScript robot verification. Not bypassed. Main-campus year/content not established in this audit.

## nnmc — Northern New Mexico College

- Discovery: https://catalog.nnmc.edu/
- Resolved source: https://catalog.nnmc.edu/
- Other source URLs: none established
- Edition: UNVERIFIED
- Access/coverage: SOURCE_BLOCKED
- Observation: 2026-10-22; exact HTTP retrieval time not exposed by web tool
- Location: Requested catalog root
- Limits: HTTP 403. Existing DB source years are reported separately; not used to invent latest official edition.

## unm — University of New Mexico

- Discovery: https://catalog.unm.edu/
- Resolved source: https://catalog.unm.edu/
- Other source URLs: none established
- Edition: 2026-2027
- Access/coverage: PARTIAL
- Observation: 2026-10-22; exact HTTP retrieval time not exposed by web tool
- Location: UNM 2026-2027 Catalog homepage heading
- Limits: Edition established; rendered extraction lacks complete program navigation. No full curriculum comparison.

## wnmu — Western New Mexico University

- Discovery: https://registrar.wnmu.edu/university-catalogs/
- Resolved source: https://registrar.wnmu.edu/university-catalogs/
- Other source URLs: https://catalog.wnmu.edu/content.php?catoid=8&navoid=612; https://catalog.wnmu.edu/preview_program.php?catoid=8&poid=2776&returnto=612
- Edition: 2025-2026
- Access/coverage: PARTIAL
- Observation: 2026-10-22; exact HTTP retrieval time not exposed by web tool
- Location: Registrar landing current catalog label; cached 2026-10-16 public DOM index and pharmacy curriculum
- Limits: Registrar still labels 2025-2026 current. Cached 234-entry index and 16-course Pharmacy roster compared with explicit capture dates; not newly recrawled course rules. Existing robots delay 120 seconds, no bulk crawl.

## cnm — Central New Mexico Community College

- Discovery: https://www.cnm.edu/students/services/catalog-resources
- Resolved source: https://www.cnm.edu/students/services/catalog-resources/documents/2026-2027-cnm-catalog-volume-58.pdf
- Other source URLs: none established
- Edition: 2026-2027
- Access/coverage: PARTIAL
- Observation: 2026-10-22; exact HTTP retrieval time not exposed by web tool
- Location: Official catalog resources 2026-2027 PDF link; Volume 58 PDF
- Limits: 449-page PDF accessible. Selected program/course evidence checked; no exhaustive inventory reconciliation.

## ccc — Clovis Community College

- Discovery: https://clovis.edu/publications/index.aspx
- Resolved source: https://clovis.edu/publications/2026%20-%202027%20Course%20Catalog%20-%20August%2018%20Addendums.pdf
- Other source URLs: none established
- Edition: 2026-2027
- Access/coverage: PARTIAL
- Observation: 2026-10-22; exact HTTP retrieval time not exposed by web tool
- Location: PDF cover and PDF page 3 state 2026-2027; landing current download link
- Limits: Old PDF metadata title says 2013-2015 but document content establishes 2026-2027. Full curriculum not parsed.

## luna — Luna Community College

- Discovery: https://luna.edu/resources/catalogs.php
- Resolved source: https://luna.edu/resources/catalogs.php
- Other source URLs: none established
- Edition: 2026-2027 (landing label)
- Access/coverage: PARTIAL
- Observation: 2026-10-22; exact HTTP retrieval time not exposed by web tool
- Location: Luna Community College Catalogs list: Catalog 2026 2027
- Limits: Year label established; dynamic document link/content not extracted, so full catalog remains unverified.

## mesalands — Mesalands Community College

- Discovery: https://www.mesalands.edu/o/mcc/page/catalog-schedules
- Resolved source: https://www.mesalands.edu/o/mcc/page/catalog-schedules
- Other source URLs: https://www.mesalands.edu/wp-content/uploads/MCC-Catalog-2025-2026-03-COM.pdf
- Edition: 2025-2026 indexed; current unverified
- Access/coverage: SOURCE_UNVERIFIED
- Observation: 2026-10-22; exact HTTP retrieval time not exposed by web tool
- Location: Official-domain search index suggests 2025-2026 PDF; direct PDF fetch returns 404
- Limits: Landing extraction lacks catalog body. Search-index evidence alone is not fresh source verification. Request current permitted PDF/export.

## nmjc — New Mexico Junior College

- Discovery: https://www.nmjc.edu/resource_service/catalog/index.aspx
- Resolved source: https://catalog.nmjc.edu/
- Other source URLs: none established
- Edition: 2026-2027
- Access/coverage: PARTIAL
- Observation: 2026-10-22; exact HTTP retrieval time not exposed by web tool
- Location: Current catalog homepage heading, linked from official college catalog landing
- Limits: Online program/course catalog navigation is accessible. Full curriculum not enumerated.

## nmmi — New Mexico Military Institute

- Discovery: https://www.nmmi.edu/academics/registrars-office/
- Resolved source: https://www.nmmi.edu/academics/registrars-office/
- Other source URLs: https://nmmi.catalog.acalog.com/
- Edition: UNVERIFIED
- Access/coverage: SOURCE_BLOCKED
- Observation: 2026-10-22; exact HTTP retrieval time not exposed by web tool
- Location: Registrar Course Catalog link to nmmi.catalog.acalog.com
- Limits: Official registrar identity/location established; catalog host retrieval failed. DB records label 2026-2027 but this is not independent source-year verification.

## sjc — San Juan College

- Discovery: https://catalog.sanjuancollege.edu/
- Resolved source: https://catalog.sanjuancollege.edu/
- Other source URLs: none established
- Edition: UNVERIFIED
- Access/coverage: SOURCE_BLOCKED
- Observation: 2026-10-22; exact HTTP retrieval time not exposed by web tool
- Location: Catalog root
- Limits: HTTP 403. No claim about official program absence or current edition.

## sfcc — Santa Fe Community College

- Discovery: https://www.sfcc.edu/college-catalog/
- Resolved source: https://www.sfcc.edu/college-catalog/
- Other source URLs: https://catalog.sfcc.edu/
- Edition: UNVERIFIED
- Access/coverage: SOURCE_BLOCKED
- Observation: 2026-10-22; exact HTTP retrieval time not exposed by web tool
- Location: Official college catalog landing
- Limits: HTTP 403. Historical project data is not treated as latest catalog evidence.

## senmc — Southeast New Mexico College

- Discovery: https://catalog.senmc.edu/
- Resolved source: https://catalog.senmc.edu/
- Other source URLs: https://catalog.senmc.edu/programs
- Edition: 2026-2027
- Access/coverage: PARTIAL
- Observation: 2026-10-22; exact HTTP retrieval time not exposed by web tool
- Location: Current catalog homepage edition; Programs page
- Limits: Institution is independent, not NMSU-Carlsbad. Dynamic Programs extraction has no inventory rows; not evidence of zero programs.

## dine — Diné College

- Discovery: https://www.dinecollege.edu/admissions/course-catalog/
- Resolved source: https://www.dinecollege.edu/wp-content/uploads/2026/10/2026-27DC-Catalog_MasterDraft-9.10.26.pdf
- Other source URLs: none established
- Edition: 2026-2027
- Access/coverage: PARTIAL
- Observation: 2026-10-22; exact HTTP retrieval time not exposed by web tool
- Location: Official Course Catalog landing current link; Tsaile/Shiprock institutional relationship text
- Limits: Officially linked PDF filename includes MasterDraft: approval/finality needs human review. Tsaile is the administrative center; Shiprock is not a separate parent institution.

## iaia — Institute of American Indian Arts

- Discovery: https://iaia.edu/admissions/college-catalog/
- Resolved source: https://iaia.edu/admissions/college-catalog/
- Other source URLs: none established
- Edition: 2026-2027 (landing label)
- Access/coverage: PARTIAL
- Observation: 2026-10-22; exact HTTP retrieval time not exposed by web tool
- Location: Current IAIA Catalog: NEW 2026-2027 link
- Limits: Current edition explicitly listed. PDF retrieval failed; content comparison remains unverified.

## ntu — Navajo Technical University

- Discovery: https://www.navajotech.edu/faculty-staff/policies-docs/
- Resolved source: https://www.navajotech.edu/wp-content/uploads/2026/08/2026-27-UndergraduateCatalog-080326.pdf
- Other source URLs: https://www.navajotech.edu/wp-content/uploads/2026/01/2025-2026_Graduate-Catalog-Update_4-18-2025.pdf
- Edition: UG 2026-2027; graduate 2025-2026
- Access/coverage: PARTIAL
- Observation: 2026-10-22; exact HTTP retrieval time not exposed by web tool
- Location: Official Policies+Docs catalog links; UG contents academic-year line
- Limits: UG and graduate editions differ and must not be silently combined. Full inventory comparison not performed.

## sipi — Southwestern Indian Polytechnic Institute

- Discovery: https://www.sipi.edu/apps/pages/Catalog
- Resolved source: https://4.files.edl.io/5a02/08/05/26/202024-20015adf-0052-4850-bffb-b464a67a8f78.pdf
- Other source URLs: https://4.files.edl.io/7ff9/03/31/23/211213-e5d9e017-643b-4826-af53-95d0faae23c6.pdf
- Edition: 2026-2027
- Access/coverage: PARTIAL
- Observation: 2026-10-22; exact HTTP retrieval time not exposed by web tool
- Location: Official page navigation Academic Catalog link; current PDF pages 2 and 4
- Limits: Body still links 2023-2024, but navigation links 2026-2027 PDF. Current PDF explicitly effective July 1 2026 to June 30 2027. Official name is Southwestern, not stored Southwest.
