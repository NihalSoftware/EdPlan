from __future__ import annotations

from uuid import uuid4

import pytest

from app.orchestrator.schemas.intent_result import IntentResult
from app.orchestrator.schemas.module_response import FinalResponse, ModuleResponse
from app.services.nexus_service import NexusChatRequest, NexusService


class FakeOrchestrator:
    async def run(self, user_id, plan_id, query):
        return FinalResponse(
            message=f"handled: {query}",
            module_responses=[
                ModuleResponse(
                    module_name="academic_planning",
                    content="Plan generated.",
                    confidence=0.91,
                )
            ],
            metadata={
                "intent": IntentResult(
                    intent="academic_planning",
                    confidence=0.82,
                    target_modules=["academic_planning"],
                ).model_dump()
            },
        )


@pytest.mark.asyncio
async def test_nexus_service_adapts_orchestrator_response(monkeypatch):
    import app.services.nexus_service as nexus_service_module

    monkeypatch.setattr(nexus_service_module, "StudentOrchestrator", lambda db=None: FakeOrchestrator())

    response = await NexusService().send_message(
        NexusChatRequest(
            message="Create a plan.",
            conversation_id="conversation-1",
            student_id="7",
            context={"plan_id": str(uuid4())},
        )
    )

    assert response.conversation_id == "conversation-1"
    assert response.response == "handled: Create a plan."
    assert response.current_intent == "academic_planning"
    assert response.confidence == 0.82
    assert response.activated_modules == ["academic_planning"]
    assert response.workflow[-1].status == "Completed"


@pytest.mark.asyncio
async def test_nexus_service_generates_conversation_id(monkeypatch):
    import app.services.nexus_service as nexus_service_module

    monkeypatch.setattr(nexus_service_module, "StudentOrchestrator", lambda db=None: FakeOrchestrator())

    response = await NexusService().send_message(
        NexusChatRequest(message="Compare universities.", student_id=1)
    )

    assert response.conversation_id
    assert response.response == "handled: Compare universities."
