# Graduation Audit

## Goal

Define how EdPlan evaluates progress toward graduation in a way that is independent of future schema decisions. This document records confirmed audit behavior only and lists unknown policy decisions as open questions.

## Inputs

* Program Requirements: The set of requirements a student must satisfy to complete a program.
* Completed Courses: Courses the student has already completed.
* Current Academic Plan: Courses the student intends to take in future semesters.

## Outputs

* Credits Completed
* Credits Remaining
* Satisfied Requirements
* Missing Requirements
* Warnings

## Audit Categories

### Satisfied

#### Confirmed Rules

* A requirement may be considered satisfied when the student has completed the required course or requirement.

#### Open Questions

* What completion statuses count as completed?
* Are minimum grades required?
* Can transfer credit, placement, test credit, or waivers satisfy a requirement?
* Can one course satisfy more than one requirement?

### In Progress

#### Confirmed Rules

* A requirement may be considered in progress when it appears in the current academic plan but is not yet completed.

#### Open Questions

* Should currently enrolled courses and future planned courses be separated?
* Should in-progress requirements count toward projected graduation completion?
* How should dropped, withdrawn, failed, or incomplete courses be handled?

### Missing

#### Confirmed Rules

* A requirement is missing when it is neither completed nor present in the current academic plan.

#### Open Questions

* How should elective requirements be audited?
* How should category-based requirements be audited?
* How should non-course requirements be audited?
* How should repeated courses affect missing requirements?

## Audit Rules

### Confirmed Rules

* Completed courses contribute to progress toward graduation.
* Planned courses may be used to identify requirements that are in progress.
* Missing requirements must be reported.
* Warnings may be reported when a plan contains potential issues.

### Open Questions

* How are completed credits calculated?
* How are remaining credits calculated?
* Are credits counted by attempted credits, earned credits, required credits, or another measure?
* Should duplicate courses count more than once?
* How are variable-credit courses handled?
* Should warnings include prerequisite issues, corequisite issues, sequence deviations, credit-load issues, or all of these?
* Should audit results include an estimated graduation term?

## Edge Cases

### Confirmed Rules

No edge-case handling rules have been confirmed beyond the audit rules above.

### Open Questions

* Transfer courses without direct course equivalencies.
* Courses that satisfy multiple requirements.
* Requirements that can be satisfied by choosing one course from a list.
* Requirements based on minimum total credits.
* Requirements based on minimum credits within a category.
* Courses repeated for a better grade.
* Courses repeated for additional credit.
* Substitutions, waivers, or advisor-approved exceptions.
* Program changes after a student has completed some coursework.
* Catalog year differences.
* Courses planned in the same semester as their corequisites.
* Courses planned before prerequisites are completed.

## Open Questions

* What is the complete set of graduation requirements for each program?
* Which requirement types must the first version of the audit support?
* What statuses should appear in audit output?
* What warning severity levels are needed, if any?
* Should audit output distinguish current progress from projected progress?
* Should audit output include explanations for each satisfied or missing requirement?
