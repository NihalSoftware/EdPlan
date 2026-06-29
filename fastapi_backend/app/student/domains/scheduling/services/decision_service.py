from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.student.domains.planning.repositories.normalized_plan_repository import (
    NormalizedPlanRepository,
    normalized_plan_repository,
)
from app.student.domains.scheduling.engine import (
    CandidateGenerator,
    CandidateValidationService,
    PreferenceScoringService,
    ScheduleMetricsService,
    ScheduleRankingService,
)
from app.student.domains.scheduling.schemas.decision import (
    DecisionContext,
    DecisionNextAction,
    DecisionReason,
    DecisionStatus,
    PlanDecisionOption,
    ScheduleDecisionRequest,
    ScheduleDecisionResult,
    TermDecisionOption,
)
from app.student.domains.scheduling.schemas.schedulepilot import ScheduleRetrievalContext
from app.student.domains.scheduling.services.retrieval_service import (
    SchedulePilotPlanNotFoundError,
    SchedulePilotRetrievalService,
    schedulepilot_retrieval_service,
)


class ScheduleDecisionService:
    """Deterministic workflow coordinator for SchedulePilot agent decisions."""

    def __init__(
        self,
        *,
        plan_repository: NormalizedPlanRepository | None = None,
        retrieval_service: SchedulePilotRetrievalService | None = None,
        candidate_generator: CandidateGenerator | None = None,
        validation_service: CandidateValidationService | None = None,
        metrics_service: ScheduleMetricsService | None = None,
        scoring_service: PreferenceScoringService | None = None,
        ranking_service: ScheduleRankingService | None = None,
    ) -> None:
        self.plan_repository = plan_repository or normalized_plan_repository
        self.retrieval_service = retrieval_service or schedulepilot_retrieval_service
        self.candidate_generator = candidate_generator or CandidateGenerator()
        self.validation_service = validation_service or CandidateValidationService()
        self.metrics_service = metrics_service or ScheduleMetricsService()
        self.scoring_service = scoring_service or PreferenceScoringService()
        self.ranking_service = ranking_service or ScheduleRankingService()

    async def decide_and_generate(
        self,
        db: AsyncSession,
        request: ScheduleDecisionRequest,
    ) -> ScheduleDecisionResult:
        normalized_preferences = _merge_preferences(
            request.system_defaults,
            request.saved_preferences,
            request.preferences,
        )
        base_context = DecisionContext(
            user_id=request.user_id,
            normalized_preferences=normalized_preferences,
        )
        plan_id, available_plans, plan_failure = await self._resolve_plan(db, request)
        base_context.available_plans = available_plans
        base_context.resolved_plan_id = plan_id
        if plan_failure is not None:
            plan_failure.context.normalized_preferences = normalized_preferences
            return plan_failure

        try:
            retrieval_context = await self.retrieval_service.build_context(
                db,
                user_id=request.user_id,
                plan_id=plan_id,
            )
        except SchedulePilotPlanNotFoundError:
            return _decision(
                status=DecisionStatus.FAILED,
                next_action=DecisionNextAction.STOP,
                reason=DecisionReason.PLAN_NOT_FOUND,
                context=base_context,
                errors=["Plan not found for the requested user."],
            )

        base_context.available_terms = [
            TermDecisionOption(
                term_id=term.term_id,
                term_name=term.term_name,
                is_active=term.is_active,
            )
            for term in retrieval_context.terms
        ]
        if not retrieval_context.plan.is_active:
            return _decision(
                status=DecisionStatus.FAILED,
                next_action=DecisionNextAction.STOP,
                reason=DecisionReason.INACTIVE_PLAN,
                context=base_context,
                retrieval_context=retrieval_context,
                errors=["The selected plan is inactive."],
            )
        if not retrieval_context.courses:
            return _decision(
                status=DecisionStatus.FAILED,
                next_action=DecisionNextAction.STOP,
                reason=DecisionReason.EMPTY_PLAN,
                context=base_context,
                retrieval_context=retrieval_context,
                errors=["The selected plan has no planned courses."],
            )

        term_id, term_failure = self._resolve_term(request, retrieval_context)
        base_context.resolved_term_id = term_id
        if term_failure is not None:
            term_failure.context.resolved_plan_id = plan_id
            term_failure.context.available_plans = available_plans
            term_failure.context.available_terms = base_context.available_terms
            term_failure.context.normalized_preferences = normalized_preferences
            return term_failure.model_copy(update={"retrieval_context": retrieval_context})

        data_failure = self._validate_scheduling_data(retrieval_context, base_context)
        if data_failure is not None:
            return data_failure

        warnings = _scheduling_warnings(retrieval_context)
        generation_result = self.candidate_generator.generate(retrieval_context)
        validated_candidates, validation_metadata = (
            self.validation_service.validate_generation_result(generation_result)
        )
        enriched_candidates, metrics_metadata = self.metrics_service.compute_for_candidates(
            validated_candidates
        )
        scored_candidates, scoring_metadata = self.scoring_service.score_candidates(
            enriched_candidates,
            normalized_preferences,
        )
        ranking_result = self.ranking_service.rank_candidates(scored_candidates)
        status = DecisionStatus.WARNING if warnings else DecisionStatus.OK
        reason = (
            DecisionReason.PARTIAL_SCHEDULING_DATA
            if warnings
            else DecisionReason.GENERATION_COMPLETE
        )
        return _decision(
            status=status,
            next_action=(
                DecisionNextAction.REVIEW_WARNINGS
                if warnings
                else DecisionNextAction.SHOW_RESULTS
            ),
            reason=reason,
            context=base_context,
            retrieval_context=retrieval_context,
            warnings=warnings,
            metadata={
                "preference_count": len(normalized_preferences),
                "query": request.query,
            },
            generation_metadata=generation_result.metadata.model_dump(mode="json"),
            generation_warnings=list(generation_result.warnings),
            validation_metadata=validation_metadata,
            metrics_metadata=metrics_metadata,
            scoring_metadata=scoring_metadata,
            ranking_result=ranking_result,
            scored_candidates=[
                candidate.model_dump(mode="json") for candidate in scored_candidates
            ],
            explanation=_explanation(retrieval_context, term_id),
        )

    async def _resolve_plan(
        self,
        db: AsyncSession,
        request: ScheduleDecisionRequest,
    ) -> tuple[str | None, list[PlanDecisionOption], ScheduleDecisionResult | None]:
        if request.plan_id:
            return request.plan_id, [], None
        plans = await self.plan_repository.list_plans(
            db,
            user_id=request.user_id,
            is_active=True,
        )
        available_plans = [_plan_option(plan) for plan in plans]
        context = DecisionContext(
            user_id=request.user_id,
            available_plans=available_plans,
        )
        if not available_plans:
            return None, available_plans, _decision(
                status=DecisionStatus.NEEDS_INPUT,
                next_action=DecisionNextAction.ASK_FOR_PLAN,
                reason=DecisionReason.NO_PLANS,
                context=context,
                errors=["No active academic plan is available."],
            )
        if len(available_plans) > 1:
            return None, available_plans, _decision(
                status=DecisionStatus.NEEDS_INPUT,
                next_action=DecisionNextAction.ASK_FOR_PLAN,
                reason=DecisionReason.MULTIPLE_PLANS,
                context=context,
                warnings=["Multiple active plans are available."],
            )
        return available_plans[0].plan_id, available_plans, None

    def _resolve_term(
        self,
        request: ScheduleDecisionRequest,
        retrieval_context: ScheduleRetrievalContext,
    ) -> tuple[str | None, ScheduleDecisionResult | None]:
        context = DecisionContext(
            user_id=request.user_id,
            resolved_plan_id=retrieval_context.plan.plan_id,
            available_terms=[
                TermDecisionOption(
                    term_id=term.term_id,
                    term_name=term.term_name,
                    is_active=term.is_active,
                )
                for term in retrieval_context.terms
            ],
        )
        term_ids = {term.term_id for term in retrieval_context.terms}
        if request.term_id:
            if request.term_id not in term_ids:
                return None, _decision(
                    status=DecisionStatus.NEEDS_INPUT,
                    next_action=DecisionNextAction.ASK_FOR_TERM,
                    reason=DecisionReason.UNKNOWN_TERM,
                    context=context,
                    retrieval_context=retrieval_context,
                    errors=["Requested academic term is not available."],
                )
            return request.term_id, None

        planned_term_ids = {
            course.planned_term_id
            for course in retrieval_context.courses
            if course.planned_term_id
        }
        if len(planned_term_ids) == 1:
            return next(iter(planned_term_ids)), None
        if len(planned_term_ids) > 1:
            return None, _decision(
                status=DecisionStatus.NEEDS_INPUT,
                next_action=DecisionNextAction.ASK_FOR_TERM,
                reason=DecisionReason.MULTIPLE_POSSIBLE_TERMS,
                context=context,
                retrieval_context=retrieval_context,
                warnings=["Planned courses span multiple academic terms."],
            )

        active_term_ids = {term.term_id for term in retrieval_context.terms if term.is_active}
        if len(active_term_ids) == 1:
            return next(iter(active_term_ids)), None
        return None, _decision(
            status=DecisionStatus.NEEDS_INPUT,
            next_action=DecisionNextAction.ASK_FOR_TERM,
            reason=(
                DecisionReason.MULTIPLE_POSSIBLE_TERMS
                if len(active_term_ids) > 1
                else DecisionReason.UNKNOWN_TERM
            ),
            context=context,
            retrieval_context=retrieval_context,
            warnings=["Scheduling term could not be resolved deterministically."],
        )

    def _validate_scheduling_data(
        self,
        retrieval_context: ScheduleRetrievalContext,
        context: DecisionContext,
    ) -> ScheduleDecisionResult | None:
        if not retrieval_context.offerings:
            return _decision(
                status=DecisionStatus.FAILED,
                next_action=DecisionNextAction.STOP,
                reason=DecisionReason.NO_OFFERINGS,
                context=context,
                retrieval_context=retrieval_context,
                errors=["No course offerings exist for planned courses."],
            )
        if not retrieval_context.sections:
            return _decision(
                status=DecisionStatus.FAILED,
                next_action=DecisionNextAction.STOP,
                reason=DecisionReason.NO_SECTIONS,
                context=context,
                retrieval_context=retrieval_context,
                errors=["No open sections exist for available offerings."],
            )
        return None


