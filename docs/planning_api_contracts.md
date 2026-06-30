# Planning API Contracts

These APIs are design contracts only. They define expected planning-domain interactions for review before implementation. Field names and required status should be finalized after planning rules and catalog contracts are approved.

## Confirmed Rules

* A prerequisite must be completed before a dependent course can be scheduled.
* If prerequisite requirements are not satisfied, the course cannot be added and the plan is invalid.
* A corequisite must be scheduled together with its associated course.
* Prerequisites and corequisites are separate concepts in EdPlan.
* Corequisites must not be modeled as previously completed requirements.
* Recommended year and semester are guidance only.
* Students may take courses earlier or later if requirements are satisfied.
* Students may complete programs faster than the recommended timeline.

## Proposed Planner Behavior

### Corequisite Auto-Enrollment

* When a student adds a course that has required corequisites, the planner automatically attempts to add all required corequisite courses to the same semester.
* Validation occurs after automatic corequisite addition.
* If all required corequisites cannot be scheduled, the operation fails.
* Failure explanations should clearly describe why the operation failed.
* Known failure reasons include semester credit limit exceeded, duplicate course conflicts, scheduling constraints, and other validation failures.

## Assumptions

No business assumptions are made in this document. Request and response shapes are placeholders for review and should be revised when identifiers, requirement formats, and validation severity rules are confirmed.

## Generate Plan

`POST /api/plans/generate`

### Request

Purpose: Request a proposed academic plan for a program.

Candidate request elements:

* Program reference.
* Completed courses.
* Optional current academic plan.
* Optional planning preferences or constraints.

Example draft shape:

```json
{
  "program": {
    "program_ref": "string"
  },
  "completed_courses": [
    {
      "course_ref": "string"
    }
  ],
  "current_plan": {
    "semesters": [
      {
        "semester_ref": "string",
        "courses": [
          {
            "course_ref": "string"
          }
        ]
      }
    ]
  },
  "preferences": {}
}
```

### Response

Purpose: Return a generated academic plan and any validation feedback.

Candidate response elements:

* Generated academic plan.
* Validation status.
* Errors.
* Warnings.

Example draft shape:

```json
{
  "success": true,
  "data": {
    "plan": {
      "semesters": [
        {
          "semester_ref": "string",
          "courses": [
            {
              "course_ref": "string"
            }
          ]
        }
      ]
    },
    "validation": {
      "is_valid": true,
      "errors": [],
      "warnings": []
    }
  }
}
```

### Validation

#### Confirmed Rules

* Generated plans must not schedule a course before all prerequisites are completed.
* Generated plans must schedule required corequisites together with their associated courses.
* Generated plans must treat prerequisites and corequisites as separate concepts.
* Generated plans may differ from the recommended course sequence if requirements are satisfied.
* Generated plans may accelerate completion if requirements are satisfied.

#### Automatic Corequisite Inclusion

* When generated plan output includes a course with required corequisites, the generated plan must also include the required corequisites in the same semester.
* Validation occurs after required corequisites are included.
* If required corequisites cannot be included in a valid generated plan, the response should clearly explain why generation failed or could not produce a valid plan.

#### Open Questions

* What preferences or constraints are supported?
* Should generation fail if a valid plan cannot be produced?
* Should generation return partial plans?
* How should unavailable or unscheduled courses be reported?
* Should the response explicitly identify courses that were included because of required corequisites?
* What identifier format should be used for programs, semesters, and courses?

### Errors

Candidate error categories:

* Invalid request.
* Unknown program reference.
* Unknown course reference.
* No valid plan available under confirmed rules.
* Required corequisites cannot be scheduled in the same semester as the associated course.
* Planning rules unavailable or incomplete.

Open questions:

* What error codes and HTTP status codes should be used?
* Should validation errors appear in the same shape as request errors?

---

## Validate Plan

`POST /api/plans/validate`

### Request

Purpose: Validate an academic plan against confirmed planning rules.

Candidate request elements:

* Program reference.
* Completed courses.
* Academic plan to validate.

Example draft shape:

```json
{
  "program": {
    "program_ref": "string"
  },
  "completed_courses": [
    {
      "course_ref": "string"
    }
  ],
  "plan": {
    "semesters": [
      {
        "semester_ref": "string",
        "courses": [
          {
            "course_ref": "string"
          }
        ]
      }
    ]
  }
}
```

### Response

Purpose: Return whether the plan is valid and describe any issues.

Example draft shape:

```json
{
  "success": true,
  "data": {
    "is_valid": true,
    "errors": [],
    "warnings": []
  }
}
```

### Validation

#### Confirmed Rules

