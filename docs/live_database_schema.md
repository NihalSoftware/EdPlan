# Live Database Schema

Source of truth: live PostgreSQL database reached through `DATABASE_URL` in `fastapi_backend/.env`. This document was generated from PostgreSQL catalog tables, not from SQLAlchemy metadata or checked-in migrations.

Generated on: 2026-06-10

## Database Overview

- Database: `edplan_db`
- Current schema: `public`
- PostgreSQL server: `18.3 (Debian 18.3-1.pgdg12+1)`
- Server encoding: `UTF8`
- Server time zone: `UTC`
- User schemas: `public`
- User-schema relations: 28 tables and 2 views/materialized views
- Alembic live version: `0008`

Catalog comments: PostgreSQL has no `pg_description` comments on the application tables/columns in this database. Table descriptions below are inferred from table names, columns, foreign keys, and checked-in backend usage.

Estimated row counts shown per table come from `pg_class.reltuples`; `-1` means PostgreSQL has not collected usable planner statistics for that relation yet.

Extensions:

| Extension | Version | Schema |
| --- | --- | --- |
| `pg_stat_statements` | `1.12` | `public` |
| `pgcrypto` | `1.4` | `public` |
| `plpgsql` | `1.0` | `pg_catalog` |

User-defined types:

| Type | Kind | Definition |
| --- | --- | --- |
| `public.userrole` | enum | admin, customer |

Sequences:

| Sequence | Type | Owned By | Increment | Min | Max | Cycle |
| --- | --- | --- | --- | --- | --- | --- |
| `public.countries_id_seq` | integer | `public.countries.id` | 1 | 1 | 2147483647 | False |
| `public.course_reschedules_id_seq` | integer | `public.course_reschedules.id` | 1 | 1 | 2147483647 | False |
| `public.course_schedules_id_seq` | integer | `public.course_schedules.id` | 1 | 1 | 2147483647 | False |
| `public.customers_id_seq` | integer | `public.customers.id` | 1 | 1 | 2147483647 | False |
| `public.education_plans_id_seq` | integer | `public.education_plans.id` | 1 | 1 | 2147483647 | False |
| `public.email_otps_id_seq` | integer | `public.email_otps.id` | 1 | 1 | 2147483647 | False |
| `public.intake_submissions_id_seq` | integer | `public.intake_submissions.id` | 1 | 1 | 2147483647 | False |
| `public.program_courses_id_seq` | integer | `public.program_courses.id` | 1 | 1 | 2147483647 | False |
| `public.states_id_seq` | integer | `public.states.id` | 1 | 1 | 2147483647 | False |
| `public.users_id_seq` | integer | `public.users.id` | 1 | 1 | 2147483647 | False |

Triggers: none found outside PostgreSQL internal triggers.

Views in user schema:

| View | Type | Notes |
| --- | --- | --- |
| `public.pg_stat_statements` | view | Extension-provided statistics view |
| `public.pg_stat_statements_info` | view | Extension-provided statistics view |

## Entity Hierarchy

Primary live entity groups:

- Identity and audit: `users` owns `login_history`, legacy `education_plans`, legacy `course_reschedules`, and normalized `ed_plans`.
- Legacy planning: `education_plans` -> `program_courses` -> `course_schedules`; plan payloads are also stored as JSON on `education_plans.payload`.
- Normalized catalog: `universities` -> `programs` -> `courses` -> `course_offerings` -> `sections` -> `section_meetings`.
- Academic calendar: `academic_terms` anchors `course_offerings`.
- Normalized planning: `ed_plans` -> `plan_courses`, `plan_sections`, and `plan_schedules`; `ed_plans` also points to `users`, `universities`, and `programs`.
- Career mapping: `careers` is joined to `programs` through `program_careers` and to `courses` through `course_careers`.
- Course rules: `course_prerequisites` and `course_corequisites` are self-referential joins on `courses`.
- Global lookups: `countries` -> `states`.
- Standalone operational tables: `intake_submissions`, `email_otps`, and `alembic_version`.

## Relationships

- `public.course_careers(career_id)` -> `public.careers(career_id)` via `course_careers_career_fk`; on update `CASCADE`, on delete `CASCADE`.
- `public.course_careers(course_id)` -> `public.courses(course_id)` via `course_careers_course_fk`; on update `CASCADE`, on delete `CASCADE`.
- `public.course_corequisites(corequisite_course_id)` -> `public.courses(course_id)` via `course_corequisites_corequisite_fk`; on update `CASCADE`, on delete `RESTRICT`.
- `public.course_corequisites(course_id)` -> `public.courses(course_id)` via `course_corequisites_course_fk`; on update `CASCADE`, on delete `CASCADE`.
- `public.course_offerings(course_id)` -> `public.courses(course_id)` via `course_offerings_course_fk`; on update `CASCADE`, on delete `RESTRICT`.
- `public.course_offerings(term_id)` -> `public.academic_terms(term_id)` via `course_offerings_term_fk`; on update `CASCADE`, on delete `RESTRICT`.
- `public.course_prerequisites(course_id)` -> `public.courses(course_id)` via `course_prerequisites_course_fk`; on update `CASCADE`, on delete `CASCADE`.
- `public.course_prerequisites(prerequisite_course_id)` -> `public.courses(course_id)` via `course_prerequisites_prerequisite_fk`; on update `CASCADE`, on delete `RESTRICT`.
- `public.course_reschedules(user_id)` -> `public.users(id)` via `course_reschedules_user_id_fkey`; on update `NO ACTION`, on delete `CASCADE`.
- `public.course_schedules(course_id)` -> `public.program_courses(id)` via `course_schedules_course_id_fkey`; on update `NO ACTION`, on delete `SET NULL`.
- `public.course_schedules(education_plan_id)` -> `public.education_plans(id)` via `course_schedules_education_plan_id_fkey`; on update `NO ACTION`, on delete `CASCADE`.
- `public.courses(program_id)` -> `public.programs(program_id)` via `courses_program_fk`; on update `CASCADE`, on delete `RESTRICT`.
- `public.customers(user_id)` -> `public.users(id)` via `customers_user_id_fkey`; on update `NO ACTION`, on delete `CASCADE`.
- `public.ed_plans(legacy_education_plan_id)` -> `public.education_plans(id)` via `ed_plans_legacy_education_plan_fk`; on update `CASCADE`, on delete `SET NULL`.
- `public.ed_plans(program_id, university_id)` -> `public.programs(program_id, university_id)` via `ed_plans_program_university_fk`; on update `CASCADE`, on delete `RESTRICT`.
- `public.ed_plans(university_id)` -> `public.universities(university_id)` via `ed_plans_university_fk`; on update `CASCADE`, on delete `RESTRICT`.
- `public.ed_plans(user_id)` -> `public.users(id)` via `ed_plans_user_fk`; on update `CASCADE`, on delete `CASCADE`.
- `public.education_plans(user_id)` -> `public.users(id)` via `education_plans_user_id_fkey`; on update `NO ACTION`, on delete `CASCADE`.
- `public.login_history(user_id)` -> `public.users(id)` via `login_history_user_fk`; on update `CASCADE`, on delete `CASCADE`.
- `public.plan_courses(course_id)` -> `public.courses(course_id)` via `plan_courses_course_fk`; on update `CASCADE`, on delete `RESTRICT`.
- `public.plan_courses(plan_id)` -> `public.ed_plans(plan_id)` via `plan_courses_plan_fk`; on update `CASCADE`, on delete `CASCADE`.
- `public.plan_courses(planned_term_id)` -> `public.academic_terms(term_id)` via `plan_courses_planned_term_fk`; on update `CASCADE`, on delete `SET NULL`.
- `public.plan_schedules(plan_id)` -> `public.ed_plans(plan_id)` via `plan_schedules_plan_fk`; on update `CASCADE`, on delete `CASCADE`.
- `public.plan_sections(plan_id)` -> `public.ed_plans(plan_id)` via `plan_sections_plan_fk`; on update `CASCADE`, on delete `CASCADE`.
- `public.plan_sections(section_id)` -> `public.sections(section_id)` via `plan_sections_section_fk`; on update `CASCADE`, on delete `RESTRICT`.
- `public.program_careers(career_id)` -> `public.careers(career_id)` via `program_careers_career_fk`; on update `CASCADE`, on delete `CASCADE`.
- `public.program_careers(program_id)` -> `public.programs(program_id)` via `program_careers_program_fk`; on update `CASCADE`, on delete `CASCADE`.
- `public.program_courses(education_plan_id)` -> `public.education_plans(id)` via `program_courses_education_plan_id_fkey`; on update `NO ACTION`, on delete `CASCADE`.
- `public.programs(university_id)` -> `public.universities(university_id)` via `programs_university_fk`; on update `CASCADE`, on delete `RESTRICT`.
- `public.section_meetings(section_id)` -> `public.sections(section_id)` via `section_meetings_section_fk`; on update `CASCADE`, on delete `CASCADE`.
- `public.sections(offering_id)` -> `public.course_offerings(offering_id)` via `sections_offering_fk`; on update `CASCADE`, on delete `CASCADE`.
- `public.states(country_id)` -> `public.countries(id)` via `states_country_id_fkey`; on update `NO ACTION`, on delete `CASCADE`.

