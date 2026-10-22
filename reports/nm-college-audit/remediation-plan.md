# Proposed remediation — NOT executed

No SQL, migration, import, merge, deletion, or application fix below has been applied.

## Priorities and approval gates

1. **P1: parent identities.** Propose a Diné parent at Tsaile, Arizona, retaining Shiprock as its NM service location. Review the two existing center IDs before introducing parent/campus links. Resolve UNM's two parent candidates through reference counts and a user-approved canonical-ID/alias map; do not delete either ID or move saved plans automatically. Correct SIPI's official spelling in a separately approved identity-only update.
2. **P1: recover catalog provenance and schema history.** Reconcile live Alembic 0014 with local sources through 0010 from the authoritative migration history. Do not stamp or reset. Document DB environment ownership, obtain a dedicated read-only role/replica, then establish per-record edition, source ID/URL and retrieval timestamp. Unknown year is not the latest year.
3. **P1: version-scoped missing content.** WNMU's October 16 same-edition index has unmatched official IDs (see CSV). Review for source-URL/name matches before proposing insertion; an unmatched ID alone is not proof that no equivalent row exists. Empty catalog rosters (including NMMI) require permitted official sources, not synthetic courses. Do not mark programs absent from one crawl inactive.
4. **P1: planning semantics.** Model requirement groups/alternatives, grade thresholds, placement, admission and concurrent exceptions without flattening OR into AND. Keep exact narratives. Separate planned from completed credits in graduation feedback. Validate alternatives and removal guards using synthetic fixtures before any release; do not change academic rules based on this audit alone.
5. **P2: source conflicts and suspicious credits.** Ask SIPI's registrar to resolve code differences between requirement tables and suggested sequences. Review NMT's repeated 120-credit values across unlike awards against exact year/credential pages. CNM Cybersecurity versus current CIS AAS concentration is a review suggestion, not a safe match or approved 64-to-62 correction.
6. **P2: sources not fully accessible.** Obtain permitted exports/PDFs for NMSU Las Cruces, NNMC, NMMI, San Juan and SFCC; a current Mesalands document; and accessible IAIA/Luna/dynamic inventories. Finish program, course, credit and dependency comparisons for every accessible institution. No full curriculum certification is issued here.
7. **P2: type/provenance boundaries.** Live numeric credits can include fractions but ORM/API use integers. Review a backward-compatible Decimal/range representation and serialization contract. Catalog departments exist but course-department bridge coverage is empty; do not infer department ownership from a shared code alone.

## Safe change design (requires a later explicit approval)

- Establish target institution, exact catalog year, official ID/code and parent scope. High-confidence ID/code/URL matches can be staged; exact-name and fuzzy cases remain review-only. Never match globally on course code.
- Generate a deterministic dry-run diff and immutable evidence hashes; report inserts, field updates, relationship changes and not-found rows separately. Preserve valid nonempty values and all historical curricula.
- Take an approved backup/snapshot and verify restore access. Rehearse against a disposable copy with masked/synthetic student data. The audit itself did not access student row contents.
- For approved batches only: use parameterized SQL/ORM and one bounded transaction, advisory/optimistic concurrency protection, expected-old-value predicates, FK checks and uniqueness scoped to institution/year/program as appropriate. Before values change, persist old/new values, table/record IDs, run ID, match/confidence, source URL and timestamp in the audit trail. Abort on unexpected counts or concurrent drift.
- Saved plans may reference program/course UUIDs. Prefer additive catalog-version records and stable aliases; avoid in-place cross-year replacement or cascading deletion. Report reference counts without exporting personal rows; ask for approval before remapping any plan.
- Roll back the transaction on validation failure. After commit, restore only the exact audited fields/IDs with expected-new-value predicates in a separately approved compensating transaction; do not overwrite later edits. Verify API serialization and planner behavior with existing plus new fixture tests.

## Completion gate for a follow-up audit

All 20 parents reconciled; every source edition established or explicitly blocked; full official program inventories matched; required/selectable course groups and narrative dependencies reconciled; source conflicts resolved; dry-run reviewed; existing saved-plan identities preserved. Row counts and selected passing fields are not completeness proof.
