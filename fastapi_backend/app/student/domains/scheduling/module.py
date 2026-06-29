from __future__ import annotations

from app.orchestrator.modules.base_module import BaseModule
from app.orchestrator.schemas.module_response import ModuleResponse
from app.orchestrator.schemas.student_context import StudentContext
from app.student.domains.scheduling.schemas.decision import (
    DecisionStatus,
    ScheduleDecisionRequest,
    ScheduleDecisionResult,
)
from app.student.domains.scheduling.services.decision_service import ScheduleDecisionService
from app.student.domains.scheduling.schemas.session import StartSessionRequest
from app.student.domains.scheduling.services.session_service import (
    SchedulingSessionService,
    scheduling_session_service,
)
from app.student.domains.scheduling.engine import (
    CandidateGenerator,
    CandidateValidationService,
    ScheduleMetricsService,
    PreferenceScoringService,
    ScheduleRankingService,
)
from app.student.domains.scheduling.services.retrieval_service import (
    SchedulePilotRetrievalService,
    schedulepilot_retrieval_service,
)

MODULE_NAME = "scheduling"
MODULE_DESCRIPTION = "Build and explain student course schedules."
MODULE_VERSION = "0.9.0"
IMPLEMENTATION_PHASE = "Phase D2"


class SchedulePilotModule(BaseModule):
    """Orchestrator module shell for SchedulePilot scheduling workflows."""

    name = MODULE_NAME
    description = MODULE_DESCRIPTION

    def __init__(
        self,
        db=None,
        retrieval_service: SchedulePilotRetrievalService | None = None,
        candidate_generator: CandidateGenerator | None = None,
        validation_service: CandidateValidationService | None = None,
        metrics_service: ScheduleMetricsService | None = None,
        scoring_service: PreferenceScoringService | None = None,
        ranking_service: ScheduleRankingService | None = None,
        decision_service: ScheduleDecisionService | None = None,
        session_service: SchedulingSessionService | None = None,
    ) -> None:
        self.db = db
        self.retrieval_service = retrieval_service or schedulepilot_retrieval_service
        self.candidate_generator = candidate_generator or CandidateGenerator()
        self.validation_service = validation_service or CandidateValidationService()
        self.metrics_service = metrics_service or ScheduleMetricsService()
        self.scoring_service = scoring_service or PreferenceScoringService()
        self.ranking_service = ranking_service or ScheduleRankingService()
        self.decision_service = decision_service or ScheduleDecisionService(
            retrieval_service=self.retrieval_service,
            candidate_generator=self.candidate_generator,
            validation_service=self.validation_service,
            metrics_service=self.metrics_service,
            scoring_service=self.scoring_service,
            ranking_service=self.ranking_service,
        )
        self.session_service = session_service or scheduling_session_service

    async def execute(self, context: StudentContext, query: str) -> ModuleResponse:
        """Retrieve scheduling context and generate deterministic candidates."""
        if self.db is None:
            return ModuleResponse(
                module_name=self.name,
                content="Scheduling retrieval requires a database session.",
                data={},
                confidence=0.0,
                metadata={
                    "description": self.description,
                    "module_version": MODULE_VERSION,
                    "implementation_phase": IMPLEMENTATION_PHASE,
                    "status": DecisionStatus.FAILED,
                    "error": "database_session_required",
                },
            )

        user = context.user or {}
        plan = context.plan or {}
        user_id = user.get("id")
        plan_id = plan.get("plan_id")
        if not isinstance(user_id, int):
            return ModuleResponse(
                module_name=self.name,
                content="Scheduling retrieval requires a loaded user and plan context.",
                data={},
                confidence=0.0,
                metadata={
                    "description": self.description,
                    "module_version": MODULE_VERSION,
                    "implementation_phase": IMPLEMENTATION_PHASE,
                    "status": DecisionStatus.FAILED,
                    "error": "student_context_required",
                },
            )

        session = self.session_service.create_session(
            StartSessionRequest(
                user_id=user_id,
                plan_id=str(plan_id) if plan_id else None,
                term_id=plan.get("term_id") or plan.get("selected_term_id"),
                query=query,
                preferences=[],
            )
        )
        decision = await self.decision_service.decide_and_generate(
            self.db,
            ScheduleDecisionRequest(
                user_id=user_id,
                plan_id=str(plan_id) if plan_id else None,
                term_id=plan.get("term_id") or plan.get("selected_term_id"),
                query=query,
                preferences=context.preferences,
            ),
        )
        session = self.session_service.apply_decision(session.state.session_id, decision)
        return _decision_response(self, decision, query, session=session)