## Table Schemas

### `public.academic_terms`

Description: Academic calendar terms used to anchor course offerings.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: -1.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `term_id` | `uuid` | no | `gen_random_uuid()` | PK |
| 2 | `term_name` | `character varying(80)` | no | `-` | - |
| 3 | `start_date` | `date` | no | `-` | - |
| 4 | `end_date` | `date` | no | `-` | - |
| 5 | `is_active` | `boolean` | no | `true` | - |

Primary key: `academic_terms_pkey` on `(term_id)`.

Unique constraints:
- `academic_terms_name_uk`: `UNIQUE (term_name)`

Check constraints:
- `academic_terms_date_chk`: `CHECK (start_date < end_date)`

Foreign keys: none.

Indexes:
- `academic_terms_name_uk`: `CREATE UNIQUE INDEX academic_terms_name_uk ON public.academic_terms USING btree (term_name)` (unique).
- `academic_terms_pkey`: `CREATE UNIQUE INDEX academic_terms_pkey ON public.academic_terms USING btree (term_id)` (primary, unique).
- `idx_academic_terms_is_active`: `CREATE INDEX idx_academic_terms_is_active ON public.academic_terms USING btree (is_active)`.

### `public.alembic_version`

Description: Alembic migration state table. It is metadata, not an application entity.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: -1.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `version_num` | `character varying(32)` | no | `-` | PK |

Primary key: `alembic_version_pkc` on `(version_num)`.

Unique constraints: none.

Check constraints: none.

Foreign keys: none.

Indexes:
- `alembic_version_pkc`: `CREATE UNIQUE INDEX alembic_version_pkc ON public.alembic_version USING btree (version_num)` (primary, unique).

### `public.careers`

Description: Career/outcome catalog used by program and course career mappings.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: -1.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `career_id` | `uuid` | no | `gen_random_uuid()` | PK |
| 2 | `career_name` | `character varying(160)` | no | `-` | - |
| 3 | `career_description` | `text` | yes | `-` | - |
| 4 | `industry` | `character varying(120)` | no | `-` | - |
| 5 | `career_level` | `character varying(40)` | no | `-` | - |
| 6 | `average_salary` | `numeric(12,2)` | yes | `-` | - |
| 7 | `growth_rate` | `character varying(80)` | yes | `-` | - |

Primary key: `careers_pkey` on `(career_id)`.

Unique constraints:
- `careers_name_uk`: `UNIQUE (career_name)`

Check constraints:
- `careers_average_salary_chk`: `CHECK (average_salary IS NULL OR average_salary >= 0::numeric)`
- `careers_level_chk`: `CHECK (career_level::text = ANY (ARRAY['Entry'::character varying, 'Associate'::character varying, 'Mid'::character varying, 'Senior'::character varying]::text[]))`

Foreign keys: none.

Indexes:
- `careers_name_uk`: `CREATE UNIQUE INDEX careers_name_uk ON public.careers USING btree (career_name)` (unique).
- `careers_pkey`: `CREATE UNIQUE INDEX careers_pkey ON public.careers USING btree (career_id)` (primary, unique).
- `idx_careers_industry`: `CREATE INDEX idx_careers_industry ON public.careers USING btree (industry)`.

### `public.countries`

Description: Country lookup table used by global data endpoints.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: -1.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `id` | `integer` | no | `nextval('countries_id_seq'::regclass)` | PK |
| 2 | `name` | `character varying(128)` | no | `-` | - |

Primary key: `countries_pkey` on `(id)`.

Unique constraints:
- `countries_name_key`: `UNIQUE (name)`

Check constraints: none.

Foreign keys: none.

Indexes:
- `countries_name_key`: `CREATE UNIQUE INDEX countries_name_key ON public.countries USING btree (name)` (unique).
- `countries_pkey`: `CREATE UNIQUE INDEX countries_pkey ON public.countries USING btree (id)` (primary, unique).

### `public.course_careers`

Description: Many-to-many join between normalized courses and careers with a relevance score.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: -1.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `id` | `uuid` | no | `gen_random_uuid()` | PK |
| 2 | `course_id` | `uuid` | no | `-` | FK -> public.courses(course_id) |
| 3 | `career_id` | `uuid` | no | `-` | FK -> public.careers(career_id) |
| 4 | `relevance_score` | `integer` | no | `80` | - |

Primary key: `course_careers_pkey` on `(id)`.

Unique constraints:
- `course_careers_pair_uk`: `UNIQUE (course_id, career_id)`

Check constraints:
- `course_careers_relevance_score_chk`: `CHECK (relevance_score >= 0 AND relevance_score <= 100)`

Foreign keys:
- `course_careers_career_fk`: `(career_id)` -> `public.careers(career_id)`; on update `CASCADE`, on delete `CASCADE`.
- `course_careers_course_fk`: `(course_id)` -> `public.courses(course_id)`; on update `CASCADE`, on delete `CASCADE`.

Indexes:
- `course_careers_pair_uk`: `CREATE UNIQUE INDEX course_careers_pair_uk ON public.course_careers USING btree (course_id, career_id)` (unique).
- `course_careers_pkey`: `CREATE UNIQUE INDEX course_careers_pkey ON public.course_careers USING btree (id)` (primary, unique).
- `idx_course_careers_career_id`: `CREATE INDEX idx_course_careers_career_id ON public.course_careers USING btree (career_id)`.
- `idx_course_careers_course_id`: `CREATE INDEX idx_course_careers_course_id ON public.course_careers USING btree (course_id)`.

