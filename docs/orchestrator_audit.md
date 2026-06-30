# Student Orchestrator Audit

## Current Responsibilities

`StudentOrchestrator` is the application service that assembles and runs the existing student orchestration framework. It owns dependency wiring for context loading, intent routing, module selection, module execution, response composition, memory updates, and run/workflow tracking. It does not implement domain business logic directly.

`StudentGraph` is the LangGraph-backed execution pipeline. The graph runs these nodes in order: `ContextLoader`, `IntentRouter`, `ModuleSelector`, `ModuleExecutor`, `ResponseComposer`, and `MemoryManager`.

`ModuleSelector` validates routed module names against the official module list and records which requested modules are unavailable in the `ModuleRegistry`.

`ModuleExecutor` resolves selected module names from `ModuleRegistry`, calls each module's async `execute(context, query)` method, and normalizes timing, success, response, and error metadata.

`PromptRegistry` is an in-memory prompt template registry grouped by prompt category. It includes `academic_planning.default` and `academic_planning.advisor`; the advisor prompt instructs the Academic Planning module to behave like a university academic advisor, use tools when information is required, avoid invented requirements or audit results, and compare aggressive, balanced, and low-risk plan alternatives when sufficient information exists. For acceleration requests it explicitly directs the advisor to determine remaining requirements, prerequisite constraints, and corequisite constraints before ranking options and stating the expected graduation timeline.

`OpenRouterProvider` implements the provider-neutral LLM abstraction for OpenRouter-compatible chat completions. It builds OpenRouter request payloads from `LLMRequest`, parses provider responses into `LLMResponse`, and reads model/API configuration from environment-backed `LLMModelConfig`.

## Current Execution Flow

1. `StudentOrchestrator.run(user_id, plan_id, query)` creates an `EdPlanState`.
2. `ContextLoader` loads `StudentContext` from existing user, plan, program, university, course, preference, and memory data.
3. `IntentRouter` classifies the query and returns an `IntentResult` with target modules.
4. `ModuleSelector` validates the target module names and checks registry availability.
5. `ModuleExecutor` resolves each selected module from `ModuleRegistry` and executes it.
6. For `academic_planning`, the module builds a compact planning summary, exposes only academic planning tools to Qwen, runs a budgeted multi-tool advisor loop, records tool observations, and asks Qwen to reason over those observations before producing the module response.
7. `ResponseComposer` combines successful `ModuleResponse` objects into a `FinalResponse`.
8. `MemoryManager` records durable student memory and preferences when persistence is available.
9. `RunTracker` and `WorkflowTracker` persist run and workflow metadata when a DB session is provided.

## Existing Module Registration Mechanism

Modules implement `BaseModule` and define:

- `name`
- async `execute(context: StudentContext, query: str) -> ModuleResponse`

`ModuleRegistry.register(module)` validates this contract and stores modules by name. The selector and executor use the same registry instance, so selected modules must be registered under the exact routed module name.

Academic Planning is now registered as:

```text
academic_planning
```

with description:

```text
Manage student education plans and graduation pathways.
```

The module exposes only these tools:

```text
create_plan
update_plan
delete_plan
get_plan
add_course
remove_course
move_course
validate_plan
audit_plan
get_remaining_courses
get_course_details
get_prerequisites
get_corequisites
get_program_requirements
get_available_terms
```

The six read-only tools reuse existing services:

- `get_remaining_courses` uses the graduation audit service and returns missing courses, remaining credits, and graduation readiness.
- `get_course_details` uses the discovery course service.
- `get_prerequisites` uses the discovery course service.
- `get_corequisites` uses the discovery course service.
- `get_program_requirements` uses the discovery program service.
- `get_available_terms` uses the scheduling catalog term service.

Academic Planning no longer stops at single rule-based tool selection. The module sends these tool schemas to Qwen, allows zero or more tool calls across multiple iterations, executes requested tools through existing services, appends tool observations, and returns Qwen's final advising response.

## Advisor Reliability

Before calling Qwen, Academic Planning computes a compact planning summary from available context:

```json
{
  "completed_courses": 0,
  "remaining_courses": null,
  "completed_credits": 0,
  "remaining_credits": null,
  "current_plan_courses": 0,
  "current_plan_credits": 0,
  "audit_status": "unknown_until_audit_tool_runs"
}
```

Unknown values remain `null` or explicit unknown states rather than being invented.

The advisor loop has hard budget protection:

```text
max_tool_iterations = 6
max_total_tool_calls = 10
max_same_tool_calls = 2
```

If a limit is reached, the module stops executing tools and asks Qwen for a final response from gathered observations. If critical information is still missing, the prompt instructs Qwen to ask the student rather than guess.

For planning/advising questions, the preferred response structure is:

```text
Summary

Aggressive Plan
- Semester 1
- Semester 2
- Graduation estimate

Balanced Plan
- Semester 1
- Semester 2
- Graduation estimate

Low-Risk Plan
- Semester 1
- Semester 2
- Graduation estimate

Recommended Option
Reasoning
```

This format is not forced for simple CRUD requests.

## Provider Integration

The provider abstraction is `BaseLLMProvider`, with `generate`, `generate_structured`, and `health_check`.

OpenRouter is supported through `OpenRouterProvider`. Required environment variables:

```text
OPENROUTER_API_KEY
```

Optional environment variables:

```text
OPENROUTER_MODEL=qwen/qwen3-7b-plus
OPENROUTER_FALLBACK_MODEL=
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_TEMPERATURE=0.2
OPENROUTER_MAX_TOKENS=1024
OPENROUTER_TIMEOUT=30
```

API keys are not hardcoded. If `OPENROUTER_API_KEY` is missing, the provider reports an unhealthy configured state and refuses network requests.