def _decision(
    *,
    status: DecisionStatus,
    next_action: DecisionNextAction,
    reason: DecisionReason,
    context: DecisionContext,
    warnings: list[str] | None = None,
    errors: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
    retrieval_context: ScheduleRetrievalContext | None = None,
    generation_metadata: dict[str, Any] | None = None,
    generation_warnings: list[str] | None = None,
    validation_metadata: dict[str, Any] | None = None,
    metrics_metadata: dict[str, Any] | None = None,
    scoring_metadata: dict[str, Any] | None = None,
    ranking_result=None,
    scored_candidates: list[dict[str, Any]] | None = None,
    explanation: str | None = None,
) -> ScheduleDecisionResult:
    return ScheduleDecisionResult(
        status=status,
        next_action=next_action,
        reason=reason,
        warnings=warnings or [],
        errors=errors or [],
        metadata=metadata or {},
        context=context,
        retrieval_context=retrieval_context,
        generation_metadata=generation_metadata,
        generation_warnings=generation_warnings or [],
        validation_metadata=validation_metadata,
        metrics_metadata=metrics_metadata,
        scoring_metadata=scoring_metadata,
        ranking_result=ranking_result,
        scored_candidates=scored_candidates or [],
        explanation=explanation,
    )


def _plan_option(plan: dict[str, Any]) -> PlanDecisionOption:
    return PlanDecisionOption(
        plan_id=plan["plan_id"],
        plan_name=plan["plan_name"],
        is_active=plan["is_active"],
        university_id=plan.get("university_id"),
        program_id=plan.get("program_id"),
    )


