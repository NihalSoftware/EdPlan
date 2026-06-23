from __future__ import annotations

from app.orchestrator.modules.base_module import BaseModule
from app.orchestrator.schemas.module_response import ModuleResponse
from app.orchestrator.schemas.student_context import StudentContext

EXAMPLE_MODULE = "ExampleModule"


class ExampleModule(BaseModule):
    """Reference module showing the official orchestrator integration contract."""

    name = EXAMPLE_MODULE

    async def execute(self, context: StudentContext, query: str) -> ModuleResponse:
        return ModuleResponse(
            module_name=self.name,
            content="ExampleModule executed through the orchestrator.",
            data={
                "context_loaded": context.user is not None or context.plan is not None,
                "query_received": bool(query.strip()),
            },
            metadata={"reference_module": True},
        )
