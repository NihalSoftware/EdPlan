# API Reference

Generated: 2026-06-17

Base path in local routing examples: `/api`.

Response envelopes usually follow:

```json
{
  "success": true,
  "data": {},
  "metadata": {}
}
```

Some legacy and supporting endpoints also return `message`.

## Discovery

### GET `/api/universities`

Purpose: Search or browse universities.

Request body: none.

Example query:

```text
/api/universities?search=state&page=0&per_page=10
```

Response example:

```json
{
  "success": true,
  "data": [
    {
      "university_id": "11111111-1111-1111-1111-111111111111",
      "unit_id": "11111111-1111-1111-1111-111111111111",
      "university_name": "Example State University",
      "name": "Example State University",
      "city": "Example City",
      "state": "CA",
      "website": "https://example.edu"
    }
  ],
  "metadata": {
    "count": 1,
    "page": 0,
    "per_page": 10,
    "source": "live_database"
  }
}
```

Tables involved: `universities`.

### GET `/api/universities/{unit_id}`

Purpose: Get one university by UUID. `unit_id` is the same value as `university_id`.

Request body: none.

Response example:

```json
{
  "success": true,
  "data": {
    "university_id": "11111111-1111-1111-1111-111111111111",
    "unit_id": "11111111-1111-1111-1111-111111111111",
    "university_name": "Example State University",
    "city": "Example City",
    "state": "CA",
    "website": "https://example.edu"
  }
}
```

Tables involved: `universities`.

### POST `/api/universities/compare`

Purpose: Fetch two to five universities in caller-provided order.

Request body example:

```json
{
  "unit_ids": [
    "11111111-1111-1111-1111-111111111111",
    "22222222-2222-2222-2222-222222222222"
  ]
}
```

Response example:

```json
{
  "success": true,
  "data": [
    {
      "university_id": "11111111-1111-1111-1111-111111111111",
      "university_name": "Example State University"
    },
    {
      "university_id": "22222222-2222-2222-2222-222222222222",
      "university_name": "Example Technical University"
    }
  ]
}
```

Tables involved: `universities`.

### GET `/api/programs`

Purpose: List academic programs, optionally filtered by university, degree, or search text.

Request body: none.

Example query:

```text
/api/programs?university_id=11111111-1111-1111-1111-111111111111&degree=Bachelors
```

Response example:

```json
{
  "success": true,
  "data": [
    {
      "program_id": "33333333-3333-3333-3333-333333333333",
      "program_name": "Computer Science",
      "degree": "Bachelors",
      "total_credit_hours": 120,
      "university": {
        "university_id": "11111111-1111-1111-1111-111111111111",
        "university_name": "Example State University"
      }
    }
  ],
  "metadata": {
    "count": 1
  }
}
```

Tables involved: `programs`, `universities`.

### GET `/api/programs/{program_id}`

Purpose: Get one academic program and its catalog course summary.

Request body: none.

Response example:

```json
{
  "success": true,
  "data": {
    "program_id": "33333333-3333-3333-3333-333333333333",
    "program_name": "Computer Science",
    "degree": "Bachelors",
    "total_credit_hours": 120,
    "courses": [
      {
        "course_id": "44444444-4444-4444-4444-444444444444",
        "course_code": "CS 101",
        "course_name": "Introduction to Computer Science",
        "credits": 3
      }
    ]
  }
}
```

Tables involved: `programs`, `universities`, `courses`.

### GET `/api/programs/{program_id}/courses`

Purpose: List courses for one program.

Request body: none.

Response example:

```json
{
  "success": true,
  "data": [
    {
      "course_id": "44444444-4444-4444-4444-444444444444",
      "program_id": "33333333-3333-3333-3333-333333333333",
      "course_code": "CS 101",
      "course_name": "Introduction to Computer Science",
      "credits": 3,
      "recommended_year": 1,
      "recommended_semester": "Fall"
    }
  ],
  "metadata": {
    "count": 1,
    "program_id": "33333333-3333-3333-3333-333333333333"
  }
}
```

