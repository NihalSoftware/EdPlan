# College Comparison

## Purpose

College Comparison helps students compare universities, academic programs, and mapped career paths using only existing EdPlan database information.

## Architecture

- `module.py` adapts comparison tools to the Student Orchestrator module contract.
- `registry.py` registers the module with `ModuleRegistry` under the existing selector alias `College Comparison`.
- `tools/` contains thin tool wrappers for LLM tool calling.
- `services/` validates inputs and formats comparison responses.
- `repositories/` reads existing catalog and optional career mapping tables.
- `api/` exposes backend routes for direct comparison workflows.
- `schemas/` defines request models shared by APIs and tools.

## Available Tools

- `search_universities`
- `compare_universities`
- `search_programs`
- `compare_programs`
- `compare_career_paths`

## Data Sources

Beta V1 uses existing EdPlan data only:

- `universities`
- `programs`
- `courses`
- `careers` when available
- `program_careers` when available
- `course_careers` when available

## Safety Rules

The advisor and services do not invent rankings, tuition, placement rates, acceptance rates, salaries, scholarships, or scores. If a field is unavailable in the EdPlan database, responses state that it is unavailable.

## Beta V1 Limitations

- No external labor market APIs.
- No scraping.
- No generated rankings or recommendation scores.
- Public/private classification is returned only when present in existing data; otherwise it is `None`.
- Duration and program descriptions are returned only when present in existing data; otherwise they are `None`.
