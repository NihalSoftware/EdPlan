# Planning Validation Design

## Goal

Design the future Planning Validation domain for normalized planning. This document is architecture and requirements only. It does not implement validation logic, create routes, modify backend code, or define migrations.

Validation should evaluate persisted or candidate plans built from:

* `ed_plans`
* `plan_courses`

The validator should use catalog, calendar, and scheduling data that already exists, and should leave future student-history tables as explicit dependencies to be added later.

## Scope

In scope:

* Prerequisite validation.
* Corequisite validation.
* Term credit validation.
* Duplicate course validation.
* Validation severity and result shape.
* Future API proposals.
* Database tables and queries needed by the eventual implementation.

Out of scope for this document:

* Backend implementation.
* API route creation.
* Migrations.
* Persistence changes.
* Graduation audit implementation.
* Section schedule conflict validation, except as a future extension.

## Architecture

Planning validation should live as a read-only planning-domain service. It should not mutate `ed_plans`, `plan_courses`, catalog data, or future student-history data.

Recommended components:

* `PlanningValidationService`: Orchestrates validation for a full plan or candidate course operation.
* `ValidationContextBuilder`: Loads plan, term, course, prerequisite, corequisite, credit, completion, waiver, and substitution data into a stable in-memory snapshot.
* Rule validators:
  * `DuplicateCourseValidator`
  * `PrerequisiteValidator`
  * `CorequisiteValidator`
  * `CreditLimitValidator`
* `ValidationIssueFactory`: Normalizes issue codes, severities, messages, and related entity references.

The validation engine should return all relevant issues instead of stopping after the first error. Clients can still block saves when any issue has `severity = "error"`.

Candidate result shape:

```json
{
  "is_valid": false,
  "issues": [
    {
      "severity": "error",
      "code": "PREREQUISITE_NOT_SATISFIED",
      "message": "Course CS 201 requires CS 101 before Fall 2027.",
      "plan_course_id": "uuid",
      "course_id": "uuid",
      "planned_term_id": "uuid",
      "related_course_ids": ["uuid"],
      "metadata": {}
    }
  ],
  "summary": {
    "error_count": 1,
    "warning_count": 0,
    "recommendation_count": 0
  }
}
```

## 1. Prerequisite Validation

### Definition

A prerequisite is satisfied when the student has completion-equivalent evidence for the required prerequisite before the dependent course begins.

Completion-equivalent evidence may come from:

* A previously completed course from a future completed-course table.
* A transfer, placement, test-credit, waiver, or substitution record from future tables.
* A course planned in an earlier term of the same plan, if the product adopts projected-plan semantics.

Recommended first validation semantics:

* For long-range plan validation, a prerequisite course planned in an earlier term should count as projected satisfaction when the earlier term ends before the dependent term starts.
* For transcript-only validation, only completed-course and approved-equivalency records should count.
* The validation response should distinguish actual satisfaction from projected satisfaction in metadata once completed-course tables exist.

Current catalog representation:

* `course_prerequisites` stores direct course-to-course requirements.
* The current table supports an implicit "all of these prerequisite rows are required" model.
* It does not yet support grouped logic such as "Course A or Course B", minimum grades, test scores, placement rules, or non-course prerequisites.

### Cross-Term Checking

Validation should compare academic terms by dates, not by term names. `academic_terms.start_date` and `academic_terms.end_date` should define ordering.

Recommended rules:

* A prerequisite planned in the same term as the dependent course does not satisfy a prerequisite.
* A prerequisite planned after the dependent course does not satisfy a prerequisite.
* A prerequisite planned in an earlier term satisfies projected sequencing only when the prerequisite term ends before the dependent term starts.
* If either course has no `planned_term_id`, validation should report a warning or error based on the operation mode. This is an open policy decision.
* In-progress courses should not satisfy prerequisites for a future dependent course unless their term ends before the dependent term starts.

### Previously Completed Courses