### `public.course_corequisites`

Description: Self-referential course dependency table for courses that must be taken together.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: -1.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `id` | `uuid` | no | `gen_random_uuid()` | PK |
| 2 | `course_id` | `uuid` | no | `-` | FK -> public.courses(course_id) |
| 3 | `corequisite_course_id` | `uuid` | no | `-` | FK -> public.courses(course_id) |

Primary key: `course_corequisites_pkey` on `(id)`.

Unique constraints:
- `course_corequisites_pair_uk`: `UNIQUE (course_id, corequisite_course_id)`

Check constraints:
- `course_corequisites_not_self_chk`: `CHECK (course_id <> corequisite_course_id)`

Foreign keys:
- `course_corequisites_corequisite_fk`: `(corequisite_course_id)` -> `public.courses(course_id)`; on update `CASCADE`, on delete `RESTRICT`.
- `course_corequisites_course_fk`: `(course_id)` -> `public.courses(course_id)`; on update `CASCADE`, on delete `CASCADE`.

Indexes:
- `course_corequisites_pair_uk`: `CREATE UNIQUE INDEX course_corequisites_pair_uk ON public.course_corequisites USING btree (course_id, corequisite_course_id)` (unique).
- `course_corequisites_pkey`: `CREATE UNIQUE INDEX course_corequisites_pkey ON public.course_corequisites USING btree (id)` (primary, unique).
- `idx_course_corequisites_corequisite_course_id`: `CREATE INDEX idx_course_corequisites_corequisite_course_id ON public.course_corequisites USING btree (corequisite_course_id)`.
- `idx_course_corequisites_course_id`: `CREATE INDEX idx_course_corequisites_course_id ON public.course_corequisites USING btree (course_id)`.

### `public.course_offerings`

Description: Term-specific availability of a normalized course.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: -1.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `offering_id` | `uuid` | no | `gen_random_uuid()` | PK |
| 2 | `course_id` | `uuid` | no | `-` | FK -> public.courses(course_id) |
| 3 | `term_id` | `uuid` | no | `-` | FK -> public.academic_terms(term_id) |
| 4 | `offering_type` | `character varying(30)` | no | `-` | - |

Primary key: `course_offerings_pkey` on `(offering_id)`.

Unique constraints:
- `course_offerings_course_term_type_uk`: `UNIQUE (course_id, term_id, offering_type)`

Check constraints:
- `course_offerings_type_chk`: `CHECK (offering_type::text = ANY (ARRAY['Lecture'::character varying, 'Lab'::character varying, 'Lecture+Lab'::character varying, 'Online'::character varying]::text[]))`

Foreign keys:
- `course_offerings_course_fk`: `(course_id)` -> `public.courses(course_id)`; on update `CASCADE`, on delete `RESTRICT`.
- `course_offerings_term_fk`: `(term_id)` -> `public.academic_terms(term_id)`; on update `CASCADE`, on delete `RESTRICT`.

Indexes:
- `course_offerings_course_term_type_uk`: `CREATE UNIQUE INDEX course_offerings_course_term_type_uk ON public.course_offerings USING btree (course_id, term_id, offering_type)` (unique).
- `course_offerings_pkey`: `CREATE UNIQUE INDEX course_offerings_pkey ON public.course_offerings USING btree (offering_id)` (primary, unique).
- `idx_course_offerings_course_id`: `CREATE INDEX idx_course_offerings_course_id ON public.course_offerings USING btree (course_id)`.
- `idx_course_offerings_term_id`: `CREATE INDEX idx_course_offerings_term_id ON public.course_offerings USING btree (term_id)`.

### `public.course_prerequisites`

Description: Self-referential course dependency table for prerequisite rules.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: -1.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `id` | `uuid` | no | `gen_random_uuid()` | PK |
| 2 | `course_id` | `uuid` | no | `-` | FK -> public.courses(course_id) |
| 3 | `prerequisite_course_id` | `uuid` | no | `-` | FK -> public.courses(course_id) |

Primary key: `course_prerequisites_pkey` on `(id)`.

Unique constraints:
- `course_prerequisites_pair_uk`: `UNIQUE (course_id, prerequisite_course_id)`

Check constraints:
- `course_prerequisites_not_self_chk`: `CHECK (course_id <> prerequisite_course_id)`

Foreign keys:
- `course_prerequisites_course_fk`: `(course_id)` -> `public.courses(course_id)`; on update `CASCADE`, on delete `CASCADE`.
- `course_prerequisites_prerequisite_fk`: `(prerequisite_course_id)` -> `public.courses(course_id)`; on update `CASCADE`, on delete `RESTRICT`.

Indexes:
- `course_prerequisites_pair_uk`: `CREATE UNIQUE INDEX course_prerequisites_pair_uk ON public.course_prerequisites USING btree (course_id, prerequisite_course_id)` (unique).
- `course_prerequisites_pkey`: `CREATE UNIQUE INDEX course_prerequisites_pkey ON public.course_prerequisites USING btree (id)` (primary, unique).
- `idx_course_prerequisites_course_id`: `CREATE INDEX idx_course_prerequisites_course_id ON public.course_prerequisites USING btree (course_id)`.
- `idx_course_prerequisites_prerequisite_course_id`: `CREATE INDEX idx_course_prerequisites_prerequisite_course_id ON public.course_prerequisites USING btree (prerequisite_course_id)`.

### `public.course_reschedules`

Description: Legacy JSON queue of user course reschedule requests.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: -1.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `id` | `integer` | no | `nextval('course_reschedules_id_seq'::regclass)` | PK |
| 2 | `user_id` | `integer` | yes | `-` | FK -> public.users(id) |
| 3 | `requested_at` | `timestamp with time zone` | yes | `now()` | - |
| 4 | `payload` | `json` | no | `-` | - |

Primary key: `course_reschedules_pkey` on `(id)`.

Unique constraints: none.

Check constraints: none.

Foreign keys:
- `course_reschedules_user_id_fkey`: `(user_id)` -> `public.users(id)`; on update `NO ACTION`, on delete `CASCADE`.

Indexes:
- `course_reschedules_pkey`: `CREATE UNIQUE INDEX course_reschedules_pkey ON public.course_reschedules USING btree (id)` (primary, unique).

### `public.course_schedules`

Description: Legacy generated schedule rows linked to legacy education plans and legacy program_courses.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: -1.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `id` | `integer` | no | `nextval('course_schedules_id_seq'::regclass)` | PK |
| 2 | `education_plan_id` | `integer` | yes | `-` | FK -> public.education_plans(id) |
| 3 | `course_id` | `integer` | yes | `-` | FK -> public.program_courses(id) |
| 4 | `day` | `character varying(32)` | yes | `-` | - |
| 5 | `time` | `character varying(32)` | yes | `-` | - |
| 6 | `available` | `boolean` | yes | `true` | - |

Primary key: `course_schedules_pkey` on `(id)`.

Unique constraints: none.

Check constraints: none.

