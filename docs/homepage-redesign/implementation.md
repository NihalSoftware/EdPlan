# edplanAI homepage redesign — October 22, 2026

## Scope and decisions

Implemented the supplied homepage reference in the existing React/Vite application, without a new framework or dependency. Following user feedback, the original sidebar navigation and original mobile header/drawer are restored unchanged. The homepage retains navy typography, teal actions, warm card borders, a generated New Mexico-inspired desert background, comparison badges, a Northern NM planner card and a compact regional footer. Homepage styling is scoped to `HomePage.css`.

The reference-style top navigation was removed at the user's request. `/home` uses the original `AppLayout` and `Navigation` components; their links, branding and behavior have not been changed. Existing route and authentication functions are reused.

The requested “29” campus copy is supplied by the design brief. This redesign does not certify database coverage, add rankings, or alter institutional/course data. The background is generated, not a documentary photo of a named New Mexico location. See `asset-provenance.md` for the exact prompt and production asset path.

## Modified files

- `ChatbotUI/src/pages/HomePage.jsx`: hero, cards, footer, accessible disclaimer and page title; no replacement navigation.
- `ChatbotUI/src/pages/HomePage.css`: page-scoped colors, typography, cards, breakpoints, focus indicators and reduced-motion behavior. Primary teal is slightly darker than the suggested swatch to maintain white-text contrast.
- `ChatbotUI/src/App.jsx`: restored `/home` inside the original sidebar shell; all route paths retained.
- `ChatbotUI/src/utils/homeNavigation.js`: allowlisted post-login destinations and Northern NM shortcut mapping.
- `ChatbotUI/src/pages/LoginPage.jsx`: preserve existing API/storage/authentication behavior; honor only the two approved homepage return destinations. Legacy default redirect remains unchanged.
- `ChatbotUI/src/pages/EducationPlanEditPage.jsx`: translate the explicit `college=nnmc` shortcut into an initial university prop.
- `ChatbotUI/src/components/education/EducationPlanEditor.jsx`: accept that optional university override, and do not restore another college's draft into the shortcut. Normal entry points retain their stored selection. Prerequisite/corequisite logic and save endpoints are unchanged.
- `ChatbotUI/public/assets/new-mexico-desert.webp`: self-hosted, optimized 1536 × 1024 landscape (380,272 bytes).
- `ChatbotUI/tests/homeNavigation.test.mjs`: dependency-free Node tests for CTA destinations and open-redirect protection.

## Functionality preserved

No backend, database, environment configuration, API contract, academic rule or existing saved-plan record was changed. Login and signup use the existing forms/services. Successful login from the comparison CTA returns to `/compare`; the planner CTA returns to `/educationplan?college=nnmc`. Signup uses the existing shared login form, retaining the destination query as it switches back to login. Authenticated homepage visitors get direct workflow links. No real credentials were entered and no account or plan was created for testing.

## Verification

| Check | Result / evidence |
|---|---|
| Existing baseline lint | Passed before changes |
| Production build | `npm run build` passed after the asset was installed |
| Final lint | `npm run lint` passed |
| Navigation unit tests | `node --test tests/homeNavigation.test.mjs`: 6 passed |
| Patch whitespace | `git diff --check` passed; Git emitted only its existing LF/CRLF notice |
| Responsive overflow | Live DOM measurements at 320, 375, 390, 768, 1024 and 1440px: no horizontal document overflow |
| Original navigation restored | Existing desktop sidebar verified; original mobile drawer opens and closes using its Home link. No replacement top navigation remains. No horizontal overflow at 320, 375, 768, 1024 or 1335px; one main landmark. |
| Disclaimer | Collapsed initially; mouse expansion, Enter collapse and Space expansion verified; full supplied text appears; `aria-expanded` and `aria-hidden` update |
| Guest comparison CTA | Opens `/login?next=%2Fcompare` and the existing login form |
| Registration CTA | Opens `/signup?next=%2Fcompare` and the existing registration form |
| Guest planner CTA | Opens login with the Northern NM planner return destination |
| Northern NM shortcut | Planner renders Northern New Mexico College selected; no save action taken |
| Background serving | Local asset returned HTTP 200, `image/webp`, 380,272 bytes |

Browser verification used the in-app browser through the computer/browser tools. Current screenshot: `navigation-restored.jpg`. Earlier screenshots `desktop.jpg`, `mobile.jpg` and `mobile-disclaimer.jpg` document the initial design before the user requested original-navigation restoration. These show the real local application, not a mockup. The pre-existing third-party chat widget remains present and may overlay a corner of the page.

## Remaining limits

- The local backend is not listening on port 8000 (`Test-NetConnection` returned false). The planner displayed its existing “Unable to load program catalog” state. Catalog loading, saving, real sign-in and the authenticated API/database flow are therefore not certified end-to-end. No mock data or fake login was substituted.
- The production build reports the existing large application chunk (approximately 743 kB minified) and stale Browserslist data. No dependency upgrades or unrelated route/bundle refactors were made.
- No automated accessibility certification or Core Web Vitals improvement is claimed. Keyboard interaction, semantics, focus styling, responsive layout and reduced-motion CSS were checked within this scope; a complete WCAG audit remains separate work.
- Existing generic login defaults to the legacy `/eduai` URL, which the app routes back to home. Only explicit homepage CTAs receive the new allowlisted return handling.

## Re-run checks

From `ChatbotUI`:

```powershell
npm run build
npm run lint
node --test tests/homeNavigation.test.mjs
```

For live data-flow testing, start the project's existing backend using its normal configuration, then verify the login and catalog flows with an approved test account. No deployment was performed.