Previously completed courses should be modeled outside `plan_courses` in a future student-history table. They should be loaded by `ed_plans.user_id` and treated as already satisfied if their completion date or completion term is before the dependent term.

Recommended behavior:

* A completed course should satisfy the matching prerequisite course regardless of whether it appears in `plan_courses`.
* Transfer, test, placement, waiver, and substitution records should satisfy prerequisites only when they explicitly map to the required course or requirement.
* `plan_courses.status = 'Completed'` can be treated as temporary plan-local evidence during early development, but it should not become the long-term source of truth for transcript history.

### Required Queries

Plan context:

```sql
SELECT ep.plan_id, ep.user_id, ep.university_id, ep.program_id
FROM ed_plans ep
WHERE ep.plan_id = :plan_id;
```

Plan courses with term order:

```sql
SELECT
  pc.id AS plan_course_id,
  pc.course_id,
  pc.planned_term_id,
  pc.status,
  c.course_code,
  c.course_name,
  c.credits,
  at.start_date,
  at.end_date
FROM plan_courses pc
JOIN courses c ON c.course_id = pc.course_id
LEFT JOIN academic_terms at ON at.term_id = pc.planned_term_id
WHERE pc.plan_id = :plan_id;
```

Prerequisite relationships for all courses in the plan:

```sql
SELECT cp.course_id, cp.prerequisite_course_id
FROM course_prerequisites cp
WHERE cp.course_id = ANY(:course_ids);
```

Future completed-course evidence:

```sql
SELECT course_id, status, grade, completed_at, completion_term_id
FROM completed_courses
WHERE user_id = :user_id
  AND status IN (:completion_statuses);
```

Future equivalency evidence:

```sql
SELECT source_course_code, equivalent_course_id, credits, effective_date
FROM transfer_credits
WHERE user_id = :user_id;

SELECT course_id, waiver_type, approved_at, expires_at
FROM waivers
WHERE user_id = :user_id;

SELECT original_course_id, substitute_course_id, approved_at
FROM substitutions
WHERE user_id = :user_id;
```

### Open Questions

* Should earlier planned courses count as projected prerequisite satisfaction for save validation?
* What statuses count as completed?
* Are minimum grades required for prerequisite satisfaction?
* How should failed, withdrawn, incomplete, or repeated attempts be treated?
* How should "Course A or Course B" prerequisite groups be represented?
* Can transfer, placement, test credit, waiver, or substitution records satisfy all prerequisite types?
* Should missing `planned_term_id` be an error, warning, or allowed draft state?
* Should prerequisite validation run against inactive academic terms?

## 2. Corequisite Validation

### Definition

A corequisite is satisfied when the required corequisite course is scheduled in the same academic term as the associated course.

Current catalog representation:

* `course_corequisites.course_id` identifies the course with the requirement.
* `course_corequisites.corequisite_course_id` identifies the required same-term companion course.
* The relationship should be treated as directed unless business rules require symmetric storage.

Recommended rules:

* A required corequisite must appear in `plan_courses` for the same `plan_id`.
* The associated course and corequisite must have the same non-null `planned_term_id`.
* A previously completed course should not automatically satisfy a corequisite under current confirmed rules.
* Corequisites are not prerequisites. Do not satisfy them with previous completion unless a future waiver or policy explicitly allows it.

### Same-Term Requirements

Validation should group plan courses by `planned_term_id`.

For each planned course:

1. Load required corequisite rows where `course_corequisites.course_id = plan_course.course_id`.
2. Confirm every `corequisite_course_id` is present in the same term.
3. Emit a `COREQUISITE_NOT_SCHEDULED_SAME_TERM` error for each missing companion.
4. Emit a separate issue if the companion exists in a different term.

If either side lacks a `planned_term_id`, the validator cannot prove same-term enrollment. Recommended default is an error for save validation and a warning for draft validation.

### Automatic Corequisite Addition Considerations

Automatic corequisite addition should be an operation-level concern, not a side effect of validation.

Recommended flow for a future add-course operation:

1. Build a candidate plan including the requested course.
2. Identify required corequisites for the requested course.
3. Add missing corequisites to the same candidate term only if the operation explicitly supports auto-add.
4. Run duplicate validation on the candidate set.
5. Run prerequisite, corequisite, and credit validation against the candidate set.
6. Save only if no validation errors remain.

The response should identify auto-added courses:

```json
{
  "auto_added_courses": [
    {
      "course_id": "uuid",
      "reason": "required_corequisite",
      "required_by_course_id": "uuid"
    }
  ]
}
```

Validation itself should report missing corequisites. It should not silently repair the plan.

### Required Queries

Corequisite relationships for all courses in the plan:

```sql
SELECT cc.course_id, cc.corequisite_course_id
FROM course_corequisites cc
WHERE cc.course_id = ANY(:course_ids);
```

Same-term plan-course lookup:

```sql
SELECT pc.course_id, pc.planned_term_id
FROM plan_courses pc
WHERE pc.plan_id = :plan_id;
```

Candidate auto-add lookup:

```sql
SELECT c.course_id, c.course_code, c.course_name, c.credits
FROM courses c
WHERE c.course_id = ANY(:corequisite_course_ids);
```

### Open Questions

* Are corequisite rows directed or should every pair be treated symmetrically?
* Can a previously completed course ever satisfy a corequisite?
* Should corequisite auto-add run on add only, or also on move, plan generation, and bulk import?
* If moving one course separates a corequisite pair, should the move fail or move the companion automatically?
* Should missing corequisites be reported on the associated course only, the companion course only, or both?
* Are optional co-enrollment suggestions represented separately from required corequisites?

## 3. Credit Validation

### Current Temporary Rule

The current temporary rule is:

```text
MAX_TERM_CREDITS = 18
```

The existing planning service exposes this limit in response metadata, but validation is not implemented yet.

### Validation Strategy

For each plan term:

1. Sum `courses.credits` for all `plan_courses` in the term.
2. Compare the sum to the applicable maximum.
3. Emit `TERM_CREDIT_LIMIT_EXCEEDED` when total credits exceed the maximum.

Recommended first implementation:

* Use the temporary 18-credit limit through a credit-limit provider so the constant can later be replaced without rewriting validator logic.
* Treat over-limit terms as errors when validation is used as a save gate.
* Return the term credit total, limit, and overage in issue metadata.
* Do not count courses without a `planned_term_id` in term totals; report those separately as unscheduled-course issues if the product chooses to validate draft completeness.

Example issue metadata:

```json
{
  "term_credits": 21,
  "max_term_credits": 18,
  "over_by": 3
}
```

### Future State

Credit limits should come from a database table rather than a constant.

Likely future table: `term_credit_limits`

Candidate fields:

* `id`
* `university_id`
* `program_id`
* `term_id`
* `term_type`
* `min_credits`
* `max_credits`
* `student_level`
* `effective_start_date`
* `effective_end_date`
* `is_active`

The validator should choose the most specific active limit:

1. Student-specific approved overload, if supported.
2. Program and exact term.
3. Program and term type.
4. University and term type.
5. Global default.

### Future Migration Path

Recommended path:

1. Introduce a `CreditLimitProvider` abstraction while still returning 18.
2. Add `term_credit_limits` in a later migration.
3. Backfill a default active max of 18 credits.
4. Read from `term_credit_limits` behind the provider.
5. Add support for overrides, minimum credits, and term-type-specific limits.
6. Remove direct usage of `MAX_TERM_CREDITS` from validation once DB limits are authoritative.

### Required Queries

Current term credit totals:

```sql
SELECT
  pc.planned_term_id,
  SUM(c.credits) AS total_credits
FROM plan_courses pc
JOIN courses c ON c.course_id = pc.course_id
WHERE pc.plan_id = :plan_id
  AND pc.planned_term_id IS NOT NULL
GROUP BY pc.planned_term_id;
```

Future applicable credit limits:

