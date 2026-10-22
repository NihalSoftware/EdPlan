# NMT official-source test fixtures

The four JSON fixtures are academically relevant subsets of public HTML SSR state
retrieved on 2026-10-15 from `https://catalog.nmt.edu/`:

- `/programs/BS-BIOLOGY`
- `/programs/BS-BMS`
- `/programs/MS-BIOLOGY`
- `/courses/BIOL2110L`

Each fixture includes the exact official source URL, retrieval timestamp, and SHA-256
of the complete cached HTML response. Editing identities and department staff/contact
details are excluded. Original academic wording, including apparent spelling errors,
is retained. These are not synthetic curriculum records or production seed data.

Tests read these saved files, never the live website. Generate them only from an
already reviewed local cache using `python -m scripts.nmt_catalog.fixtures`.

BIOL2610L was **not** retrieved successfully: its live page returned HTTP 405.
The separate timing test in `test_nmt_catalog.py` uses explicitly synthetic rule
nodes. The supplied PDF's printed page 106 independently states the corresponding
pre-or-corequisite and corequisite, but dual-source verification remains outstanding.

The fixtures do not cover every program category; no claim of complete catalog
coverage or publication approval is made.
