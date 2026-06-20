# Frontend Handoff

Generated: 2026-06-17

## Recommended Implementation Order

1. University search and selection.
2. Program listing filtered by selected university.
3. Course listing for the selected program.
4. Plan creation.
5. Add, list, update, and remove plan courses.
6. Plan validation display.
7. Graduation audit display.
8. Optional catalog details for terms, offerings, sections, and meetings.

Use the normalized `/api/plans` workflow for new frontend work. Treat `/api/users/education-plan*` as legacy compatibility routes.

## Required Endpoints

Minimum workflow:

- `GET /api/universities`
- `GET /api/programs?university_id={university_id}`
- `GET /api/programs/{program_id}/courses`
- `GET /api/courses/{course_id}/prerequisites`
- `GET /api/courses/{course_id}/corequisites`
- `GET /api/terms`
- `POST /api/plans`
- `GET /api/plans?user_id={user_id}`
- `GET /api/plans/{plan_id}`
- `GET /api/plans/{plan_id}/courses`
- `POST /api/plans/{plan_id}/courses`
- `PATCH /api/plans/{plan_id}/courses/{course_id}`
- `DELETE /api/plans/{plan_id}/courses/{course_id}`
- `POST /api/plans/{plan_id}/validate`
- `POST /api/plans/{plan_id}/validate-course`
- `GET /api/plans/{plan_id}/audit`

Optional catalog inspection:

- `GET /api/courses/{id}/offerings`
- `GET /api/offerings/{id}/sections`
- `GET /api/sections/{id}/meetings`

## Example API Flow

1. Search universities:

```text
GET /api/universities?search=state&page=0&per_page=10
```

2. List programs for selected university:

```text
GET /api/programs?university_id={university_id}
```

3. List required courses for selected program:

```text
GET /api/programs/{program_id}/courses
```

4. Load terms for term pickers:

```text
GET /api/terms
```

5. Create a plan:

```json
POST /api/plans
{
  "user_id": 1,
  "university_id": "11111111-1111-1111-1111-111111111111",
  "program_id": "33333333-3333-3333-3333-333333333333",
  "plan_name": "CS Graduation Plan",
  "description": "Four-year plan",
  "is_active": true
}
```

6. Validate a candidate course before adding:

```json
POST /api/plans/{plan_id}/validate-course
{
  "course_id": "44444444-4444-4444-4444-444444444444",
  "planned_term_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "status": "Planned",
  "operation": "add"
}
```

7. Add the course:

```json
POST /api/plans/{plan_id}/courses
{
  "course_id": "44444444-4444-4444-4444-444444444444",
  "planned_term_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "status": "Planned",
  "notes": null
}
```

8. Validate the full plan:

```text
POST /api/plans/{plan_id}/validate
```

9. Run graduation audit:

```text
GET /api/plans/{plan_id}/audit
```

## Common Objects

University:

```json
{
  "university_id": "11111111-1111-1111-1111-111111111111",
  "unit_id": "11111111-1111-1111-1111-111111111111",
  "university_name": "Example State University",
  "name": "Example State University",
  "city": "Example City",
  "state": "CA",
  "website": "https://example.edu"
}
```

Program:

```json
{
  "program_id": "33333333-3333-3333-3333-333333333333",
  "program_name": "Computer Science",
  "degree": "Bachelors",
  "total_credit_hours": 120,
  "university": {}
}
```

Course:

```json
{
  "course_id": "44444444-4444-4444-4444-444444444444",
  "program_id": "33333333-3333-3333-3333-333333333333",
  "course_code": "CS 101",
  "code": "CS 101",
  "course_name": "Introduction to Computer Science",
  "credits": 3,
  "recommended_year": 1,
  "year": 1,
  "recommended_semester": "Fall",
  "semester": "Fall"
}
```

Academic term:

```json
{
  "term_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "term_name": "Fall 2026",
  "start_date": "2026-08-24",
  "end_date": "2026-12-15",
  "is_active": true
}
```

Plan:

```json
{
  "plan_id": "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
  "user_id": 1,
  "university_id": "11111111-1111-1111-1111-111111111111",
  "program_id": "33333333-3333-3333-3333-333333333333",
  "plan_name": "CS Graduation Plan",
  "description": "Four-year plan",
  "is_active": true,
  "max_term_credits": 18,
  "term_credit_totals": [],
  "courses": []
}
```

Plan course:

```json
{
  "id": "ffffffff-ffff-ffff-ffff-ffffffffffff",
  "plan_id": "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
  "course_id": "44444444-4444-4444-4444-444444444444",
  "planned_term_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "status": "Planned",
  "notes": null,
  "course": {},
  "planned_term": {}
}
```

Validation issue:

```json
{
  "severity": "error",
  "code": "PREREQUISITE_NOT_SATISFIED",
  "message": "CS 201 requires CS 101 in an earlier term.",
  "plan_course_id": "ffffffff-ffff-ffff-ffff-ffffffffffff",
  "course_id": "66666666-6666-6666-6666-666666666666",
  "course_code": "CS 201",
  "planned_term_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "planned_term_name": "Fall 2026",
  "related_course_ids": [
    "44444444-4444-4444-4444-444444444444"
  ],
  "related_course_codes": [
    "CS 101"
  ],
  "metadata": {}
}
```

## UUID Fields

Treat these as opaque strings in the frontend:

- `university_id`
- `unit_id`
- `program_id`
- `course_id`
- `term_id`
- `offering_id`
- `section_id`
- `meeting_id`
- `plan_id`
- `plan_courses.id`
- `planned_term_id`
- `prerequisite_course_id`
- `corequisite_course_id`

Non-UUID identifiers:

- `user_id` is an integer.
- Legacy `education_plans.id`, `program_courses.id`, and `course_reschedules.id` are integers.
- `countries.id` and `states.id` are integers.

## Expected Workflow

The frontend should keep the selected `university_id`, `program_id`, `plan_id`, and course IDs in state. Do not derive IDs from display names.

Recommended screen flow:

1. University picker stores `university_id`.
2. Program picker fetches by `university_id` and stores `program_id`.
3. Course browser fetches by `program_id`.
4. Plan creator sends `user_id`, `university_id`, `program_id`, and `plan_name`.
5. Plan editor groups `plan_courses` by `planned_term_id`.
6. Before add/update, call `validate-course` and show blocking issues to the user.
7. After add/update/delete, reload plan courses or the plan detail.
8. Full validation runs on demand or before audit.
9. Audit page shows credits, missing courses, and `graduation_ready`.

Important backend behavior for UI decisions:

- Valid `status` values are `Planned`, `In Progress`, and `Completed`.
- The current maximum term credit value is 18.
- Validation can report credit overloads, prerequisite issues, corequisite issues, and duplicates.
- Adding a course may still succeed even when validation would report an issue.
- Audit counts planned courses as completed until a transcript system exists.
- Schedule generation is not implemented. Section and meeting endpoints are read-only catalog inspection.