Foreign keys:
- `course_schedules_course_id_fkey`: `(course_id)` -> `public.program_courses(id)`; on update `NO ACTION`, on delete `SET NULL`.
- `course_schedules_education_plan_id_fkey`: `(education_plan_id)` -> `public.education_plans(id)`; on update `NO ACTION`, on delete `CASCADE`.

Indexes:
- `course_schedules_pkey`: `CREATE UNIQUE INDEX course_schedules_pkey ON public.course_schedules USING btree (id)` (primary, unique).

### `public.courses`

Description: Normalized course catalog records under programs.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: -1.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `course_id` | `uuid` | no | `gen_random_uuid()` | PK |
| 2 | `program_id` | `uuid` | no | `-` | FK -> public.programs(program_id) |
| 3 | `course_code` | `character varying(40)` | no | `-` | - |
| 4 | `course_name` | `character varying(255)` | no | `-` | - |
| 5 | `credits` | `integer` | no | `-` | - |
| 6 | `lecture_hours` | `integer` | no | `0` | - |
| 7 | `lab_hours` | `integer` | no | `0` | - |
| 8 | `recommended_year` | `integer` | yes | `-` | - |
| 9 | `recommended_semester` | `character varying(20)` | yes | `-` | - |
| 10 | `description` | `text` | yes | `-` | - |

Primary key: `courses_pkey` on `(course_id)`.

Unique constraints:
- `courses_program_code_uk`: `UNIQUE (program_id, course_code)`

Check constraints:
- `courses_credits_chk`: `CHECK (credits > 0)`
- `courses_hours_chk`: `CHECK (lecture_hours >= 0 AND lab_hours >= 0)`
- `courses_recommended_semester_chk`: `CHECK (recommended_semester IS NULL OR (recommended_semester::text = ANY (ARRAY['Fall'::character varying, 'Spring'::character varying, 'Summer'::character varying, 'Winter'::character varying]::text[])))`
- `courses_recommended_year_chk`: `CHECK (recommended_year IS NULL OR recommended_year >= 1 AND recommended_year <= 8)`

Foreign keys:
- `courses_program_fk`: `(program_id)` -> `public.programs(program_id)`; on update `CASCADE`, on delete `RESTRICT`.

Indexes:
- `courses_pkey`: `CREATE UNIQUE INDEX courses_pkey ON public.courses USING btree (course_id)` (primary, unique).
- `courses_program_code_uk`: `CREATE UNIQUE INDEX courses_program_code_uk ON public.courses USING btree (program_id, course_code)` (unique).
- `idx_courses_course_code`: `CREATE INDEX idx_courses_course_code ON public.courses USING btree (course_code)`.
- `idx_courses_program_id`: `CREATE INDEX idx_courses_program_id ON public.courses USING btree (program_id)`.

### `public.customers`

Description: Optional customer profile details keyed by user_id.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: -1.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `id` | `integer` | no | `nextval('customers_id_seq'::regclass)` | PK |
| 2 | `user_id` | `integer` | yes | `-` | FK -> public.users(id) |
| 3 | `company_name` | `character varying(150)` | yes | `-` | - |
| 4 | `title` | `character varying(150)` | yes | `-` | - |
| 5 | `notes` | `character varying(4000)` | yes | `-` | - |
| 6 | `created_at` | `timestamp with time zone` | yes | `now()` | - |

Primary key: `customers_pkey` on `(id)`.

Unique constraints: none.

Check constraints: none.

Foreign keys:
- `customers_user_id_fkey`: `(user_id)` -> `public.users(id)`; on update `NO ACTION`, on delete `CASCADE`.

Indexes:
- `customers_pkey`: `CREATE UNIQUE INDEX customers_pkey ON public.customers USING btree (id)` (primary, unique).

### `public.ed_plans`

Description: Normalized education plan root linking a user to a university and program.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: -1.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `plan_id` | `uuid` | no | `gen_random_uuid()` | PK |
| 2 | `user_id` | `integer` | no | `-` | FK -> public.users(id) |
| 3 | `university_id` | `uuid` | no | `-` | FK -> public.programs(program_id, university_id); FK -> public.universities(university_id) |
| 4 | `program_id` | `uuid` | no | `-` | FK -> public.programs(program_id, university_id) |
| 5 | `plan_name` | `character varying(160)` | no | `-` | - |
| 6 | `description` | `text` | yes | `-` | - |
| 7 | `is_active` | `boolean` | no | `true` | - |
| 8 | `created_at` | `timestamp with time zone` | no | `now()` | - |
| 9 | `updated_at` | `timestamp with time zone` | no | `now()` | - |
| 10 | `legacy_education_plan_id` | `integer` | yes | `-` | FK -> public.education_plans(id) |

Primary key: `ed_plans_pkey` on `(plan_id)`.

Unique constraints:
- `ed_plans_user_name_uk`: `UNIQUE (user_id, plan_name)`

Check constraints: none.

Foreign keys:
- `ed_plans_legacy_education_plan_fk`: `(legacy_education_plan_id)` -> `public.education_plans(id)`; on update `CASCADE`, on delete `SET NULL`.
- `ed_plans_program_university_fk`: `(program_id, university_id)` -> `public.programs(program_id, university_id)`; on update `CASCADE`, on delete `RESTRICT`.
- `ed_plans_university_fk`: `(university_id)` -> `public.universities(university_id)`; on update `CASCADE`, on delete `RESTRICT`.
- `ed_plans_user_fk`: `(user_id)` -> `public.users(id)`; on update `CASCADE`, on delete `CASCADE`.

Indexes:
- `ed_plans_pkey`: `CREATE UNIQUE INDEX ed_plans_pkey ON public.ed_plans USING btree (plan_id)` (primary, unique).
- `ed_plans_user_name_uk`: `CREATE UNIQUE INDEX ed_plans_user_name_uk ON public.ed_plans USING btree (user_id, plan_name)` (unique).
- `idx_ed_plans_legacy_education_plan_id`: `CREATE UNIQUE INDEX idx_ed_plans_legacy_education_plan_id ON public.ed_plans USING btree (legacy_education_plan_id)` (unique).
- `idx_ed_plans_program_id`: `CREATE INDEX idx_ed_plans_program_id ON public.ed_plans USING btree (program_id)`.
- `idx_ed_plans_university_id`: `CREATE INDEX idx_ed_plans_university_id ON public.ed_plans USING btree (university_id)`.
- `idx_ed_plans_user_id`: `CREATE INDEX idx_ed_plans_user_id ON public.ed_plans USING btree (user_id)`.

### `public.education_plans`

Description: Legacy education plan root storing denormalized/generated plan payload JSON.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: 20.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `id` | `integer` | no | `nextval('education_plans_id_seq'::regclass)` | PK |
| 2 | `user_id` | `integer` | yes | `-` | FK -> public.users(id) |
| 3 | `program_name` | `character varying(256)` | no | `-` | - |
| 4 | `university_name` | `character varying(256)` | no | `-` | - |
| 5 | `payload` | `json` | no | `-` | - |
| 6 | `created_at` | `timestamp with time zone` | yes | `now()` | - |
| 7 | `updated_at` | `timestamp with time zone` | yes | `now()` | - |
| 8 | `degree` | `character varying(128)` | yes | `-` | - |

Primary key: `education_plans_pkey` on `(id)`.

Unique constraints: none.

