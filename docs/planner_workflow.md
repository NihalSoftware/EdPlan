# Planner Workflow

## Goal

Describe end-to-end planner behavior for generation, validation, course movement, and graduation audit. This document uses confirmed planning rules and marks unresolved behavior as open questions.

## Generate Plan Workflow

### Candidate Workflow

```text
Student selects program
↓
Planner receives request
↓
Planner evaluates completed courses
↓
Planner generates plan
↓
Corequisite auto-enrollment
↓
Validation
↓
Response returned
```

### Confirmed Rules

* Generated plans must not schedule a course before all prerequisites are completed.
* Generated plans must schedule required corequisites together with their associated courses.
* Recommended year and semester are guidance only.
* Students may complete programs faster than the recommended timeline.

### Candidate Behavior

* When generated output includes a course with required corequisites, the required corequisites are included in the same semester.
* Validation occurs after required corequisites are included.
* If required corequisites cannot be included in a valid generated plan, the response explains why a valid plan could not be produced.

### Open Questions

* Should generation return partial plans?
* Should generated plans identify automatically included corequisites?
* What planning preferences or constraints are supported?
* How should unavailable or unscheduled courses be reported?

---

## Validate Plan Workflow

### Candidate Workflow

```text
Request
↓
Validation Engine
↓
Response
```

Expanded candidate flow:

```text
Request
↓
Prerequisite Validation
↓
Corequisite Validation
↓
Plan Validation
↓
Validation Result
↓
Response
```

### Confirmed Rules

* A plan is invalid if it schedules a course before all prerequisites are completed.
* A plan is invalid if a course is scheduled without required corequisites in the same semester.
* Prerequisites and corequisites are separate concepts.
* A plan is not invalid solely because it differs from recommended year or semester.
* A plan is not invalid solely because it completes faster than the recommended timeline.

### Open Questions

* Should validation stop after blocking errors or collect all issues?
* Should validation include credit-load checks?
* Should validation include scheduling constraints?
* Should validation include course availability checks?
* Which issues are errors and which are warnings?

---

## Move Course Workflow

### Candidate Workflow

```text
Request
↓
Course move
↓
Corequisite handling
↓
Validation
↓
Response
```

### Confirmed Rules

* A move is invalid if it schedules a course before all prerequisites are completed.
* A move is invalid if it leaves a course without required corequisites in the same semester.
* A move is not invalid solely because it deviates from recommended year or semester.
* A move is not invalid solely because it accelerates completion.

### Open Questions

* Should moving a course automatically move its corequisites?
* Should moving a course automatically move dependent courses?
* What happens when moving a course causes a corequisite violation?
* If moving a course would separate it from required corequisites, should the move fail or should the planner attempt to move the corequisites too?
* If moving a corequisite would separate it from its associated course, should the move fail or should the planner attempt to move the associated course too?
* Should invalid moves be rejected or returned with validation errors?

---

## Graduation Audit Workflow

### Candidate Workflow

```text
Request
↓
Audit evaluation
↓
Requirement classification
↓
Response
```

### Confirmed Rules

* Completed courses contribute to progress toward graduation.
* Planned courses may be used to identify requirements that are in progress.
* Missing requirements must be reported.
* Warnings may be reported when a plan contains potential issues.

### Candidate Classification

* Satisfied.
* In progress.
* Missing.

### Open Questions

* How are credits completed calculated?
* How are credits remaining calculated?
* Should audit output distinguish current progress from projected progress?
* Should audit output include an estimated graduation term?
* Which requirement types must the first audit version support?

## Failure Paths

### Prerequisite Violation

Confirmed behavior:

* If prerequisite requirements are not satisfied, the dependent course cannot be added.
* A plan with an unmet prerequisite is invalid.

Candidate response:

* Return a validation error identifying the dependent course and unmet prerequisite requirement.

Open questions:

* What issue code should represent prerequisite violations?
* What related course information should be included?

### Corequisite Violation

Confirmed behavior:

* A course must be scheduled with required corequisites in the same semester.
* A plan missing required same-semester corequisites is invalid.

Candidate response:

* Return a validation error identifying the course and missing required corequisite.

Open questions:

* Should the planner attempt corequisite auto-enrollment before returning an error?
* Should automatically added corequisites be identified in the response?

### Invalid Plan

Confirmed behavior:

* Plans that violate prerequisite or required corequisite rules are invalid.

Open questions:

* Should invalid plans return an error response or a successful response with validation errors?
* Should validation collect all issues or stop after the first blocking issue?

### Unknown References

Candidate behavior:

* If a request references an unknown program, course, semester, or requirement, the planner should return a clear error.

Open questions:

* What reference types must be validated in the first implementation?
* What error codes should unknown references use?

### Incomplete Planning Data

Candidate behavior:

* If required planning data is unavailable, the planner should return a clear explanation.

Open questions:

* What data is required to generate a plan?
* What data is required to validate a plan?
* What data is required to run a graduation audit?
* Should incomplete data produce errors, warnings, or partial results?

## Open Questions

* What identifiers should planner workflows use?
* Which workflows should include warnings?
* Which workflows should return partial results?
* What response shape should all workflows share?
* Which candidate validation checks are required for the first implementation?
