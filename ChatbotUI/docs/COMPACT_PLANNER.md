# Compact education-plan update

Reference inspected: https://www.studentspace.ai/educationplan

Computer Use read the reference's live accessibility tree. Native screenshot capture timed out, so isolated headless Edge screenshots at 1335px and 390px provided the visual reference.

## Changes

- Compact heading and explanatory text, without duplicate headings or nested page padding.
- University context, program selector, and Save Your Plan in one desktop control row.
- Year filter, course/credit/prerequisite summaries, semester selector, and Add Semester in a compact wrapping toolbar.
- Course catalog collapsed into a narrow right-side rail on desktop, or a disclosure above the plan on smaller screens.
- Two-column semester cards when the available plan width permits; one column on phones or when the catalog leaves insufficient space.
- Per-semester Add Course opens the catalog and selects the correct target semester. Existing course validation and prerequisite behavior remain in use.
- Career filters use a compact panel with labeled controls and no empty summary row. Program summaries still appear when selected.

No backend, catalog data, API payload, save handler, prerequisite rule, or existing navigation route was replaced.

## Verification

The verification skill guided separation of rendered frontend checks from live backend checks.

`scripts/compact-ui-check.mjs` runs at 375, 390, 768, 1280, 1335, and 1920px. It uses isolated browser-only API fixtures derived from existing bundled catalog JSON; it does not write to PostgreSQL or change production data.

Checks cover semester additions continuing Fall/Spring, catalog disclosure, per-semester course addition, local saving, one Save Your Plan action, compact career-filter height, document overflow, and uncaught browser errors. Screenshots are saved to `artifacts/compact-ui/` and ignored by Git.

Run with an existing Playwright installation and browser:

```powershell
$env:PLAYWRIGHT_MODULE = 'C:\path\to\node_modules\playwright'
$env:BROWSER_EXECUTABLE = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
$env:UI_BASE_URL = 'http://127.0.0.1:5173'
node scripts/compact-ui-check.mjs
```

`--reference` captures the public reference instead. No runtime dependencies are added.

Limitations: no local backend API was available during checks, so real account/remote database saving is not claimed as verified. The existing third-party chat widget is unchanged. Existing build chunk-size warnings remain outside this scoped layout update.