def _merge_preferences(
    system_defaults: Iterable[dict[str, Any]],
    saved_preferences: Iterable[dict[str, Any]],
    request_preferences: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for preference in system_defaults:
        _merge_preference(merged, preference)
    for preference in saved_preferences:
        _merge_preference(merged, preference)
    for preference in request_preferences:
        _merge_preference(merged, preference)
    return list(merged.values())


def _merge_preference(target: dict[str, dict[str, Any]], preference: dict[str, Any]) -> None:
    key = preference.get("key") or preference.get("preference_key") or preference.get("name")
    if not key:
        key = str(len(target))
    payload = dict(preference)
    payload["key"] = key
    target[str(key)] = payload


def _scheduling_warnings(retrieval_context: ScheduleRetrievalContext) -> list[str]:
    warnings: list[str] = []
    retrieval_warnings = retrieval_context.warnings
    if retrieval_warnings.courses_without_offerings:
        warnings.append("Some planned courses do not have course offerings.")
    if retrieval_warnings.offerings_without_sections:
        warnings.append("Some course offerings do not have open sections.")
    if retrieval_warnings.sections_without_meetings:
        warnings.append("Some sections are missing meeting information.")
    return warnings


def _explanation(retrieval_context: ScheduleRetrievalContext, term_id: str | None) -> str:
    term_name = next(
        (term.term_name for term in retrieval_context.terms if term.term_id == term_id),
        "the resolved term",
    )
    return (
        f"Generated schedules for {term_name} using your "
        f"{retrieval_context.plan.plan_name} plan."
    )


schedule_decision_service = ScheduleDecisionService()