Check constraints: none.

Foreign keys:
- `education_plans_user_id_fkey`: `(user_id)` -> `public.users(id)`; on update `NO ACTION`, on delete `CASCADE`.

Indexes:
- `education_plans_pkey`: `CREATE UNIQUE INDEX education_plans_pkey ON public.education_plans USING btree (id)` (primary, unique).

### `public.email_otps`

Description: Email one-time-password/verification attempts keyed by email address.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: -1.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `id` | `integer` | no | `nextval('email_otps_id_seq'::regclass)` | PK |
| 2 | `email` | `character varying(256)` | no | `-` | - |
| 3 | `code_hash` | `character varying(128)` | no | `-` | - |
| 4 | `attempts` | `integer` | no | `0` | - |
| 5 | `created_at` | `timestamp with time zone` | yes | `now()` | - |
| 6 | `expires_at` | `timestamp with time zone` | no | `-` | - |
| 7 | `verified_at` | `timestamp with time zone` | yes | `-` | - |
| 8 | `consumed_at` | `timestamp with time zone` | yes | `-` | - |

Primary key: `email_otps_pkey` on `(id)`.

Unique constraints: none.

Check constraints: none.

Foreign keys: none.

Indexes:
- `email_otps_pkey`: `CREATE UNIQUE INDEX email_otps_pkey ON public.email_otps USING btree (id)` (primary, unique).
- `ix_email_otps_email`: `CREATE INDEX ix_email_otps_email ON public.email_otps USING btree (email)`.
- `ix_email_otps_expires_at`: `CREATE INDEX ix_email_otps_expires_at ON public.email_otps USING btree (expires_at)`.

### `public.intake_submissions`

Description: Raw onboarding intake payload submissions.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: 54.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `id` | `integer` | no | `nextval('intake_submissions_id_seq'::regclass)` | PK |
| 2 | `submitted_at` | `timestamp with time zone` | no | `now()` | - |
| 3 | `payload` | `json` | no | `-` | - |

Primary key: `intake_submissions_pkey` on `(id)`.

Unique constraints: none.

Check constraints: none.

Foreign keys: none.

Indexes:
- `intake_submissions_pkey`: `CREATE UNIQUE INDEX intake_submissions_pkey ON public.intake_submissions USING btree (id)` (primary, unique).
- `ix_intake_submissions_submitted_at`: `CREATE INDEX ix_intake_submissions_submitted_at ON public.intake_submissions USING btree (submitted_at)`.

### `public.login_history`

Description: Login audit/history records for users.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: -1.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `login_id` | `uuid` | no | `gen_random_uuid()` | PK |
| 2 | `user_id` | `integer` | no | `-` | FK -> public.users(id) |
| 3 | `login_time` | `timestamp with time zone` | no | `now()` | - |
| 4 | `logout_time` | `timestamp with time zone` | yes | `-` | - |
| 5 | `ip_address` | `character varying(45)` | yes | `-` | - |
| 6 | `status` | `character varying(30)` | no | `-` | - |

Primary key: `login_history_pkey` on `(login_id)`.

Unique constraints: none.

Check constraints:
- `login_history_logout_after_login_chk`: `CHECK (logout_time IS NULL OR logout_time >= login_time)`
- `login_history_status_chk`: `CHECK (status::text = ANY (ARRAY['Success'::character varying, 'Failed'::character varying, 'Locked'::character varying]::text[]))`

Foreign keys:
- `login_history_user_fk`: `(user_id)` -> `public.users(id)`; on update `CASCADE`, on delete `CASCADE`.

Indexes:
- `idx_login_history_login_time`: `CREATE INDEX idx_login_history_login_time ON public.login_history USING btree (login_time)`.
- `idx_login_history_user_id`: `CREATE INDEX idx_login_history_user_id ON public.login_history USING btree (user_id)`.
- `login_history_pkey`: `CREATE UNIQUE INDEX login_history_pkey ON public.login_history USING btree (login_id)` (primary, unique).

### `public.plan_courses`

Description: Courses selected into a normalized education plan.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: -1.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `id` | `uuid` | no | `gen_random_uuid()` | PK |
| 2 | `plan_id` | `uuid` | no | `-` | FK -> public.ed_plans(plan_id) |
| 3 | `course_id` | `uuid` | no | `-` | FK -> public.courses(course_id) |
| 4 | `planned_term_id` | `uuid` | yes | `-` | FK -> public.academic_terms(term_id) |
| 5 | `status` | `character varying(30)` | no | `'Planned'::character varying` | - |
| 6 | `notes` | `text` | yes | `-` | - |

Primary key: `plan_courses_pkey` on `(id)`.

Unique constraints:
- `plan_courses_plan_course_uk`: `UNIQUE (plan_id, course_id)`

Check constraints:
- `plan_courses_status_chk`: `CHECK (status::text = ANY (ARRAY['Planned'::character varying, 'In Progress'::character varying, 'Completed'::character varying]::text[]))`

Foreign keys:
- `plan_courses_course_fk`: `(course_id)` -> `public.courses(course_id)`; on update `CASCADE`, on delete `RESTRICT`.
- `plan_courses_plan_fk`: `(plan_id)` -> `public.ed_plans(plan_id)`; on update `CASCADE`, on delete `CASCADE`.
- `plan_courses_planned_term_fk`: `(planned_term_id)` -> `public.academic_terms(term_id)`; on update `CASCADE`, on delete `SET NULL`.

Indexes:
- `idx_plan_courses_course_id`: `CREATE INDEX idx_plan_courses_course_id ON public.plan_courses USING btree (course_id)`.
- `idx_plan_courses_plan_id`: `CREATE INDEX idx_plan_courses_plan_id ON public.plan_courses USING btree (plan_id)`.
- `idx_plan_courses_planned_term_id`: `CREATE INDEX idx_plan_courses_planned_term_id ON public.plan_courses USING btree (planned_term_id)`.
- `plan_courses_pkey`: `CREATE UNIQUE INDEX plan_courses_pkey ON public.plan_courses USING btree (id)` (primary, unique).
- `plan_courses_plan_course_uk`: `CREATE UNIQUE INDEX plan_courses_plan_course_uk ON public.plan_courses USING btree (plan_id, course_id)` (unique).

### `public.plan_schedules`

Description: Generated or selected schedule blocks for normalized plan courses.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: -1.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `schedule_id` | `uuid` | no | `gen_random_uuid()` | PK |
| 2 | `plan_id` | `uuid` | no | `-` | FK -> public.ed_plans(plan_id) |
| 3 | `generated_at` | `timestamp with time zone` | no | `now()` | - |
| 4 | `total_credits` | `integer` | no | `0` | - |
| 5 | `status` | `character varying(30)` | no | `'Draft'::character varying` | - |
| 6 | `notes` | `text` | yes | `-` | - |

Primary key: `plan_schedules_pkey` on `(schedule_id)`.

Unique constraints: none.

Check constraints:
- `plan_schedules_status_chk`: `CHECK (status::text = ANY (ARRAY['Draft'::character varying, 'Active'::character varying, 'Final'::character varying, 'Archived'::character varying]::text[]))`
- `plan_schedules_total_credits_chk`: `CHECK (total_credits >= 0)`

