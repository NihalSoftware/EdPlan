# Known Limitations

Generated: 2026-06-17

- Temporary 18-credit limit: validation uses `MAX_TERM_CREDITS = 18`. This is not yet institution-, program-, student-, or term-specific.
- Credit limit enforcement is validation-only: add/update plan-course endpoints expose the limit in metadata but do not block writes.
- Audit treats planned courses as completed: graduation audit has no transcript source and counts planned program courses toward progress.
- No transcript system: completed, in-progress, withdrawn, failed, repeated, and transferred courses are not modeled.
- No transfer credit system: external credits cannot be evaluated or applied to a plan.
- No substitutions or waivers: audit cannot account for advisor-approved exceptions.
- No schedule generation: terms, offerings, sections, and meetings are readable catalog data only.
- No agent layer: agent packages are placeholders and no agent workflow is implemented.
- No recommendation engine: the backend does not suggest courses, terms, programs, or schedules.
- No AI functionality: no model calls, AI orchestration, or AI-generated academic advice exists in the backend.
- Legacy education-plan routes are still present: `/api/users/education-plan*` persists JSON-backed payloads separately from normalized `ed_plans`.
- Email verification is disabled: verification endpoints return permissive stub responses.
- Graduation rules are course-list based: audit compares planned courses to program catalog courses, not a full degree-rule tree.
- Normalized scheduling persistence is not wired: live schema may include future plan schedule/section tables, but implemented routes do not use them.
