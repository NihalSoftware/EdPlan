# Planner Rules

## Goal

Define planning and validation behavior for academic plans in EdPlan. This document captures confirmed planning rules only and identifies unknown policy decisions as open questions for review before implementation.

## Definitions

* Program: A structured set of academic requirements that a student is working toward completing.
* Course: An academic unit that may carry credits and may have prerequisite, corequisite, or sequence guidance.
* Semester: A planning period in which one or more courses may be scheduled.
* Academic Plan: A proposed sequence of courses across one or more semesters.
* Prerequisite: A course or requirement that must be completed before another course may be scheduled.
* Corequisite: A course or requirement that must be scheduled together with an associated course.

## Planning Rules

### Prerequisites

#### Confirmed Rules

* A prerequisite must be completed before a dependent course can be scheduled.
* If prerequisite requirements are not satisfied, the dependent course cannot be added.
* If prerequisite requirements are not satisfied, the plan is invalid.

#### Open Questions

* How should the planner treat prerequisites that are in progress but not completed?
* Are minimum grades required for prerequisite completion?
* Can placement, transfer credit, test credit, or other approved credit satisfy prerequisites?
* How should prerequisite groups be represented, such as "Course A or Course B"?

### Corequisites

#### Confirmed Rules

* A corequisite must be scheduled together with its associated course.
* Prerequisites and corequisites are separate concepts in EdPlan.
* Corequisites must not be modeled as previously completed requirements. Previously completed requirements belong to prerequisite behavior.

#### Open Questions

* How should optional course pairings be distinguished from required corequisites?
* How should the planner handle a course move that separates a course from its corequisite?

### Corequisite Auto-Enrollment

#### Proposed Rule

* When a student adds a course that has required corequisites, the planner automatically attempts to add all required corequisite courses to the same semester.
* Validation occurs after automatic corequisite addition.
* If all required corequisites cannot be scheduled, the operation fails.
* The planner should return a clear explanation of why the operation failed.

#### Known Failure Reasons

* Semester credit limit exceeded.
* Duplicate course conflicts.
* Scheduling constraints.
* Other validation failures.

#### Open Questions

* What response shape should identify automatically added corequisites?
* Should the planner distinguish automatic additions from courses explicitly selected by the student?
* Should auto-enrollment run only when adding a course, or also during plan generation and plan modification?

### Recommended Course Sequence

#### Confirmed Rules

* Recommended year and semester are guidance only.
* Students may take courses earlier or later if requirements are satisfied.

#### Open Questions

* Should deviations from the recommended sequence produce warnings?
* Are any courses restricted to specific academic terms?
* Are recommended sequences different for full-time, part-time, or transfer students?

### Accelerated Completion

#### Confirmed Rules

* Students may complete programs faster than the recommended timeline.

#### Open Questions

* Are there maximum credit limits per semester?
* Are summer or intersession terms supported?
* Are there minimum time-in-program rules for any program?

### Semester Planning

#### Confirmed Rules

* A semester can contain multiple planned courses.
* Semester placement must respect confirmed prerequisite and corequisite rules.
* Recommended year and semester do not prevent valid alternate placement.

#### Open Questions

* What is the maximum allowed credit load per semester?
* What is the minimum credit load, if any?
* Are semester types limited to fall and spring, or are summer and other terms supported?
* Should course availability by semester be enforced?
* Should time conflicts be considered in academic planning?
* Are non-course requirements planned within semesters?

## Validation Rules

### Confirmed Rules

* A plan is invalid if it schedules a course before its prerequisites are completed.
* A plan is invalid if a course is scheduled without required corequisites in the same semester.
* A plan is not invalid solely because it differs from the recommended year or semester.
* A plan is not invalid solely because it completes a program faster than the recommended timeline.
* When corequisite auto-enrollment is used, validation occurs after automatic corequisite addition.

### Open Questions

* Should validation distinguish errors from warnings?
* Should validation block plan generation or only report issues?
* Should duplicate courses be allowed when repeating a course is required or desired?
* How should withdrawn, failed, incomplete, or repeated courses affect validation?
* Should total program credits be validated?

## Plan Modification Rules

### Confirmed Rules

* No specific plan modification rules have been confirmed beyond the validation rules above.

### Open Questions

* Which plan edits are supported, such as moving, adding, removing, or replacing courses?
* Should moving a course automatically move dependent courses?
* Should moving a course automatically move corequisites?
* What happens when moving a course causes a corequisite violation?
* Should users be allowed to save a plan with validation warnings?
* Should users be allowed to save a plan with validation errors?

## Assumptions

No additional business assumptions are made in this document. Terms are defined only to support review of the confirmed rules and open questions.

## Open Questions

* What is the authoritative source for program requirements?
* What is the authoritative source for course prerequisites and corequisites?
* How are transfer credits represented?
* How are non-course graduation requirements represented?
* Are requirements evaluated by credits, course completion, categories, milestones, or a combination?
* What student-specific constraints should the planner consider?
* Which planning issues are errors and which are warnings?
