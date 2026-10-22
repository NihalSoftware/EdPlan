# Official WNMU public index snapshot

`catalog-index.json` is a compact projection of the visible program index at
https://catalog.wnmu.edu/content.php?catoid=8&navoid=612, read in the user's in-app
browser on 2026-10-16. Source selected label: `2025-2026 Catalog`.

`units` are `[official_heading_id, exact_name, category_groups]`; groups are
`[exact_category, [[official_poid, exact_program_title], ...]]`.
`universityPrograms` retains root-level General Education. Each program link
conformed to the recorded URL template. Snapshot contains 234 distinct official
program IDs. No detail page, credit total, description or rule is implied.

The projection preserves document order: a current `h4` sets the academic unit,
a `p` sets the category and its following `ul.program-list` supplies program links.
Root-level lists have no department. Multiple department headings may share the
same parent div; extracting all lists under `h4.parentElement` would incorrectly
assign other departments' programs. The tested snapshot uses document order.

Offline tests use this fixture; they do not download the live site. See
`docs/WNMU_CATALOG_IMPORT.md` for provenance, transfer verification, limitations
and safe application commands.
