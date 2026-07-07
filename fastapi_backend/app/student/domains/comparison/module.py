from __future__ import annotations

import json
from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.orchestrator.llm import (
    BaseLLMProvider,
    LLMMessage,
    LLMProviderError,
    LLMRequest,
    OpenRouterProvider,
)
from app.orchestrator.modules.base_module import BaseModule
from app.orchestrator.schemas.module_response import ModuleResponse
from app.orchestrator.schemas.student_context import StudentContext
from app.student.domains.comparison.services.comparison_service import (
    ComparisonService,
    comparison_service,
)
from app.student.domains.comparison.tools.registry import COMPARISON_TOOLS

MODULE_NAME = "college_comparison"
MODULE_DESCRIPTION = "Help students compare universities and academic programs using existing EdPlan data."

COMPARISON_ADVISOR_PROMPT = (
    "You are EdPlan's UniversityAdvisor. Explain deterministic university and "
    "program comparison results produced from the EdPlan database. Never invent "
    "tuition, transfer agreements, rankings, acceptance rates, salaries, or "
    "university facts. If a field is unavailable, state that it is unavailable. "
    "Recommend only from the ranked recommendations provided."
)

SUPPORTED_TOOL_NAMES = {
    "search_universities",
    "compare_universities",
    "search_programs",
    "compare_programs",
    "compare_career_paths",
}


def get_tools():
    return COMPARISON_TOOLS


class CollegeComparisonModule(BaseModule):
    """Orchestrator module adapter for UniversityAdvisor comparison workflows."""

    name = MODULE_NAME
    description = MODULE_DESCRIPTION

    def __init__(
        self,
        db: AsyncSession | None = None,
        tools: list[Any] | None = None,
        llm_provider: BaseLLMProvider | None = None,
        service: ComparisonService | None = None,
        max_tool_iterations: int = 6,
        max_total_tool_calls: int = 10,
        max_same_tool_calls: int = 3,
    ) -> None:
        self.db = db
        self.tools = {tool.name: tool for tool in tools or get_tools()}
        self.llm_provider = llm_provider or OpenRouterProvider()
        self.service = service or comparison_service
        self.max_tool_iterations = max_tool_iterations
        self.max_total_tool_calls = max_total_tool_calls
        self.max_same_tool_calls = max_same_tool_calls

    async def execute(self, context: StudentContext, query: str) -> ModuleResponse:
        if self.db is None:
            return self._clarification_response(["database_session"])

        student_context = self._student_context_payload(context)
        comparison = await self.service.build_advising_comparison(
            self.db,
            student_context=student_context,
            query=query,
        )
        if comparison["summary"]["status"] == "needs_context":
            return self._needs_context_response(comparison)

        advisor_content, llm_status = await self._advisor_response(comparison, query)
        content = advisor_content or _fallback_response(comparison)
        return ModuleResponse(
            module_name=self.name,
            content=content,
            data={
                "comparison_plan": jsonable_encoder(comparison),
                "comparison_summary": comparison["summary"],
            },
            confidence=0.82 if comparison["validation"]["status"] == "valid" else 0.68,
            metadata={
                "description": self.description,
                "advisor_prompt": "comparison.advisor",
                "llm_status": llm_status,
                "status": (
                    "completed_with_warnings"
                    if comparison["warnings"]
                    else "completed"
                ),
                "warnings": comparison["warnings"],
                "available_tools": self.available_tool_names,
                "deterministic_comparison": True,
            },
        )

    def _clarification_response(self, missing: list[str]) -> ModuleResponse:
        readable = ", ".join(item.replace("_", " ") for item in missing)
        return ModuleResponse(
            module_name=self.name,
            content=(
                "I can compare universities once the required comparison context is "
                f"available. I still need: {readable}."
            ),
            data={"missing_context": missing},
            confidence=0.35,
            metadata={
                "description": self.description,
                "status": "needs_context",
                "warnings": [],
                "deterministic_comparison": True,
            },
        )

    def _needs_context_response(self, comparison: dict[str, Any]) -> ModuleResponse:
        return ModuleResponse(
            module_name=self.name,
            content=(
                "I can compare universities, but I need at least two universities or "
                "a specific program focus first. For example: compare NNMC vs Santa "
                "Fe Community College for Computer Science."
            ),
            data={"comparison_plan": comparison, "missing_context": comparison["validation"].get("missing", [])},
            confidence=0.4,
            metadata={
                "description": self.description,
                "status": "needs_context",
                "warnings": comparison["warnings"],
                "deterministic_comparison": True,
            },
        )

    async def _advisor_response(
        self,
        comparison: dict[str, Any],
        query: str,
    ) -> tuple[str | None, str]:
        payload = {
            "student_context": comparison["student_context"],
            "comparison_results": {
                "summary": comparison["summary"],
                "recommended_university": comparison["recommended_university"],
                "comparison_table": comparison["comparison_table"],
                "ranked_recommendations": comparison["ranked_recommendations"],
                "validation": comparison["validation"],
                "warnings": comparison["warnings"],
            },
            "student_query": query,
        }
        try:
            response = await self.llm_provider.generate(
                LLMRequest(
                    messages=[
                        LLMMessage(
                            role="user",
                            content=(
                                "Explain this UniversityAdvisor recommendation using only "
                                "the structured comparison results. Do not invent facts.\n\n"
                                f"{json.dumps(jsonable_encoder(payload))}"
                            ),
                        )
                    ],
                    system_prompt=COMPARISON_ADVISOR_PROMPT,
                    tools=[],
                    temperature=0.2,
                    max_tokens=1200,
                    metadata={"module": self.name, "mode": "structured_comparison"},
                )
            )
        except LLMProviderError:
            return None, "unavailable"
        except Exception:
            return None, "failed"
        if not response.content:
            return None, "empty"
        return response.content, "ok"

    @staticmethod
    def _student_context_payload(context: StudentContext) -> dict[str, Any]:
        return {
            "user": context.user,
            "plan": context.plan,
            "program": context.program,
            "university": context.university,
            "completed_courses": context.completed_courses,
            "preferences": context.preferences,
            "career_goal": context.career_goal,
            "orchestrator_outputs": context.orchestrator_outputs,
        }

    @property
    def available_tool_names(self) -> list[str]:
        return [tool.name for tool in get_tools()]

    @property
    def tool_schemas(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
            for tool in get_tools()
            if tool.name in SUPPORTED_TOOL_NAMES
        ]


def _fallback_response(comparison: dict[str, Any]) -> str:
    recommended = comparison.get("recommended_university") or {}
    summary = comparison["summary"]
    lines = [
        (
            f"I compared {summary['university_count']} universities"
            f"{' for ' + summary['program_focus'] if summary.get('program_focus') else ''}."
        )
    ]
    if recommended:
        lines.append(
            f"Recommended option: {recommended['university_name']} "
            f"(score {recommended['score']})."
        )
        if recommended.get("reasons"):
            lines.append("Why: " + "; ".join(recommended["reasons"][:3]) + ".")
    if comparison.get("warnings"):
        lines.append("Warnings: " + " ".join(comparison["warnings"][:2]))
    if comparison.get("recommendations"):
        lines.append("Next step: " + comparison["recommendations"][0])
    return "\n".join(lines)
