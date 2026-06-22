# EdPlan Orchestrator Module Developer Guide

This guide defines the official integration contract for Student Platform modules that run inside the EdPlan Student Orchestrator.

The orchestrator owns workflow coordination. Student modules own domain behavior. Keep those boundaries clear.

## Architecture

The orchestrator workflow is:

```text
ContextLoader
  -> IntentRouter
  -> ModuleSelector
  -> ModuleExecutor
  -> ResponseComposer
  -> MemoryManager
```

Modules are not called directly by API routes. They are selected by intent, resolved from `ModuleRegistry`, executed by `ModuleExecutor`, and merged into a `FinalResponse` by `ResponseComposer`.

## Required Interface

Every module must inherit from `BaseModule`:

```python
from app.orchestrator.modules.base_module import BaseModule
from app.orchestrator.schemas.module_response import ModuleResponse
from app.orchestrator.schemas.student_context import StudentContext


class MyModule(BaseModule):
    name = "Official Module Name"

    async def execute(self, context: StudentContext, query: str) -> ModuleResponse:
        return ModuleResponse(
            module_name=self.name,
            content="Module response text.",
            data={},
            metadata={},
        )
```

Required:

- `name`: non-empty string.
- `execute()`: async method.
- Return type: `ModuleResponse`.

The registry rejects objects that do not implement `BaseModule`, modules without valid names, and modules with non-async `execute()` methods. The executor marks a module execution as failed if `execute()` returns anything other than `ModuleResponse`.

## Reference Module

`ExampleModule` is available as a reference implementation:

```python
from app.orchestrator.modules.example_module import ExampleModule
```

It demonstrates orchestrator integration only. It does not contain academic, scheduling, career, finance, academic success, or college comparison logic.

## Registration Process

Register modules during application startup or test setup:

```python
from app.orchestrator.modules.module_registry import ModuleRegistry
from app.orchestrator.modules.example_module import ExampleModule

registry = ModuleRegistry()
registry.register(ExampleModule())
```

Then pass the registry to the orchestrator:

```python
orchestrator = StudentOrchestrator(module_registry=registry)
```

The registry supports discovery:

```python
registry.list_modules()
registry.exists("ExampleModule")
registry.get("ExampleModule")
```

## Selection Requirements

`ModuleSelector` only selects official module names. If a new production module name is introduced, add it to the official module list in `module_selector.py`.

Current official production module names:

- `Academic Planning`
- `Scheduling`
- `Career`
- `Finance`
- `Academic Success`
- `College Comparison`

Reference integration module:

- `ExampleModule`

## Execution Lifecycle

For each selected module:

1. `ModuleExecutor` resolves the module from `ModuleRegistry`.
2. The module receives `StudentContext` and the original user query.
3. The module returns `ModuleResponse`.
4. Execution time is recorded in `ModuleExecutionResult`.
5. Exceptions are captured as failed module results.
6. `ResponseComposer` combines successful module responses.

Modules should treat `StudentContext` as read-only. Do not mutate orchestrator state inside modules.

## Common Mistakes

Avoid:

- Returning `dict` instead of `ModuleResponse`.
- Using a sync `execute()` method.
- Registering duplicate module names.
- Embedding API route logic in a module.
- Writing cross-domain business logic inside the orchestrator.
- Mutating `StudentContext`.
- Raising exceptions for expected domain outcomes.

Prefer:

- Return structured failure or warning data in `ModuleResponse.metadata`.
- Keep domain logic inside the module package.
- Add focused unit tests for module behavior.
- Add orchestration tests only for integration boundaries.

## Testing Requirements

Each module should include:

- Unit tests for module logic.
- Contract test confirming `execute()` returns `ModuleResponse`.
- Registry test confirming the module can be registered.
- Orchestrator integration test with a test-only intent router targeting the module.

Minimal integration test shape:

```python
registry = ModuleRegistry()
registry.register(MyModule())

orchestrator = StudentOrchestrator(
    context_loader=FakeContextLoader(),
    intent_router=TestIntentRouter(target_modules=[MyModule.name]),
    module_registry=registry,
)

response = await orchestrator.run(user_id=1, plan_id=plan_id, query="test")
assert response.message in {"success", "partial_success", "failure"}
```

## Boundary Rules

Modules may:

- Read `StudentContext`.
- Use injected domain services.
- Return `ModuleResponse`.

Modules must not:

- Create API endpoints.
- Call OpenRouter directly.
- Manage orchestrator memory directly.
- Write workflow events directly.
- Modify module selection rules at runtime.

The orchestrator remains the coordination layer. Modules remain domain workers.