```sql
SELECT *
FROM term_credit_limits
WHERE is_active = true
  AND (
    program_id = :program_id
    OR university_id = :university_id
    OR program_id IS NULL
  )
  AND (
    term_id = :term_id
    OR term_type = :term_type
    OR term_id IS NULL
  )
ORDER BY specificity DESC
LIMIT 1;
```

Future student overload approvals:

```sql
SELECT approved_max_credits, approved_at, expires_at
FROM credit_overrides
WHERE user_id = :user_id
  AND term_id = :term_id
  AND status = 'Approved';
```

### Open Questions

* Should exceeding 18 credits block save immediately or start as a warning during rollout?
* Are there minimum credit requirements per term?
* Are credit limits different for summer, winter, graduate, undergraduate, part-time, or full-time students?
* Can advisors approve credit overloads?
* Should in-progress and completed plan courses count toward planned term load?
* Should labs, zero-credit courses, or variable-credit courses receive special handling?

## 4. Duplicate Course Validation

### Current Rule

Duplicate courses are not currently allowed in a normalized plan.

Reason:

* `plan_courses` has a unique constraint on `(plan_id, course_id)`.

Validation should detect duplicates before attempting persistence so clients receive a domain-level issue instead of only a database constraint failure.

Recommended issue:

```text
DUPLICATE_COURSE_IN_PLAN
```

Severity:

* `error`

### Retake Considerations

Retakes are not supported by the current `plan_courses` shape because the same `course_id` cannot appear twice in one plan.

Future retake support will need to answer:

* Whether a failed or withdrawn course should remain in the plan history.
* Whether a repeated course should count once or multiple times toward credits.
* Whether grade replacement, grade averaging, or best-attempt rules apply.
* Whether a course can be repeated for credit by catalog policy.
* Whether retakes should be represented as multiple `plan_courses` rows, a separate attempt table, or student transcript history only.

### Future Support for Repeated Courses

Likely future options:

* Add `attempt_number` or `repeat_group_id` to `plan_courses` and replace the `(plan_id, course_id)` uniqueness rule.
* Add a `plan_course_attempts` table that models repeated attempts while keeping a stable course reference.
* Add catalog-level repeatability rules, such as `course_repeat_rules`.
* Use future `completed_courses` as transcript history and keep `plan_courses` focused on future intended enrollment.

### Required Queries

For a persisted plan:

```sql
SELECT course_id, COUNT(*) AS occurrences
FROM plan_courses
WHERE plan_id = :plan_id
GROUP BY course_id
HAVING COUNT(*) > 1;
```

For a candidate add-course operation:

```sql
SELECT 1
FROM plan_courses
WHERE plan_id = :plan_id
  AND course_id = :course_id;
```

For future repeat rules:

```sql
SELECT course_id, is_repeatable, max_attempts, max_repeat_credits
FROM course_repeat_rules
WHERE course_id = ANY(:course_ids);
```

### Open Questions

* Are duplicate courses ever allowed in a draft plan?
* Should retakes be planned before transcript outcomes are known?
* Which statuses require or allow retakes?
* Do repeated attempts count toward term credit load?
* How should repeated courses affect prerequisite satisfaction?
* Should course substitutions create apparent duplicates that are actually valid?

## 5. Validation Severity Model

Validation should support three severities.

### Errors

Errors are blocking. A plan with one or more errors must not be saved when validation is used as a save gate.

Examples:

* `DUPLICATE_COURSE_IN_PLAN`: The same course appears more than once without an approved repeat rule.
* `PREREQUISITE_NOT_SATISFIED`: A dependent course is scheduled before its required prerequisite.
* `COREQUISITE_NOT_SCHEDULED_SAME_TERM`: A required corequisite is missing from the same term.
* `TERM_CREDIT_LIMIT_EXCEEDED`: A term exceeds the applicable maximum credit limit.
* `UNKNOWN_COURSE_REFERENCE`: A candidate request references a course that does not exist or is outside the plan program.

### Warnings

Warnings are informational and should not block save.

Examples:

