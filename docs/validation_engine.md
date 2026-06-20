# Validation Engine

## Goal

Define how plan validation should be organized before planner implementation begins. The validation engine evaluates academic plans against confirmed planning rules and returns structured validation results.

## Validation Categories

### Prerequisite Validation

#### Confirmed Rules

* A prerequisite must be completed before a dependent course can be scheduled.
* If prerequisite requirements are not satisfied, the course cannot be added.
* If prerequisite requirements are not satisfied, the plan is invalid.

#### Validation Flow

Candidate flow:

1. Read completed courses.
2. Read planned course placement by semester.
3. For each planned course, identify prerequisite requirements.
4. Confirm prerequisites are completed before the dependent course semester.
5. Add a validation error for each unmet prerequisite.

#### Open Questions

* How should prerequisites that are in progress be treated?
* How should prerequisite groups be represented, such as "Course A or Course B"?
* Can placement, transfer credit, test credit, or other approved credit satisfy prerequisites?
* What data should each prerequisite validation error include?

---

### Corequisite Validation

#### Confirmed Rules

* A corequisite must be scheduled together with its associated course.
* Prerequisites and corequisites are separate concepts.
* Corequisites must not be modeled as previously completed requirements.
* A plan is invalid if a course is scheduled without required corequisites in the same semester.

#### Validation Flow

Candidate flow:

1. Read planned course placement by semester.
2. For each planned course, identify required corequisites.
3. Confirm each required corequisite is scheduled in the same semester as the associated course.
4. Add a validation error for each missing same-semester corequisite.

#### Open Questions

* How should optional course pairings be distinguished from required corequisites?
* Should validation report missing corequisites on the associated course, the corequisite course, or both?
* What data should each corequisite validation error include?
* Should the validation engine know whether a corequisite was automatically added?

---

### Plan Validation

#### Confirmed Rules

* A plan is not invalid solely because it differs from recommended year or semester.
* A plan is not invalid solely because it completes a program faster than the recommended timeline.
* When corequisite auto-enrollment is used, validation occurs after automatic corequisite addition.

#### Validation Flow

Candidate flow:

1. Receive the full academic plan.
2. Run prerequisite validation.
3. Run corequisite validation.
4. Run any additional confirmed plan-level validation.
5. Return a combined validation result.

#### Open Questions

* Should recommended sequence deviations produce warnings?
* Should validation include semester credit-load checks?
* Should validation include scheduling constraints?
* Should validation include duplicate course conflicts?
* Should validation include course availability checks?
* Should validation block plan generation or only report issues?

## Validation Result Model

### Candidate Structures

The validation result may include:

* `is_valid`: Boolean validation status.
* `errors`: Blocking validation issues.
* `warnings`: Non-blocking validation issues.

Candidate issue structure:

```json
{
  "code": "string",
  "message": "string",
  "course_ref": "string",
  "semester_ref": "string",
  "related_course_refs": ["string"]
}
```

### Open Questions

* What issue codes are required?
* Should issues include machine-readable severity values?
* Should issues include user-facing messages, machine-readable metadata, or both?
* Should warnings ever make a plan invalid?

## Validation Pipeline

Candidate pipeline:

```text
Plan
↓
Prerequisite Validation
↓
Corequisite Validation
↓
Plan Validation
↓
Validation Result
```

## Open Questions

* What is the complete set of validation categories for the first implementation?
* What identifiers should validation results use?
* Should validation stop after blocking errors or continue collecting all issues?
* How should validation behave when planning data is incomplete?
* Which validation failures should be eligible for clear operation-failure explanations?