Foreign keys:
- `plan_schedules_plan_fk`: `(plan_id)` -> `public.ed_plans(plan_id)`; on update `CASCADE`, on delete `CASCADE`.

Indexes:
- `idx_plan_schedules_plan_id`: `CREATE INDEX idx_plan_schedules_plan_id ON public.plan_schedules USING btree (plan_id)`.
- `plan_schedules_pkey`: `CREATE UNIQUE INDEX plan_schedules_pkey ON public.plan_schedules USING btree (schedule_id)` (primary, unique).
- `ux_plan_schedules_one_active_per_plan`: `CREATE UNIQUE INDEX ux_plan_schedules_one_active_per_plan ON public.plan_schedules USING btree (plan_id) WHERE ((status)::text = 'Active'::text)` (unique). Predicate: `((status)::text = 'Active'::text)`.

### `public.plan_sections`

Description: Sections selected into a normalized education plan.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: -1.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `id` | `uuid` | no | `gen_random_uuid()` | PK |
| 2 | `plan_id` | `uuid` | no | `-` | FK -> public.ed_plans(plan_id) |
| 3 | `section_id` | `uuid` | no | `-` | FK -> public.sections(section_id) |
| 4 | `is_enrolled` | `boolean` | no | `false` | - |
| 5 | `enrollment_status` | `character varying(30)` | no | `'Planned'::character varying` | - |
| 6 | `notes` | `text` | yes | `-` | - |

Primary key: `plan_sections_pkey` on `(id)`.

Unique constraints:
- `plan_sections_plan_section_uk`: `UNIQUE (plan_id, section_id)`

Check constraints:
- `plan_sections_enrollment_status_chk`: `CHECK (enrollment_status::text = ANY (ARRAY['Planned'::character varying, 'Enrolled'::character varying, 'Waitlisted'::character varying, 'Completed'::character varying]::text[]))`

Foreign keys:
- `plan_sections_plan_fk`: `(plan_id)` -> `public.ed_plans(plan_id)`; on update `CASCADE`, on delete `CASCADE`.
- `plan_sections_section_fk`: `(section_id)` -> `public.sections(section_id)`; on update `CASCADE`, on delete `RESTRICT`.

Indexes:
- `idx_plan_sections_plan_id`: `CREATE INDEX idx_plan_sections_plan_id ON public.plan_sections USING btree (plan_id)`.
- `idx_plan_sections_section_id`: `CREATE INDEX idx_plan_sections_section_id ON public.plan_sections USING btree (section_id)`.
- `plan_sections_pkey`: `CREATE UNIQUE INDEX plan_sections_pkey ON public.plan_sections USING btree (id)` (primary, unique).
- `plan_sections_plan_section_uk`: `CREATE UNIQUE INDEX plan_sections_plan_section_uk ON public.plan_sections USING btree (plan_id, section_id)` (unique).

### `public.program_careers`

Description: Many-to-many join between programs and careers.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: -1.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `id` | `uuid` | no | `gen_random_uuid()` | PK |
| 2 | `program_id` | `uuid` | no | `-` | FK -> public.programs(program_id) |
| 3 | `career_id` | `uuid` | no | `-` | FK -> public.careers(career_id) |
| 4 | `relevance_score` | `integer` | no | `80` | - |

Primary key: `program_careers_pkey` on `(id)`.

Unique constraints:
- `program_careers_pair_uk`: `UNIQUE (program_id, career_id)`

Check constraints:
- `program_careers_relevance_score_chk`: `CHECK (relevance_score >= 0 AND relevance_score <= 100)`

Foreign keys:
- `program_careers_career_fk`: `(career_id)` -> `public.careers(career_id)`; on update `CASCADE`, on delete `CASCADE`.
- `program_careers_program_fk`: `(program_id)` -> `public.programs(program_id)`; on update `CASCADE`, on delete `CASCADE`.

Indexes:
- `idx_program_careers_career_id`: `CREATE INDEX idx_program_careers_career_id ON public.program_careers USING btree (career_id)`.
- `idx_program_careers_program_id`: `CREATE INDEX idx_program_careers_program_id ON public.program_careers USING btree (program_id)`.
- `program_careers_pair_uk`: `CREATE UNIQUE INDEX program_careers_pair_uk ON public.program_careers USING btree (program_id, career_id)` (unique).
- `program_careers_pkey`: `CREATE UNIQUE INDEX program_careers_pkey ON public.program_careers USING btree (id)` (primary, unique).

### `public.program_courses`

Description: Legacy flattened course rows under legacy education_plans; distinct from normalized courses.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: 749.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `id` | `integer` | no | `nextval('program_courses_id_seq'::regclass)` | PK |
| 2 | `education_plan_id` | `integer` | yes | `-` | FK -> public.education_plans(id) |
| 3 | `year_label` | `character varying(64)` | yes | `-` | - |
| 4 | `semester_label` | `character varying(64)` | yes | `-` | - |
| 5 | `course_code` | `character varying(64)` | yes | `-` | - |
| 6 | `course_name` | `character varying(256)` | yes | `-` | - |
| 7 | `credits` | `integer` | yes | `-` | - |
| 8 | `prerequisite` | `character varying(256)` | yes | `-` | - |
| 9 | `corequisite` | `character varying(256)` | yes | `-` | - |
| 10 | `schedule` | `json` | yes | `-` | - |

Primary key: `program_courses_pkey` on `(id)`.

Unique constraints: none.

Check constraints: none.

Foreign keys:
- `program_courses_education_plan_id_fkey`: `(education_plan_id)` -> `public.education_plans(id)`; on update `NO ACTION`, on delete `CASCADE`.

Indexes:
- `program_courses_pkey`: `CREATE UNIQUE INDEX program_courses_pkey ON public.program_courses USING btree (id)` (primary, unique).

### `public.programs`

Description: Academic programs offered by universities.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: -1.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `program_id` | `uuid` | no | `gen_random_uuid()` | PK |
| 2 | `university_id` | `uuid` | no | `-` | FK -> public.universities(university_id) |
| 3 | `program_name` | `character varying(255)` | no | `-` | - |
| 4 | `degree` | `character varying(120)` | no | `-` | - |
| 5 | `total_credit_hours` | `integer` | no | `-` | - |

Primary key: `programs_pkey` on `(program_id)`.

Unique constraints:
- `programs_program_university_uk`: `UNIQUE (program_id, university_id)`
- `programs_university_name_degree_uk`: `UNIQUE (university_id, program_name, degree)`

Check constraints:
- `programs_total_credit_hours_chk`: `CHECK (total_credit_hours > 0)`

Foreign keys:
- `programs_university_fk`: `(university_id)` -> `public.universities(university_id)`; on update `CASCADE`, on delete `RESTRICT`.

Indexes:
- `idx_programs_university_id`: `CREATE INDEX idx_programs_university_id ON public.programs USING btree (university_id)`.
- `programs_pkey`: `CREATE UNIQUE INDEX programs_pkey ON public.programs USING btree (program_id)` (primary, unique).
- `programs_program_university_uk`: `CREATE UNIQUE INDEX programs_program_university_uk ON public.programs USING btree (program_id, university_id)` (unique).
- `programs_university_name_degree_uk`: `CREATE UNIQUE INDEX programs_university_name_degree_uk ON public.programs USING btree (university_id, program_name, degree)` (unique).

