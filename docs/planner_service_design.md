# Planner Service Design

## Goal

Define the architecture and responsibilities of the future `PlannerService` at the planning-domain level. This document is implementation-oriented but remains independent of internal representation and API framework choices.

## Responsibilities

### Confirmed Responsibilities

* Generate academic plans that respect confirmed prerequisite and corequisite rules.
* Validate academic plans against confirmed planning rules.
* Support course movement workflows through validation.
* Produce graduation audit results using completed courses and the current academic plan.
* Return clear explanations when planning operations fail.

### Candidate Responsibilities

* Coordinate validation steps through a validation engine.
* Coordinate graduation progress evaluation through an audit component.
* Normalize request inputs into planning-domain objects before validation.
* Return structured errors and warnings for client display.

## Non-Responsibilities

### Confirmed Non-Responsibilities

* The service must not treat corequisites as previously completed requirements.
* The service must not enforce unconfirmed planning, audit, or workflow rules.

### Open Questions

* Which component owns student preference handling?
* Which component owns course availability or scheduling constraints?
* Which component owns formatting user-facing explanations?

## Service Overview

`PlannerService` is the planning-domain coordinator. It receives planning requests, delegates rule evaluation to validation and audit components, and returns planning outputs in a stable domain shape.

Confirmed rules used by the service:

* A prerequisite must be completed before a dependent course can be scheduled.
* If prerequisite requirements are not satisfied, the course cannot be added and the plan is invalid.
* A corequisite must be scheduled together with its associated course.
* Prerequisites and corequisites are separate concepts.
* Recommended year and semester are guidance only.
* Students may complete programs faster than the recommended timeline.

---

### generate_plan()

#### Purpose

Create a proposed academic plan for a program using completed courses, any current plan context, and confirmed planning rules.

#### Inputs

Candidate inputs:

* Program reference.
* Completed courses.
* Optional current academic plan.
* Optional planning preferences or constraints.

#### Outputs

Candidate outputs:

* Generated academic plan.
* Validation result.
* Errors.
* Warnings.

#### Validation Behavior

Confirmed behavior:

* Generated plans must not schedule a course before all prerequisites are completed.
* Generated plans must schedule required corequisites together with their associated courses.
* Generated plans may differ from the recommended course sequence when requirements are satisfied.
* Generated plans may accelerate completion when requirements are satisfied.

Proposed behavior:

* If generated output includes a course with required corequisites, the required corequisites are included in the same semester.
* Validation occurs after required corequisites are included.
* If required corequisites cannot be included in a valid generated plan, generation returns a clear failure explanation.

#### Dependencies

Candidate dependencies:

* Program requirements provider.
* Course relationship provider for prerequisites and corequisites.
* Validation engine.
* Plan generation strategy.

#### Open Questions

* What planning preferences or constraints are supported?
* Should generation return partial plans?
* Should generation explicitly identify automatically included corequisites?
* How should unavailable or unscheduled courses be reported?

---

### validate_plan()

#### Purpose

Evaluate whether an academic plan satisfies confirmed planning rules.

#### Inputs

Candidate inputs:

* Program reference.
* Completed courses.
* Academic plan to validate.

#### Outputs

Candidate outputs:

* Validation status.
* Errors.
* Warnings.

#### Validation Behavior

Confirmed behavior:

* A plan is invalid if it schedules a course before all prerequisites are completed.
* A plan is invalid if a course is scheduled without required corequisites in the same semester.
* A plan is not invalid solely because it differs from recommended year or semester.
* A plan is not invalid solely because it completes faster than the recommended timeline.

#### Dependencies

Candidate dependencies:

* Validation engine.
* Program requirements provider.
* Course relationship provider.

#### Open Questions

* Should validation distinguish blocking errors from warnings?
* Should sequence deviations produce warnings?
* Should validation include course availability checks?
* Should validation include credit-load checks?

---

### move_course()

#### Purpose

Evaluate a requested course move within an academic plan and return the resulting plan or a clear failure explanation.

#### Inputs

Candidate inputs:

* Current academic plan.
* Course to move.
* Source semester.
* Target semester.
* Completed courses.

#### Outputs

Candidate outputs:

* Updated academic plan.
* Validation result.
* Errors.
* Warnings.

#### Validation Behavior

Confirmed behavior:

* A move is invalid if it schedules a course before all prerequisites are completed.
* A move is invalid if it leaves a course without required corequisites in the same semester.
* A move is not invalid solely because it deviates from recommended year or semester.
* A move is not invalid solely because it accelerates completion.

#### Dependencies

Candidate dependencies:

* Plan mutation component.
* Validation engine.
* Course relationship provider.

#### Open Questions

* Should moving a course automatically move its corequisites?
* Should moving a course automatically move dependent courses?
* What happens when moving a course causes a corequisite violation?
* Should invalid moves be rejected, or returned as an updated plan with validation errors?
* Can users move courses into new semesters?
* Can users move courses into past semesters?

---

### audit_graduation()

#### Purpose

Evaluate progress toward graduation using program requirements, completed courses, and the current academic plan.

#### Inputs

Candidate inputs:

* Program requirements.
* Completed courses.
* Current academic plan.

#### Outputs

Candidate outputs:

* Credits completed.
* Credits remaining.
* Satisfied requirements.
* In-progress requirements.
* Missing requirements.
* Warnings.

#### Validation Behavior

Confirmed behavior:

* Completed courses contribute to progress toward graduation.
* Planned courses may identify requirements that are in progress.
* Missing requirements must be reported.
* Warnings may be reported when a plan contains potential issues.

#### Dependencies

Candidate dependencies:

* Graduation audit component.
* Program requirements provider.
* Validation engine, if audit warnings include plan validation issues.

#### Open Questions

* How are completed credits calculated?
* How are remaining credits calculated?
* Should audit output distinguish current progress from projected progress?
* Should audit output include an estimated graduation term?
* Which requirement types must the first audit version support?

## Future Extensions

These are future possibilities only, not confirmed requirements:

* Scheduling integration.
* Finance integration.
* Career integration.
* Agent integration.

## Open Questions

* What are the stable identifiers for programs, courses, semesters, and requirements?
* What issue severity levels are needed?
* What should be the standard error shape across planner operations?
* Which planning behaviors must be synchronous?
* Which planning behaviors can be asynchronous in future versions?