* `PREREQUISITE_PROJECTED_NOT_COMPLETED`: A prerequisite is planned in an earlier term but is not yet completed in transcript history.
* `UNSCHEDULED_COURSE_IN_PLAN`: A course has no `planned_term_id`.
* `COURSE_NOT_OFFERED_IN_TERM`: A planned course has no matching `course_offerings` row for that term, if availability validation is enabled.
* `INACTIVE_TERM_USED`: A planned term is marked inactive.

### Recommendations

Recommendations are planner suggestions. They are not validation failures.

Examples:

* `RECOMMENDED_SEQUENCE_DEVIATION`: A course is valid but differs from the catalog recommended year or semester.
* `BALANCE_TERM_LOAD`: Move a course from a heavy term to a lighter term.
* `ADD_COREQUISITE_TOGETHER`: Suggest adding a required corequisite when previewing a course before save.
* `CONSIDER_EARLIER_AVAILABLE_TERM`: Suggest an earlier term when prerequisites are already satisfied.

### Severity Rules

* `is_valid` should be `false` only when at least one error exists.
* Warnings and recommendations should not make `is_valid` false.
* The same condition should not be emitted at multiple severities in the same validation mode.
* Issues should include machine-readable codes and stable entity references.
* User-facing text should be generated consistently from issue codes and metadata.

## 6. Validation Execution Order

Recommended order:

1. Duplicate checks.
2. Prerequisite checks.
3. Corequisite checks.
4. Credit checks.

Rationale:

* Duplicate checks run first because duplicate course rows make prerequisite and corequisite references ambiguous.
* Prerequisite checks run before corequisite checks because they validate cross-term ordering and can identify courses that are fundamentally misplaced.
* Corequisite checks run before credit checks because future auto-add workflows can change the final course set for a term.
* Credit checks run after the course set is stable so term totals reflect all planned and automatically added courses.

For a future auto-add operation, the operation flow should be:

1. Build candidate plan.
2. Add required corequisites if the operation supports auto-add.
3. Run duplicate checks.
4. Run prerequisite checks.
5. Run corequisite checks.
6. Run credit checks.
7. Save only if there are no errors.

## 7. API Design Proposal

These are future endpoint proposals only. Do not implement them as part of this design task.

### Validate Persisted Plan

```text
POST /api/plans/{plan_id}/validate
```

Purpose:

* Validate the current persisted plan in `ed_plans` and `plan_courses`.

Candidate request:

```json
{
  "mode": "save",
  "include_recommendations": true
}
```

Candidate response:

```json
{
  "success": true,
  "data": {
    "plan_id": "uuid",
    "is_valid": false,
    "issues": [],
    "summary": {
      "error_count": 0,
      "warning_count": 0,
      "recommendation_count": 0
    }
  }
}
```

### Validate Candidate Course Operation

```text
POST /api/plans/{plan_id}/validate-course
```

Purpose:

* Validate a proposed add, move, remove, or status update without saving it.

Candidate request:

```json
{
  "operation": "add",
  "course_id": "uuid",
  "planned_term_id": "uuid",
  "status": "Planned",
  "allow_corequisite_auto_add": true
}
```

Candidate response:

```json
{
  "success": true,
  "data": {
    "is_valid": true,
    "issues": [],
    "candidate_changes": {
      "auto_added_courses": []
    }
  }
}
```

### Validate Draft Plan

```text
POST /api/plans/validate-draft
```

Purpose:

* Validate an unsaved client-side draft. This is useful for planner generation, bulk editing, or previews.

Candidate request:

```json
{
  "user_id": 123,
  "university_id": "uuid",
  "program_id": "uuid",
  "courses": [
    {
      "course_id": "uuid",
      "planned_term_id": "uuid",
      "status": "Planned"
    }
  ]
}
```

### API Open Questions

