# EdPlan Nexus Integration

EdPlan Nexus now uses a thin API boundary that delegates requests to the existing
`StudentOrchestrator`.

## Request Flow

1. `EdPlanNexusWorkspacePage.jsx` renders the workspace shell.
2. `useNexusChat` owns the session conversation id, message lifecycle, loading,
   retry, and telemetry state.
3. `nexusService.sendMessage` sends `POST /api/nexus/chat` through the shared
   Axios client.
4. `app/api/routes/nexus.py` validates the API contract and delegates to
   `NexusService`.
5. `NexusService` invokes `StudentOrchestrator.run()` and adapts the
   orchestrator `FinalResponse` to the frontend Nexus response contract.

## Integration Points

- Add persistent conversation loading inside `useNexusChat`.
- Add streaming by extending the message model with chunk events.
- Add citations and tool messages through the existing `citations` and
  `toolCalls` fields in `createMessage`.
- Pass a real `context.plan_id` when the active plan is available so the
  orchestrator can use DB-backed module execution and tracing.

## Current Non-Goals

- No new AI logic.
- No LangGraph changes.
- No authentication changes.
- No conversation persistence.
- No streaming.