Tables involved: `courses`, `programs`, `universities`.

### GET `/api/courses`

Purpose: List catalog courses, optionally filtered by program or search text.

Request body: none.

Example query:

```text
/api/courses?program_id=33333333-3333-3333-3333-333333333333&search=systems
```

Response example:

```json
{
  "success": true,
  "data": [
    {
      "course_id": "44444444-4444-4444-4444-444444444444",
      "program_id": "33333333-3333-3333-3333-333333333333",
      "course_code": "CS 101",
      "course_name": "Introduction to Computer Science",
      "credits": 3
    }
  ],
  "metadata": {
    "count": 1
  }
}
```

Tables involved: `courses`, `programs`, `universities`.

### GET `/api/courses/{course_id}`

Purpose: Get one catalog course, including program, prerequisites, and corequisites.

Request body: none.

Response example:

```json
{
  "success": true,
  "data": {
    "course_id": "44444444-4444-4444-4444-444444444444",
    "program_id": "33333333-3333-3333-3333-333333333333",
    "course_code": "CS 101",
    "course_name": "Introduction to Computer Science",
    "credits": 3,
    "program": {
      "program_id": "33333333-3333-3333-3333-333333333333",
      "program_name": "Computer Science",
      "degree": "Bachelors"
    },
    "prerequisites": [],
    "corequisites": []
  }
}
```

Tables involved: `courses`, `programs`, `universities`, `course_prerequisites`, `course_corequisites`.

### GET `/api/courses/{course_id}/prerequisites`

Purpose: List prerequisite courses for a catalog course.

Request body: none.

Response example:

```json
{
  "success": true,
  "data": [
    {
      "id": "55555555-5555-5555-5555-555555555555",
      "course_id": "66666666-6666-6666-6666-666666666666",
      "prerequisite_course_id": "44444444-4444-4444-4444-444444444444",
      "course": {
        "course_id": "44444444-4444-4444-4444-444444444444",
        "course_code": "CS 101",
        "course_name": "Introduction to Computer Science",
        "credits": 3
      }
    }
  ],
  "metadata": {
    "count": 1,
    "course_id": "66666666-6666-6666-6666-666666666666"
  }
}
```

Tables involved: `course_prerequisites`, `courses`.

### GET `/api/courses/{course_id}/corequisites`

Purpose: List corequisite courses for a catalog course.

Request body: none.

Response example:

```json
{
  "success": true,
  "data": [
    {
      "id": "77777777-7777-7777-7777-777777777777",
      "course_id": "88888888-8888-8888-8888-888888888888",
      "corequisite_course_id": "99999999-9999-9999-9999-999999999999",
      "course": {
        "course_id": "99999999-9999-9999-9999-999999999999",
        "course_code": "CS 101L",
        "course_name": "Introduction to Computer Science Lab",
        "credits": 1
      }
    }
  ],
  "metadata": {
    "count": 1,
    "course_id": "88888888-8888-8888-8888-888888888888"
  }
}
```

Tables involved: `course_corequisites`, `courses`.

### GET `/api/global/countries`

Purpose: List country lookup rows.

Request body: none.

Response example:

```json
[
  {
    "id": 1,
    "name": "United States"
  }
]
```

Tables involved: `countries`.

### GET `/api/global/states/{country_id}`

Purpose: List state lookup rows for a country.

Request body: none.

Response example:

```json
[
  {
    "id": 1,
    "name": "California",
    "country_id": 1
  }
]
```

Tables involved: `states`, `countries`.

## Catalog

### GET `/api/terms`

Purpose: List academic terms.

Request body: none.

Response example:

```json
{
  "success": true,
  "data": [
    {
      "term_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
      "term_name": "Fall 2026",
      "start_date": "2026-08-24",
      "end_date": "2026-12-15",
      "is_active": true
    }
  ],
  "metadata": {
    "count": 1
  }
}
```

Tables involved: `academic_terms`.

### GET `/api/terms/{id}`

Purpose: Get one academic term.

Request body: none.

Response example:

```json
{
  "success": true,
  "data": {
    "term_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "term_name": "Fall 2026",
    "start_date": "2026-08-24",
    "end_date": "2026-12-15",
    "is_active": true
  }
}
```

Tables involved: `academic_terms`.

### GET `/api/courses/{id}/offerings`

Purpose: List term offerings for a course.

Request body: none.

Response example:

```json
{
  "success": true,
  "data": [
    {
      "offering_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
      "course_id": "44444444-4444-4444-4444-444444444444",
      "term_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
      "offering_type": "Lecture"
    }
  ],
  "metadata": {
    "count": 1,
    "course_id": "44444444-4444-4444-4444-444444444444"
  }
}
```

Tables involved: `course_offerings`, `courses`, `academic_terms`.

### GET `/api/offerings/{id}`

Purpose: Get one course offering.

Request body: none.

Response example:

```json
{
  "success": true,
  "data": {
    "offering_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
    "course_id": "44444444-4444-4444-4444-444444444444",
    "term_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "offering_type": "Lecture"
  }
}
```

Tables involved: `course_offerings`, `courses`, `academic_terms`.

### GET `/api/offerings/{id}/sections`

Purpose: List sections for an offering.

Request body: none.

Response example:

```json
{
  "success": true,
  "data": [
    {
      "section_id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
      "offering_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
      "section_number": "001",
      "crn": "12345",
      "campus": "Main",
      "instructor": "Dr. Example",
      "instruction_method": "In Person",
      "capacity": 30,
      "enrolled": 24,
      "status": "Open"
    }
  ],
  "metadata": {
    "count": 1,
    "offering_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
  }
}
```

Tables involved: `sections`, `course_offerings`.

### GET `/api/sections/{id}`

Purpose: Get one section.

Request body: none.

Response example:

```json
{
  "success": true,
  "data": {
    "section_id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
    "offering_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
    "section_number": "001",
    "crn": "12345",
    "instruction_method": "In Person",
    "capacity": 30,
    "enrolled": 24,
    "status": "Open"
  }
}
```

Tables involved: `sections`, `course_offerings`, `courses`, `academic_terms`.

### GET `/api/sections/{id}/meetings`

Purpose: List meetings for a section.

Request body: none.

Response example:

```json
{
  "success": true,
  "data": [
    {
      "meeting_id": "dddddddd-dddd-dddd-dddd-dddddddddddd",
      "section_id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
      "weekday": 1,
      "start_time": "09:00:00",
      "end_time": "10:15:00",
      "building": "ENG",
      "room": "101",
      "meeting_type": "Class"
    }
  ],
  "metadata": {
    "count": 1,
    "section_id": "cccccccc-cccc-cccc-cccc-cccccccccccc"
  }
}
```

Tables involved: `section_meetings`, `sections`.

## Planning

### GET `/api/plans`

Purpose: List normalized plans. Optional filters: `user_id`, `is_active`.

Request body: none.

Response example:

```json
{
  "success": true,
  "data": [
    {
      "plan_id": "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
      "user_id": 1,
      "university_id": "11111111-1111-1111-1111-111111111111",
      "program_id": "33333333-3333-3333-3333-333333333333",
      "plan_name": "CS Graduation Plan",
      "is_active": true,
      "max_term_credits": 18,
      "term_credit_totals": []
    }
  ],
  "metadata": {
    "count": 1
  }
}
```

Tables involved: `ed_plans`, `plan_courses`, `universities`, `programs`, `courses`, `academic_terms`.

### POST `/api/plans`

Purpose: Create a normalized plan.

Request body example:

```json
{
  "user_id": 1,
  "university_id": "11111111-1111-1111-1111-111111111111",
  "program_id": "33333333-3333-3333-3333-333333333333",
  "plan_name": "CS Graduation Plan",
  "description": "Four-year plan",
  "is_active": true
}
```

Response example:

```json
{
  "success": true,
  "data": {
    "plan_id": "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
    "user_id": 1,
    "plan_name": "CS Graduation Plan",
    "is_active": true,
    "courses": [],
    "max_term_credits": 18,
    "term_credit_totals": []
  }
}
```