* Should invalid plans return `success: true` with validation issues or an HTTP error?
* Should `mode` change severity, such as `draft`, `save`, `advisor_review`, or `generation`?
* Should validation responses include user-facing messages, localization keys, or only machine-readable codes?
* Should completed-course evidence be passed in the request during early development or loaded only from database tables?
* Should validation endpoints require ownership checks based on `ed_plans.user_id`?

## 8. Required Database Tables

### Already Existing Tables

Planning:

* `ed_plans`
* `plan_courses`
* `plan_sections`
* `plan_schedules`

Catalog:

* `universities`
* `programs`
* `courses`
* `course_prerequisites`
* `course_corequisites`

Calendar and scheduling:

* `academic_terms`
* `course_offerings`
* `sections`
* `section_meetings`

Identity:

* `users`

Legacy planning tables exist but should not be mixed with normalized validation unless a migration or compatibility layer explicitly maps them:

* `education_plans`
* `program_courses`
* `course_schedules`
* `course_reschedules`

### Future Tables Likely Needed

Credit policy:

* `term_credit_limits`
* `credit_overrides`

Student academic history:

* `completed_courses`
* `transfer_credits`
* `test_credits`
* `placement_credits`

Exceptions and equivalencies:

* `waivers`
* `substitutions`
* `student_course_equivalencies`

Repeat and attempt policy:

* `course_repeat_rules`
* `completed_course_attempts` or `student_course_attempts`

Optional validation operations:

* `planning_validation_runs`, if validation results need audit history.
* `planning_validation_overrides`, if advisors can approve specific issues.

## 9. Open Questions

Business rules:

* Should earlier planned courses count as projected prerequisite satisfaction?
* What completion statuses and grades satisfy prerequisites?
* Can in-progress courses satisfy future prerequisites?
* How are failed, withdrawn, incomplete, or repeated courses represented?
* Can transfer, test, placement, waiver, and substitution records satisfy prerequisites?
* Can a previously completed course ever satisfy a corequisite?
* Are corequisite relationships directed or symmetric?
* Are optional co-enrollment suggestions distinct from required corequisites?
* Should validation enforce course offerings by term?
* Should validation enforce section meeting conflicts?

Credit policy:

* Should the temporary 18-credit max block save immediately?
* Are credit limits different by program, university, term type, student level, or student status?
* Are credit overload approvals supported?
* Do repeated, zero-credit, variable-credit, lab, or completed courses count toward term load?

Duplicates and retakes:

* Are duplicate courses ever allowed?
* How should planned retakes be represented?
* Should repeated courses count toward prerequisites, credits, and program requirements?
* What catalog rules determine whether a course is repeatable for credit?

API and UX:

* Should invalid validation responses be HTTP success responses with blocking issues?
* Which modes should validation support: draft, save, generation, advisor review?
* Should validation collect all issues or stop after blocking prerequisites?
* Should warning and recommendation messages be generated backend-side or frontend-side?
* How should validation identify auto-added corequisites?

Data modeling:

* What is the authoritative table for completed courses?
* What is the authoritative table for transfer credits?
* How should waivers and substitutions map to courses versus broader requirements?
* Should validation results be persisted for audit history?
* Should legacy `education_plans` be validated, migrated, or ignored by normalized validation?

## Recommended Implementation Order

1. Finalize validation result shape and issue code taxonomy.
2. Build read-only context queries for `ed_plans`, `plan_courses`, `courses`, `academic_terms`, `course_prerequisites`, and `course_corequisites`.
3. Implement duplicate validation first because current persistence already disallows duplicates.
4. Implement prerequisite validation against direct all-of `course_prerequisites`.
5. Implement corequisite validation against direct same-term `course_corequisites`.
6. Implement credit validation with a provider that initially returns `MAX_TERM_CREDITS = 18`.
7. Add future validation endpoints after the service is covered by domain tests.
8. Add future tables for completed courses, transfer credits, waivers, substitutions, repeat rules, and term credit limits in separate migration work.
9. Expand validation to grouped prerequisites, minimum grades, course availability, schedule conflicts, advisor overrides, and persisted validation history only after first-version rules are stable.