def _decision_response(
    module: SchedulePilotModule,
    decision: ScheduleDecisionResult,
    query: str,
    *,
    session=None,
):
    data = {
        "decision": decision.model_dump(
            mode="json",
            exclude={
                "retrieval_context",
                "ranking_result",
                "scored_candidates",
            },
        )
    }
    if session is not None:
        data["session"] = session.model_dump(mode="json")
    counts = {
        "courses": 0,
        "terms": 0,
        "offerings": 0,
        "sections": 0,
        "meetings": 0,
        "candidates": 0,
        "scored_candidates": 0,
        "ranked_options": 0,
        "feasible_candidates": 0,
        "infeasible_candidates": 0,
    }
    if decision.retrieval_context is not None:
        retrieval_data = decision.retrieval_context.model_dump(mode="json")
        data.update(retrieval_data)
        counts.update(
            {
                "courses": len(decision.retrieval_context.courses),
                "terms": len(decision.retrieval_context.terms),
                "offerings": len(decision.retrieval_context.offerings),
                "sections": len(decision.retrieval_context.sections),
                "meetings": len(decision.retrieval_context.meetings),
            }
        )
    if decision.ranking_result is not None:
        data["candidates"] = list(decision.scored_candidates)
        data["validated_candidates"] = data["candidates"]
        data["scored_candidates"] = data["candidates"]
        data["ranked_options"] = [
            option.model_dump(mode="json") for option in decision.ranking_result.options
        ]
        data["top_option"] = (
            decision.ranking_result.top_option.model_dump(mode="json")
            if decision.ranking_result.top_option is not None
            else None
        )
        data["ranking_metadata"] = decision.ranking_result.metadata.model_dump(mode="json")
        counts["candidates"] = len(decision.scored_candidates)
        counts["scored_candidates"] = len(decision.scored_candidates)
        counts["ranked_options"] = len(decision.ranking_result.options)
        counts["feasible_candidates"] = decision.ranking_result.metadata.feasible_candidates
    else:
        data["candidates"] = []
        data["validated_candidates"] = []
        data["scored_candidates"] = []
        data["ranked_options"] = []
        data["top_option"] = None
        data["ranking_metadata"] = {}
    if decision.generation_metadata is not None:
        data["generation_metadata"] = decision.generation_metadata
    if decision.validation_metadata is not None:
        data["validation_metadata"] = decision.validation_metadata
        counts["feasible_candidates"] = decision.validation_metadata.get("feasible_count", 0)
        counts["infeasible_candidates"] = decision.validation_metadata.get("infeasible_count", 0)
    if decision.metrics_metadata is not None:
        data["metrics_metadata"] = decision.metrics_metadata
    if decision.scoring_metadata is not None:
        data["scoring_metadata"] = decision.scoring_metadata
    data["generation_warnings"] = list(decision.generation_warnings)

    content = _content_for_decision(decision)
    confidence = 0.75 if decision.status in {DecisionStatus.OK, DecisionStatus.WARNING} else 0.0
    return ModuleResponse(
        module_name=module.name,
        content=content,
        data=data,
        confidence=confidence,
        metadata={
            "description": module.description,
            "module_version": MODULE_VERSION,
            "implementation_phase": IMPLEMENTATION_PHASE,
            "status": decision.status,
            "next_action": decision.next_action,
            "reason": decision.reason,
            "warnings": list(decision.warnings),
            "errors": list(decision.errors),
            "query": query,
            "counts": counts,
            "candidate_generation_implemented": True,
            "conflict_detection_implemented": True,
            "feasibility_validation_implemented": True,
            "metrics_implemented": True,
            "scoring_implemented": True,
            "ranking_implemented": True,
            "decision_engine_implemented": True,
            "interaction_session_implemented": True,
            "persistence_implemented": False,
        },
    )


def _content_for_decision(decision: ScheduleDecisionResult) -> str:
    if decision.status == DecisionStatus.OK:
        return decision.explanation or "Schedule options generated successfully."
    if decision.status == DecisionStatus.WARNING:
        return decision.explanation or "Schedule options generated with warnings."
    if decision.status == DecisionStatus.NEEDS_INPUT:
        return "More information is needed before schedule generation can begin."
    if decision.status == DecisionStatus.PARTIAL:
        return "SchedulePilot produced a partial scheduling result."
    return "SchedulePilot could not generate schedules for the current request."