Tables involved: `ed_plans`, `users`, `universities`, `programs`.

### GET `/api/plans/{plan_id}`

Purpose: Get one normalized plan with courses.

Request body: none.

Response example:

```json
{
  "success": true,
  "data": {
    "plan_id": "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
    "plan_name": "CS Graduation Plan",
    "is_active": true,
    "courses": [],
    "max_term_credits": 18,
    "term_credit_totals": []
  }
}
```

Tables involved: `ed_plans`, `plan_courses`, `universities`, `programs`, `courses`, `academic_terms`.

### PATCH `/api/plans/{plan_id}`

Purpose: Update normalized plan metadata.

Request body example:

```json
{
  "plan_name": "Updated CS Plan",
  "description": "Updated note",
  "is_active": true
}
```

Response example:

```json
{
  "success": true,
  "data": {
    "plan_id": "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
    "plan_name": "Updated CS Plan",
    "description": "Updated note",
    "is_active": true
  }
}
```

Tables involved: `ed_plans`.

### DELETE `/api/plans/{plan_id}`

Purpose: Deactivate a normalized plan. This is a soft delete by setting `is_active` to false.

Request body: none.

Response example:

```json
{
  "success": true,
  "data": {
    "plan_id": "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
    "is_active": false
  }
}
```

Tables involved: `ed_plans`.

### GET `/api/plans/{plan_id}/courses`

Purpose: List courses currently added to a plan.

Request body: none.

Response example:

```json
{
  "success": true,
  "data": [
    {
      "id": "ffffffff-ffff-ffff-ffff-ffffffffffff",
      "plan_id": "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
      "course_id": "44444444-4444-4444-4444-444444444444",
      "planned_term_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
      "status": "Planned",
      "notes": null
    }
  ],
  "metadata": {
    "count": 1,
    "max_term_credits": 18,
    "term_credit_totals": [
      {
        "planned_term_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "term_name": "Fall 2026",
        "credits": 3
      }
    ]
  }
}
```

Tables involved: `ed_plans`, `plan_courses`, `courses`, `academic_terms`.

### POST `/api/plans/{plan_id}/courses`

Purpose: Add a course to a normalized plan.

Request body example:

```json
{
  "course_id": "44444444-4444-4444-4444-444444444444",
  "planned_term_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "status": "Planned",
  "notes": "Take first year"
}
```

Response example:

```json
{
  "success": true,
  "data": {
    "id": "ffffffff-ffff-ffff-ffff-ffffffffffff",
    "plan_id": "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
    "course_id": "44444444-4444-4444-4444-444444444444",
    "planned_term_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "status": "Planned",
    "notes": "Take first year"
  },
  "metadata": {
    "max_term_credits": 18
  }
}
```

Tables involved: `plan_courses`, `ed_plans`, `courses`, `academic_terms`.

### PATCH `/api/plans/{plan_id}/courses/{course_id}`

Purpose: Update a course already in a normalized plan.

Request body example:

```json
{
  "planned_term_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "status": "In Progress",
  "notes": "Moved to fall"
}
```

Response example:

```json
{
  "success": true,
  "data": {
    "id": "ffffffff-ffff-ffff-ffff-ffffffffffff",
    "plan_id": "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
    "course_id": "44444444-4444-4444-4444-444444444444",
    "planned_term_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "status": "In Progress",
    "notes": "Moved to fall"
  },
  "metadata": {
    "max_term_credits": 18
  }
}
```

Tables involved: `plan_courses`, `ed_plans`, `courses`, `academic_terms`.

### DELETE `/api/plans/{plan_id}/courses/{course_id}`

Purpose: Remove a course from a normalized plan.

Request body: none.

Response example:

```json
{
  "success": true,
  "data": null,
  "metadata": {
    "plan_id": "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
    "course_id": "44444444-4444-4444-4444-444444444444"
  }
}
```

Tables involved: `plan_courses`.

### POST `/api/users/education-plan`

Purpose: Legacy compatibility route to save or replace a JSON-backed education plan.