* A plan is invalid if it schedules a course before all prerequisites are completed.
* A plan is invalid if a course is scheduled without required corequisites in the same semester.
* A plan must treat prerequisites and corequisites as separate concepts.
* A plan is not invalid solely because it differs from recommended year or semester.
* A plan is not invalid solely because it completes faster than the recommended timeline.

#### Open Questions

* What issue severities are supported?
* Should prerequisite and corequisite issues include affected courses and semesters?
* Should sequence deviations be warnings?
* Should validation include credit-load checks?
* Should validation include course availability checks?

### Errors

Candidate error categories:

* Invalid request.
* Unknown program reference.
* Unknown course reference.
* Required corequisite missing from the associated course semester.
* Planning rules unavailable or incomplete.

Open questions:

* Should invalid plans return `success: true` with validation errors, or an error response?
* What error code taxonomy is required?

---

## Graduation Audit

`POST /api/plans/audit`

### Request

Purpose: Evaluate progress toward graduation for a program.

Candidate request elements:

* Program requirements reference.
* Completed courses.
* Current academic plan.

Example draft shape:

```json
{
  "program": {
    "program_ref": "string"
  },
  "completed_courses": [
    {
      "course_ref": "string"
    }
  ],
  "current_plan": {
    "semesters": [
      {
        "semester_ref": "string",
        "courses": [
          {
            "course_ref": "string"
          }
        ]
      }
    ]
  }
}
```

### Response

Purpose: Return graduation progress and any audit warnings.

Example draft shape:

```json
{
  "success": true,
  "data": {
    "credits_completed": null,
    "credits_remaining": null,
    "satisfied_requirements": [],
    "in_progress_requirements": [],
    "missing_requirements": [],
    "warnings": []
  }
}
```

### Validation

#### Confirmed Rules

* Completed courses contribute to progress toward graduation.
* Planned courses may identify requirements that are in progress.
* Missing requirements must be reported.

#### Open Questions

* How should credits completed and remaining be calculated?
* What requirement categories are supported?
* Should audit output include projected completion?
* Should planned courses count toward projected graduation status?
* How should transfer credit and waivers be represented?

### Errors

Candidate error categories:

* Invalid request.
* Unknown program reference.
* Unknown course reference.
* Program requirements unavailable.

Open questions:

* Should incomplete audit data return an error or a partial audit with warnings?
* What fields are required for a valid audit request?

---

## Move Course

`POST /api/plans/move-course`

### Request

Purpose: Request a course move within an academic plan.

Candidate request elements:

* Current academic plan.
* Course to move.
* Source semester.
* Target semester.
* Completed courses.

Example draft shape:

```json
{
  "plan": {
    "semesters": [
      {
        "semester_ref": "string",
        "courses": [
          {
            "course_ref": "string"
          }
        ]
      }
    ]
  },
  "move": {
    "course_ref": "string",
    "from_semester_ref": "string",
    "to_semester_ref": "string"
  },
  "completed_courses": [
    {
      "course_ref": "string"
    }
  ]
}
```

### Response

Purpose: Return the updated plan and validation feedback.

Example draft shape:

```json
{
  "success": true,
  "data": {
    "plan": {
      "semesters": []
    },
    "validation": {
      "is_valid": true,
      "errors": [],
      "warnings": []
    }
  }
}
```

### Validation

#### Confirmed Rules

* A move is invalid if it schedules a course before all prerequisites are completed.
* A move is invalid if it leaves a course without required corequisites in the same semester.
* A move must treat prerequisites and corequisites as separate concepts.
* A move is not invalid solely because it deviates from recommended year or semester.
* A move is not invalid solely because it accelerates completion.

#### Open Questions

* Should dependent courses move automatically?
* Should corequisites move automatically?
* What happens when moving a course causes a corequisite violation?
* If moving a course would separate it from required corequisites, should the move fail or should the planner attempt to move the corequisites too?
* If moving a corequisite would separate it from its associated course, should the move fail or should the planner attempt to move the associated course too?
* Should invalid moves be rejected or returned with validation errors?
* Can users move courses into new semesters?
* Can users move courses into past semesters?
* Should move operations preserve course order within a semester?

### Errors

Candidate error categories:

* Invalid request.
* Course not found in plan.
* Source semester not found.
* Target semester not found.
* Move violates confirmed planning rules.
* Move causes a required corequisite violation.
* Planning rules unavailable or incomplete.

Open questions:

* Should move validation errors prevent saving?
* What error shape should clients use for field-specific issues?

## Cross-Cutting Open Questions

* What identifier format should all planning APIs use?
* Which fields are required in each request?
* Should responses include human-readable messages, machine-readable codes, or both?
* What severity levels should validation issues support?
* How should transfer, test, placement, waiver, and substitution credits be represented?
* What versioning strategy is needed for these contracts?
