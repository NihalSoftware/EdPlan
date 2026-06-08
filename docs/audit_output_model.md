# Audit Output Model

## Goal

Define a stable graduation-audit response model that can be reviewed before implementation. This document describes candidate output concepts without committing to internal representation or unconfirmed graduation rules.

## Audit Categories

### Satisfied

Confirmed rule:

* A requirement may be considered satisfied when the student has completed the required course or requirement.

Open questions:

* What completion statuses count as completed?
* Can transfer credit, placement, test credit, or waivers satisfy a requirement?
* Can one course satisfy more than one requirement?

### In Progress

Confirmed rule:

* A requirement may be considered in progress when it appears in the current academic plan but is not yet completed.

Open questions:

* Should currently enrolled courses and future planned courses be separated?
* Should in-progress requirements count toward projected graduation completion?
* How should dropped, withdrawn, failed, or incomplete courses be handled?

### Missing

Confirmed rule:

* A requirement is missing when it is neither completed nor present in the current academic plan.

Open questions:

* How should elective requirements be audited?
* How should category-based requirements be audited?
* How should non-course requirements be audited?
* How should repeated courses affect missing requirements?

## Candidate Output Structure

Candidate top-level concepts:

```json
{
  "credits_completed": null,
  "credits_remaining": null,
  "satisfied_requirements": [],
  "in_progress_requirements": [],
  "missing_requirements": [],
  "warnings": []
}
```

### Confirmed Output Concepts

* Credits completed.
* Credits remaining.
* Satisfied requirements.
* Missing requirements.
* Warnings.

### Candidate Output Concepts

* In-progress requirements.
* Requirement explanations.
* Related courses for each requirement.
* Requirement status.

### Open Questions

* How are credits completed calculated?
* How are credits remaining calculated?
* Should audit output distinguish current progress from projected progress?
* Should audit output include explanations for each satisfied or missing requirement?
* Should audit output include an estimated graduation term?

## Requirement Representation

### Candidate Structures

A requirement entry may include:

```json
{
  "requirement_ref": "string",
  "name": "string",
  "status": "satisfied | in_progress | missing",
  "matched_course_refs": ["string"],
  "planned_course_refs": ["string"],
  "message": "string"
}
```

This structure is a candidate only. It is intended to support review of audit output, not to define internal representation.

### Open Questions

* What identifier format should requirements use?
* What requirement types must the first audit version support?
* Should requirement entries include category information?
* Should requirement entries include credits?
* Should one course be allowed to satisfy multiple requirements?
* How should requirements with multiple valid course options be represented?
* How should non-course requirements be represented?

## Warning Representation

### Candidate Structures

A warning entry may include:

```json
{
  "code": "string",
  "message": "string",
  "course_ref": "string",
  "semester_ref": "string",
  "requirement_ref": "string"
}
```

Potential warning sources, pending confirmation:

* Prerequisite issues.
* Corequisite issues.
* Sequence deviations.
* Credit-load issues.

### Open Questions

* Which warning categories are required?
* Should warnings include severity levels?
* Should warnings be user-facing, machine-readable, or both?
* Should warnings affect audit status?
* Should warnings duplicate validation errors or reference them?

## Open Questions

* What is the complete set of graduation requirements for each program?
* Which audit statuses should be supported?
* What warning severity levels are needed, if any?
* How should transfer, placement, test, waiver, and substitution credits appear in audit output?
* How should program changes after completed coursework be handled?
* How should catalog year differences be represented?