Request body example:

```json
{
  "emailaddress": "student@example.com",
  "degree": "Bachelors",
  "program": [
    {
      "program": "Computer Science",
      "university": "Example State University",
      "year": "1",
      "semester": "Fall",
      "code": "CS 101",
      "courseName": "Introduction to Computer Science",
      "credits": 3
    }
  ]
}
```

Response example:

```json
{
  "success": true,
  "message": "Education plan saved",
  "data": {
    "program": [
      {
        "program": "Computer Science",
        "university": "Example State University",
        "code": "CS 101"
      }
    ],
    "degree": "Bachelors"
  }
}
```

Tables involved: `users`, `education_plans`, `program_courses`.

### POST `/api/users/education-plan/query`

Purpose: Legacy compatibility route to fetch one JSON-backed education plan.

Request body example:

```json
{
  "email": "student@example.com",
  "programname": "Computer Science",
  "univerityname": "Example State University",
  "degree": "Bachelors"
}
```

Response example:

```json
{
  "success": true,
  "message": "Plan retrieved",
  "data": {
    "program": [],
    "degree": "Bachelors"
  }
}
```

Tables involved: `education_plans`, `users`.

### POST `/api/users/education-plan/list`

Purpose: Legacy compatibility route to list JSON-backed education plans for a user email.

Request body example:

```json
{
  "email": "student@example.com"
}
```

Response example:

```json
{
  "success": true,
  "message": "Plans loaded",
  "data": [
    {
      "program": [],
      "degree": "Bachelors"
    }
  ]
}
```

Tables involved: `education_plans`, `users`.

### POST `/api/users/education-plan/delete`

Purpose: Legacy compatibility route to delete one JSON-backed education plan.

Request body example:

```json
{
  "email": "student@example.com",
  "programname": "Computer Science",
  "univerityname": "Example State University",
  "degree": "Bachelors"
}
```

Response example:

```json
{
  "success": true,
  "message": "Education plan deleted",
  "data": null
}
```

Tables involved: `education_plans`, `program_courses`, `course_schedules`, `users`.

### POST `/api/users/education-plan/reschedule`

Purpose: Legacy compatibility route to queue reschedule preferences. It does not generate a schedule.

Request body example:

```json
{
  "emailaddress": "student@example.com",
  "reschedule": [
    {
      "day": "Monday",
      "fromtime": "09:00",
      "totime": "11:00"
    }
  ]
}
```

Response example:

```json
{
  "success": true,
  "message": "Reschedule request queued",
  "data": {
    "reschedule": [
      {
        "day": "Monday",
        "fromtime": "09:00",
        "totime": "11:00"
      }
    ]
  }
}
```

Tables involved: `users`, `course_reschedules`.

## Validation

### POST `/api/plans/{plan_id}/validate`

Purpose: Validate the full current normalized plan.

Request body example:

```json
{}
```

Response example:

```json
{
  "success": true,
  "data": {
    "plan_id": "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
    "is_valid": false,
    "issues": [
      {
        "severity": "error",
        "code": "TERM_CREDIT_LIMIT_EXCEEDED",
        "message": "Fall 2026 has 21 planned credits, which exceeds the 18-credit limit.",
        "course_id": "44444444-4444-4444-4444-444444444444",
        "course_code": "CS 101",
        "planned_term_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "metadata": {
          "term_credits": 21,
          "max_term_credits": 18,
          "over_by": 3
        }
      }
    ],
    "summary": {
      "error_count": 1,
      "warning_count": 0,
      "recommendation_count": 0
    }
  }
}
```

Tables involved: `ed_plans`, `plan_courses`, `courses`, `course_prerequisites`, `course_corequisites`, `academic_terms`.

### POST `/api/plans/{plan_id}/validate-course`

Purpose: Validate a candidate add or update before saving it.

Request body example:

```json
{
  "course_id": "44444444-4444-4444-4444-444444444444",
  "planned_term_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "status": "Planned",
  "operation": "add"
}
```

Response example:

```json
{
  "success": true,
  "data": {
    "plan_id": "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
    "is_valid": true,
    "issues": [],
    "summary": {
      "error_count": 0,
      "warning_count": 0,
      "recommendation_count": 0
    }
  }
}
```

Tables involved: `ed_plans`, `plan_courses`, `courses`, `course_prerequisites`, `course_corequisites`, `academic_terms`.

## Graduation Audit

### GET `/api/plans/{plan_id}/audit`

Purpose: Report graduation progress for a normalized plan against its selected program catalog.

Request body: none.

Response example:

```json
{
  "plan_id": "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
  "program": {
    "program_id": "33333333-3333-3333-3333-333333333333",
    "program_name": "Computer Science",
    "degree": "Bachelors",
    "required_credits": 120
  },
  "credits": {
    "planned": 30,
    "required": 120,
    "remaining": 90,
    "completion_percentage": 25.0
  },
  "courses": {
    "total_required": 40,
    "completed": 10,
    "missing": 30,
    "completion_percentage": 25.0
  },
  "graduation_ready": false,
  "missing_courses": [
    {
      "course_id": "66666666-6666-6666-6666-666666666666",
      "course_code": "CS 201",
      "course_name": "Data Structures"
    }
  ]
}
```

Tables involved: `ed_plans`, `plan_courses`, `programs`, `courses`.

## Supporting Endpoints Outside The Core Workflow

These endpoints are implemented but are not part of the requested discovery -> plan -> validate -> audit flow.

### GET `/`

Purpose: Basic API status endpoint.

Request body: none.

Response example:

```json
{
  "success": true,
  "message": "EduPlan API is running",
  "data": {
    "name": "EduPlan API",
    "version": "1.0.0"
  }
}
```

Tables involved: none.

### POST `/api/users`

Purpose: Register a user and return a bearer token.

Request body example:

```json
{
  "email": "student@example.com",
  "password": "secret123",
  "first_name": "Student",
  "last_name": "Example",
  "phone_number": "555-0100"
}
```

Response example:

```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "bearer_token": "jwt-token",
    "profile": {
      "id": 1,
      "email": "student@example.com"
    }
  }
}
```

Tables involved: `users`.

### POST `/api/users/login`

Purpose: Authenticate a user and return a bearer token.

Request body example:

```json
{
  "email": "student@example.com",
  "password": "secret123"
}
```

Response example:

```json
{
  "success": true,
  "message": "You are logged in successfully.",
  "data": {
    "bearer_token": "jwt-token",
    "role": "customer",
    "first_name": "Student",
    "last_name": "Example"
  }
}
```

Tables involved: `users`.

### POST `/api/users/email-verification/request`

Purpose: Disabled email-verification stub.

Request body example:

```json
{
  "email": "student@example.com"
}
```

Response example:

```json
{
  "success": true,
  "message": "Email verification is disabled. You can continue signup.",
  "data": {
    "email": "student@example.com"
  }
}
```

Tables involved: none.

### GET `/api/users/email-verification/status`

Purpose: Disabled email-verification status stub.

Request body: none.

Example query:

```text
/api/users/email-verification/status?email=student@example.com
```

Response example:

```json
{
  "success": true,
  "message": "Verification status retrieved",
  "data": {
    "verified": true,
    "email": "student@example.com"
  }
}
```

Tables involved: none.

### POST `/api/users/email-advisor`

Purpose: Send or hand off an advisor email notification.

Request body example:

```json
{
  "email": "student@example.com",
  "advisorEmail": "advisor@example.edu",
  "body": "Please review my plan.",
  "phone": "555-0100"
}
```

Response example:

```json
{
  "success": true,
  "message": "Advisor notified",
  "data": null
}
```

Tables involved: none.

### POST `/api/intake`

Purpose: Persist raw intake form submission data.

Request body example:

```json
{
  "email": "student@example.com",
  "intended_program": "Computer Science",
  "start_term": "Fall 2026"
}
```

Response example:

```json
{
  "success": true,
  "message": "Saved",
  "data": {
    "id": 1
  }
}
```

Tables involved: `intake_submissions`.