### `public.section_meetings`

Description: Meeting time/location rows for scheduled sections.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: -1.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `meeting_id` | `uuid` | no | `gen_random_uuid()` | PK |
| 2 | `section_id` | `uuid` | no | `-` | FK -> public.sections(section_id) |
| 3 | `weekday` | `smallint` | yes | `-` | - |
| 4 | `start_time` | `time without time zone` | yes | `-` | - |
| 5 | `end_time` | `time without time zone` | yes | `-` | - |
| 6 | `building` | `character varying(80)` | yes | `-` | - |
| 7 | `room` | `character varying(40)` | yes | `-` | - |
| 8 | `meeting_type` | `character varying(30)` | no | `'Class'::character varying` | - |

Primary key: `section_meetings_pkey` on `(meeting_id)`.

Unique constraints:
- `section_meetings_unique_time_uk`: `UNIQUE NULLS NOT DISTINCT (section_id, weekday, start_time, end_time, meeting_type)`

Check constraints:
- `section_meetings_time_pair_chk`: `CHECK (weekday IS NULL AND start_time IS NULL AND end_time IS NULL OR weekday IS NOT NULL AND start_time IS NOT NULL AND end_time IS NOT NULL AND start_time < end_time)`
- `section_meetings_type_chk`: `CHECK (meeting_type::text = ANY (ARRAY['Class'::character varying, 'Lab'::character varying, 'Exam'::character varying, 'Online Async'::character varying]::text[]))`
- `section_meetings_weekday_chk`: `CHECK (weekday IS NULL OR weekday >= 1 AND weekday <= 7)`

Foreign keys:
- `section_meetings_section_fk`: `(section_id)` -> `public.sections(section_id)`; on update `CASCADE`, on delete `CASCADE`.

Indexes:
- `idx_section_meetings_conflict_lookup`: `CREATE INDEX idx_section_meetings_conflict_lookup ON public.section_meetings USING btree (weekday, start_time, end_time)`.
- `idx_section_meetings_section_id`: `CREATE INDEX idx_section_meetings_section_id ON public.section_meetings USING btree (section_id)`.
- `section_meetings_pkey`: `CREATE UNIQUE INDEX section_meetings_pkey ON public.section_meetings USING btree (meeting_id)` (primary, unique).
- `section_meetings_unique_time_uk`: `CREATE UNIQUE INDEX section_meetings_unique_time_uk ON public.section_meetings USING btree (section_id, weekday, start_time, end_time, meeting_type) NULLS NOT DISTINCT` (unique).

### `public.sections`

Description: Schedulable class sections under course offerings.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: -1.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `section_id` | `uuid` | no | `gen_random_uuid()` | PK |
| 2 | `offering_id` | `uuid` | no | `-` | FK -> public.course_offerings(offering_id) |
| 3 | `section_number` | `character varying(20)` | no | `-` | - |
| 4 | `crn` | `character varying(30)` | no | `-` | - |
| 5 | `campus` | `character varying(120)` | yes | `-` | - |
| 6 | `instructor` | `character varying(150)` | yes | `-` | - |
| 7 | `instruction_method` | `character varying(40)` | no | `'In Person'::character varying` | - |
| 8 | `capacity` | `integer` | no | `-` | - |
| 9 | `enrolled` | `integer` | no | `0` | - |
| 10 | `status` | `character varying(20)` | no | `'Open'::character varying` | - |

Primary key: `sections_pkey` on `(section_id)`.

Unique constraints:
- `sections_crn_uk`: `UNIQUE (crn)`
- `sections_offering_section_uk`: `UNIQUE (offering_id, section_number)`

Check constraints:
- `sections_capacity_chk`: `CHECK (capacity >= 0)`
- `sections_enrolled_chk`: `CHECK (enrolled >= 0 AND enrolled <= capacity)`
- `sections_instruction_method_chk`: `CHECK (instruction_method::text = ANY (ARRAY['In Person'::character varying, 'Online'::character varying, 'Hybrid'::character varying]::text[]))`
- `sections_status_chk`: `CHECK (status::text = ANY (ARRAY['Open'::character varying, 'Closed'::character varying, 'Cancelled'::character varying]::text[]))`

Foreign keys:
- `sections_offering_fk`: `(offering_id)` -> `public.course_offerings(offering_id)`; on update `CASCADE`, on delete `CASCADE`.

Indexes:
- `idx_sections_offering_id`: `CREATE INDEX idx_sections_offering_id ON public.sections USING btree (offering_id)`.
- `idx_sections_offering_status`: `CREATE INDEX idx_sections_offering_status ON public.sections USING btree (offering_id, status)`.
- `idx_sections_status`: `CREATE INDEX idx_sections_status ON public.sections USING btree (status)`.
- `sections_crn_uk`: `CREATE UNIQUE INDEX sections_crn_uk ON public.sections USING btree (crn)` (unique).
- `sections_offering_section_uk`: `CREATE UNIQUE INDEX sections_offering_section_uk ON public.sections USING btree (offering_id, section_number)` (unique).
- `sections_pkey`: `CREATE UNIQUE INDEX sections_pkey ON public.sections USING btree (section_id)` (primary, unique).

### `public.states`

Description: State/region lookup table linked to countries.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: -1.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `id` | `integer` | no | `nextval('states_id_seq'::regclass)` | PK |
| 2 | `name` | `character varying(128)` | no | `-` | - |
| 3 | `country_id` | `integer` | yes | `-` | FK -> public.countries(id) |

Primary key: `states_pkey` on `(id)`.

Unique constraints: none.

Check constraints: none.

Foreign keys:
- `states_country_id_fkey`: `(country_id)` -> `public.countries(id)`; on update `NO ACTION`, on delete `CASCADE`.

Indexes:
- `states_pkey`: `CREATE UNIQUE INDEX states_pkey ON public.states USING btree (id)` (primary, unique).

### `public.universities`

Description: University/institution catalog.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: -1.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `university_id` | `uuid` | no | `gen_random_uuid()` | PK |
| 2 | `university_name` | `character varying(255)` | no | `-` | - |
| 3 | `city` | `character varying(120)` | no | `-` | - |
| 4 | `state` | `character varying(120)` | no | `-` | - |
| 5 | `website` | `character varying(255)` | yes | `-` | - |

Primary key: `universities_pkey` on `(university_id)`.

Unique constraints:
- `universities_name_city_state_uk`: `UNIQUE (university_name, city, state)`

Check constraints: none.

Foreign keys: none.

Indexes:
- `universities_name_city_state_uk`: `CREATE UNIQUE INDEX universities_name_city_state_uk ON public.universities USING btree (university_name, city, state)` (unique).
- `universities_pkey`: `CREATE UNIQUE INDEX universities_pkey ON public.universities USING btree (university_id)` (primary, unique).

### `public.users`

Description: Application users for authentication and ownership of plans/history.

Relation type: table; persistence: permanent; estimated rows from catalog statistics: 35.

Columns:

| # | Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | `id` | `integer` | no | `nextval('users_id_seq'::regclass)` | PK |
| 2 | `email` | `character varying(256)` | no | `-` | - |
| 3 | `password_hash` | `character varying(512)` | no | `-` | - |
| 4 | `first_name` | `character varying(100)` | yes | `-` | - |
| 5 | `last_name` | `character varying(100)` | yes | `-` | - |
| 6 | `phone_number` | `character varying(32)` | yes | `-` | - |
| 7 | `role` | `userrole` | no | `'customer'::userrole` | - |
| 8 | `is_active` | `boolean` | no | `true` | - |
| 9 | `is_deactivated` | `boolean` | no | `false` | - |
| 10 | `last_login_at` | `timestamp with time zone` | yes | `-` | - |
| 11 | `created_at` | `timestamp with time zone` | yes | `now()` | - |
| 12 | `updated_at` | `timestamp with time zone` | yes | `now()` | - |
| 13 | `is_email_verified` | `boolean` | no | `false` | - |

Primary key: `users_pkey` on `(id)`.

Unique constraints:
- `users_email_key`: `UNIQUE (email)`

Check constraints: none.

Foreign keys: none.

Indexes:
- `users_email_key`: `CREATE UNIQUE INDEX users_email_key ON public.users USING btree (email)` (unique).
- `users_pkey`: `CREATE UNIQUE INDEX users_pkey ON public.users USING btree (id)` (primary, unique).

## Backend Coverage Assessment

Assessment is based on checked-in files under `fastapi_backend/app`, not on live database access. `Covered` means there is an active model plus route/repository/service usage. `Partial` means either a model exists without active API usage, or code references only part of the live table behavior.

| Table | SQLAlchemy Model In Repo | Coverage | Evidence |
| --- | --- | --- | --- |
| `public.academic_terms` | no | Not covered | No checked-in SQLAlchemy model, repository, or route found. |
| `public.alembic_version` | no | Metadata | Managed by Alembic only. |
| `public.careers` | no | Not covered | No checked-in SQLAlchemy model, repository, or route found. |
| `public.countries` | yes | Covered | Model: Country. Routes: GET /global/countries. |
| `public.course_careers` | no | Not covered | No checked-in SQLAlchemy model, repository, or route found. |
| `public.course_corequisites` | no | Not covered | No checked-in SQLAlchemy model, repository, or route found. |
| `public.course_offerings` | no | Not covered | No checked-in SQLAlchemy model, repository, or route found. |
| `public.course_prerequisites` | no | Not covered | No checked-in SQLAlchemy model, repository, or route found. |
| `public.course_reschedules` | yes | Covered | Model: CourseReschedule. Route: POST /api/users/education-plan/reschedule. |
| `public.course_schedules` | yes | Partial | Model: CourseSchedule exists, but no active repository or route usage was found. |
| `public.courses` | no | Not covered | No checked-in SQLAlchemy model, repository, or route found. This is the normalized course catalog, not the legacy ProgramCourse model. |
| `public.customers` | yes | Partial | Model: Customer exists, but no active repository or route usage was found. |
| `public.ed_plans` | no | Not covered | No checked-in SQLAlchemy model, repository, or route found for the normalized plan root. |
| `public.education_plans` | yes | Covered | Model: EducationPlan. Routes: /api/users/education-plan, query, list, delete. |
| `public.email_otps` | no | Partial | Migration 0003 creates it, but the current email verification endpoints are disabled and do not read or write this table. |
| `public.intake_submissions` | yes | Covered | Model: IntakeSubmission. Route: POST /api/intake. |
| `public.login_history` | no | Not covered | No checked-in SQLAlchemy model, repository, or route found. |
| `public.plan_courses` | no | Not covered | No checked-in SQLAlchemy model, repository, or route found. |
| `public.plan_schedules` | no | Not covered | No checked-in SQLAlchemy model, repository, or route found. |
| `public.plan_sections` | no | Not covered | No checked-in SQLAlchemy model, repository, or route found. |
| `public.program_careers` | no | Not covered | No checked-in SQLAlchemy model, repository, or route found. |
| `public.program_courses` | yes | Covered | Model: ProgramCourse. Written by education plan service for legacy generated plan courses. |
| `public.programs` | yes | Partial | Model/repository used by /api/programs. Not imported into app.models, so Alembic target_metadata does not include it. |
| `public.section_meetings` | no | Not covered | No checked-in SQLAlchemy model, repository, or route found. |
| `public.sections` | no | Not covered | No checked-in SQLAlchemy model, repository, or route found. |
| `public.states` | yes | Covered | Model: State. Routes: GET /global/states/{country_id}. |
| `public.universities` | yes | Partial | Model/repository relationship used by /api/programs. /api/universities uses College Scorecard, not this table; model is not imported into app.models. |
| `public.users` | yes | Covered | Model: User. Routes: POST /api/users and POST /api/users/login; security dependency reads users by email. Live column `is_email_verified` is not represented in the checked-in User model. |

Coverage summary: the checked-in backend is centered on legacy plan persistence (`education_plans`, `program_courses`, `course_reschedules`), auth (`users`), intake (`intake_submissions`), global lookups (`countries`, `states`), and program browsing (`programs`, `universities`). The live database also contains a newer normalized planning/catalog/scheduling model (`ed_plans`, `plan_courses`, `plan_sections`, `plan_schedules`, `courses`, `course_offerings`, `sections`, `section_meetings`, academic terms, careers, and join tables) that is not represented in the checked-in SQLAlchemy model set or route layer.

Schema drift notes:

- `users.is_email_verified` exists in the live database but is not declared on `app.models.user.User`.
- `customers.user_id` has a live foreign key to `users.id`; the checked-in `Customer` model declares it as a plain integer.
- Several legacy FK columns are nullable in the live database because the migrations did not specify `nullable=False`; rely on the live nullability in this document rather than ORM type hints.
- Discovery models for `universities` and `programs` exist, but they are not imported by `app/models/__init__.py`, so Alembic `target_metadata` does not include them.

## Migration Notes

- Live `public.alembic_version` reports: `0008`.
- Checked-in migration files in this repo report revisions: `0001` (0001_create_core_tables.py), `0002` (0002_create_intake_submissions_table.py), `0003` (0003_add_email_verification.py), `0004` (0004_add_plan_degree.py).
- The live database is ahead of the checked-in migration chain: it is at `0008`, while this repo contains migrations only through `0004`. Revisions `0005` through `0008` are not present in this working tree.
- Treat the live database as authoritative for any follow-up modeling work. Do not infer the current schema from the local Alembic files alone.
- Alembic `target_metadata` currently imports `app.models`, and `app/models/__init__.py` imports only `User`, `Customer`, `EducationPlan`, `ProgramCourse`, `CourseSchedule`, `CourseReschedule`, `Country`, `State`, and `IntakeSubmission`. It does not import the discovery `Program`/`University` models, and it has no models for the normalized live tables. Autogenerate should not be trusted until metadata imports and missing models/migrations are reconciled.
- The live schema intentionally contains both legacy integer-key planning tables and newer UUID-key normalized planning tables. Keep these separate: `education_plans`/`program_courses`/`course_schedules` are legacy, while `ed_plans`/`plan_courses`/`plan_sections`/`plan_schedules` are normalized.
- Several live tables use UUID primary keys with `gen_random_uuid()` defaults. Keep the database-side default when adding ORM models unless there is a deliberate application-side UUID generation strategy.
- `email_otps` exists in the database and has a checked-in migration, but current email verification endpoints are disabled and do not persist OTPs.
