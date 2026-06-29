from __future__ import annotations

import uuid
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from app.student.domains.scheduling.engine import (
    CandidateValidationService,
    PreferenceScoringService,
    ScheduleCandidate,
    ScheduleGenerationMetadata,
    ScheduleGenerationResult,
    ScheduleMetricsService,
    ScheduleOption,
    ScheduleRankingService,
)
from app.student.domains.scheduling.schemas.revision import (
    LockedSection,
    LockSectionRequest,
    RestoreOriginalScheduleRequest,
    RevisionOperation,
    RevisionSummary,
    ScheduleRevisionRequest,
    ScheduleRevisionResult,
    UnlockSectionRequest,
)
from app.student.domains.scheduling.schemas.session import (
    GeneratedScheduleSet,
    SessionHistoryAction,
    SessionIdRequest,
    TemporaryPreference,
)
from app.student.domains.scheduling.services.session_service import (
    SchedulingSessionService,
    scheduling_session_service,
)


class ScheduleRevisionService:
    """Deterministic editor for SchedulePilot session options."""

    def __init__(
        self,
        *,
        session_service: SchedulingSessionService | None = None,
        validation_service: CandidateValidationService | None = None,
        metrics_service: ScheduleMetricsService | None = None,
        scoring_service: PreferenceScoringService | None = None,
        ranking_service: ScheduleRankingService | None = None,
    ) -> None:
        self.session_service = session_service or scheduling_session_service
        self.validation_service = validation_service or CandidateValidationService()
        self.metrics_service = metrics_service or ScheduleMetricsService()
        self.scoring_service = scoring_service or PreferenceScoringService()
        self.ranking_service = ranking_service or ScheduleRankingService()

    def revise(self, request: ScheduleRevisionRequest) -> ScheduleRevisionResult:
        session = self.session_service.get_session(request.session_id)
        previous_state = _snapshot(session)
        option = _selected_option(session, request.option_id)

        if request.operation == RevisionOperation.APPLY_TEMPORARY_PREFERENCE:
            _apply_preference(session, request.preference)
            revised_option = option
            revision = _revision(request, option, [], [])
        elif request.operation == RevisionOperation.REMOVE_TEMPORARY_PREFERENCE:
            _remove_preference(session, request.preference)
            revised_option = option
            revision = _revision(request, option, [], [])
        elif request.operation == RevisionOperation.KEEP_SELECTED_FIXED:
            for section in option.selected_sections:
                _lock_section(session, section.section_id, section.course_id, "keep selected fixed")
            revised_option = option
            revision = _revision(
                request,
                option,
                [],
                [],
                locked_section_ids=[section.section_id for section in option.selected_sections],
            )
        else:
            revised_option, revision = self._replace_from_alternatives(session, option, request)

        session.state.generated = _replace_option(session.state.generated, option.option_id, revised_option)
        session.state.selection.selected_option_id = revised_option.option_id
        session.state.revision_count += 1
        session.state.last_revision = revision
        session.state.revision_history.append(revision)
        session.state.redo_stack = []
        session.state.updated_at = _utcnow()
        _append_session_history(
            session,
            "Revised schedule option.",
            previous_state=previous_state,
        )
        return ScheduleRevisionResult(
            success=True,
            session_id=request.session_id,
            revised_option=revised_option,
            revision=revision,
            message="Schedule revision applied.",
        )

    def lock_section(self, request: LockSectionRequest):
        session = self.session_service.get_session(request.session_id)
        previous_state = _snapshot(session)
        _lock_section(session, request.section_id, request.course_id, request.reason)
        session.state.updated_at = _utcnow()
        _append_session_history(session, "Locked schedule section.", previous_state=previous_state)
        return self.session_service.load_session(SessionIdRequest(session_id=request.session_id))

    def unlock_section(self, request: UnlockSectionRequest):
        session = self.session_service.get_session(request.session_id)
        previous_state = _snapshot(session)
        session.state.locked_sections = [
            locked
            for locked in session.state.locked_sections
            if locked.section_id != request.section_id
        ]
        session.state.updated_at = _utcnow()
        _append_session_history(session, "Unlocked schedule section.", previous_state=previous_state)
        return self.session_service.load_session(SessionIdRequest(session_id=request.session_id))

    def undo_last_revision(self, request: SessionIdRequest):
        session = self.session_service.get_session(request.session_id)
        revision_entries = [
            entry
            for entry in session.state.history
            if entry.description == "Revised schedule option." and entry.previous_state
        ]
        if not revision_entries:
            raise ValueError("No schedule revision can be undone.")
        current_state = _snapshot(session)
        previous_state = revision_entries[-1].previous_state
        restored = session.state.__class__.model_validate(previous_state)
        restored.history = list(session.state.history)
        restored.redo_stack = list(session.state.redo_stack) + [current_state]
        restored.updated_at = _utcnow()
        session.state = restored
        _append_session_history(session, "Undid schedule revision.")
        return self.session_service.load_session(SessionIdRequest(session_id=request.session_id))

    def redo_last_revision(self, request: SessionIdRequest):
        session = self.session_service.get_session(request.session_id)
        if not session.state.redo_stack:
            raise ValueError("No schedule revision can be redone.")
        snapshot = session.state.redo_stack[-1]
        history = list(session.state.history)
        restored = session.state.__class__.model_validate(snapshot)
        restored.history = history
        restored.redo_stack = session.state.redo_stack[:-1]
        restored.updated_at = _utcnow()
        session.state = restored
        _append_session_history(session, "Redid schedule revision.")
        return self.session_service.load_session(SessionIdRequest(session_id=request.session_id))

    def restore_original(self, request: RestoreOriginalScheduleRequest):
        session = self.session_service.get_session(request.session_id)
        if session.state.original_generated is None:
            raise ValueError("Original generated schedule set is not available.")
        previous_state = _snapshot(session)
        session.state.generated = session.state.original_generated.model_copy(deep=True)
        session.state.selection.selected_option_id = None
        session.state.revision_count = 0
        session.state.last_revision = None
        session.state.revision_history = []
        session.state.redo_stack = []
        session.state.updated_at = _utcnow()
        _append_session_history(
            session,
            "Restored original generated schedule set.",
            previous_state=previous_state,
        )
        return self.session_service.load_session(SessionIdRequest(session_id=request.session_id))

    def _replace_from_alternatives(
        self,
        session,
        option: ScheduleOption,
        request: ScheduleRevisionRequest,
    ) -> tuple[ScheduleOption, RevisionSummary]:
        target = _target_section(option, request)
        if target.section_id in _locked_section_ids(session):
            raise ValueError("Locked sections cannot be revised.")
        replacement = _replacement_section(session, target, request)
        if replacement.section_id in _locked_section_ids(session):
            raise ValueError("Locked sections cannot be used as replacements.")
        meetings_by_section = _meetings_by_section(session)
        revised_sections = [
            replacement if section.section_id == target.section_id else section
            for section in option.selected_sections
        ]
        revised_meetings = []
        for section in revised_sections:
            revised_meetings.extend(meetings_by_section.get(section.section_id, []))
        candidate = ScheduleCandidate(
            candidate_id=f"revision-{uuid.uuid4()}",
            courses=[],
            sections=revised_sections,
            meetings=revised_meetings,
            metadata={
                "source_option_id": option.option_id,
                "revision_operation": request.operation,
                "partial_regeneration": True,
                "affected_course_ids": [target.course_id],
                "locked_section_ids": list(_locked_section_ids(session)),
            },
        )
        result = ScheduleGenerationResult(
            candidates=[candidate],
            metadata=ScheduleGenerationMetadata(
                generated_count=1,
                truncated=False,
                generation_time_ms=0,
                max_candidate_count=1,
                course_count=1,
                section_count=len(revised_sections),
            ),
        )
        validated, _ = self.validation_service.validate_generation_result(result)
        enriched, _ = self.metrics_service.compute_for_candidates(validated)
        scored, _ = self.scoring_service.score_candidates(
            enriched,
            [preference.model_dump(mode="json") for preference in session.state.preferences.temporary],
        )
        ranked = self.ranking_service.rank_candidates(scored)
        revised_option = ranked.top_option or _option_from_candidate(scored[0], option)
        revised_option = revised_option.model_copy(
            update={
                "option_id": option.option_id,
                "rank": option.rank,
                "metadata": {
                    **revised_option.metadata,
                    "revision_operation": request.operation,
                    "partial_regeneration": True,
                },
            },
            deep=True,
        )
        revision = _revision(
            request,
            option,
            [target.section_id],
            [replacement.section_id],
            affected_course_ids=[target.course_id],
            locked_section_ids=list(_locked_section_ids(session)),
            warnings=[warning.message for warning in revised_option.warnings],
        )
        return revised_option, revision


def _selected_option(session, option_id: str | None) -> ScheduleOption:
    selected_id = option_id or session.state.selection.selected_option_id
    if selected_id is None and session.state.generated.options:
        selected_id = session.state.generated.options[0].option_id
    for option in session.state.generated.options:
        if option.option_id == selected_id:
            return option
    raise ValueError("Schedule option is not available in the current session.")


def _target_section(option: ScheduleOption, request: ScheduleRevisionRequest):
    for section in option.selected_sections:
        if request.section_id and section.section_id == request.section_id:
            return section
        if request.course_id and section.course_id == request.course_id:
            return section
    raise ValueError("Target section is not available in the selected option.")


def _replacement_section(session, target, request: ScheduleRevisionRequest):
    alternatives = [
        section
        for option in session.state.generated.options
        for section in option.selected_sections
        if section.course_id == target.course_id and section.section_id != target.section_id
    ]
    if request.replacement_section_id:
        alternatives = [
            section
            for section in alternatives
            if section.section_id == request.replacement_section_id
        ]
    if request.operation == RevisionOperation.REPLACE_INSTRUCTOR:
        alternatives = [
            section for section in alternatives if section.instructor == request.instructor
        ]
    if request.operation == RevisionOperation.REPLACE_DELIVERY:
        alternatives = [
            section
            for section in alternatives
            if section.instruction_method == request.instruction_method
        ]
    if request.operation == RevisionOperation.REPLACE_MEETING_TIME:
        meeting_section_ids = {
            meeting.section_id
            for meeting in _all_meetings(session)
            if (request.weekday is None or meeting.weekday == request.weekday)
            and (request.start_time is None or meeting.start_time == request.start_time)
            and (request.end_time is None or meeting.end_time == request.end_time)
        }
        alternatives = [
            section for section in alternatives if section.section_id in meeting_section_ids
        ]
    if not alternatives:
        raise ValueError("No deterministic replacement section is available.")
    return sorted(alternatives, key=lambda section: (section.section_number, section.section_id))[0]


def _meetings_by_section(session):
    meetings: dict[str, list] = {}
    for meeting in _all_meetings(session):
        meetings.setdefault(meeting.section_id, []).append(meeting)
    return meetings


def _all_meetings(session):
    return [
        meeting
        for option in session.state.generated.options
        for meeting in option.selected_meetings
    ]


def _replace_option(generated: GeneratedScheduleSet, option_id: str, option: ScheduleOption):
    options = [
        option if existing.option_id == option_id else existing
        for existing in generated.options
    ]
    return generated.model_copy(
        update={
            "options": options,
            "ranking_order": [item.option_id for item in options],
        },
        deep=True,
    )


def _option_from_candidate(candidate: ScheduleCandidate, source_option: ScheduleOption) -> ScheduleOption:
    return source_option.model_copy(
        update={
            "selected_sections": list(candidate.sections),
            "selected_meetings": list(candidate.meetings),
            "metrics": candidate.metrics,
            "warnings": list(candidate.warnings),
            "conflicts": list(candidate.conflicts),
            "score": candidate.score,
            "normalized_score": candidate.normalized_score,
            "tradeoffs": ["Revised schedule requires review"],
            "explanation": "This revised schedule requires review because it is not currently feasible.",
        },
        deep=True,
    )


def _revision(
    request: ScheduleRevisionRequest,
    option: ScheduleOption,
    replaced_section_ids: list[str],
    added_section_ids: list[str],
    *,
    affected_course_ids: list[str] | None = None,
    locked_section_ids: list[str] | None = None,
    warnings: list[str] | None = None,
) -> RevisionSummary:
    return RevisionSummary(
        revision_id=str(uuid.uuid4()),
        operation=request.operation,
        option_id=option.option_id,
        affected_course_ids=affected_course_ids or [],
        replaced_section_ids=replaced_section_ids,
        added_section_ids=added_section_ids,
        locked_section_ids=locked_section_ids or [],
        warnings=warnings or [],
        created_at=_utcnow(),
    )


def _lock_section(session, section_id: str, course_id: str | None, reason: str | None) -> None:
    if section_id in _locked_section_ids(session):
        return
    session.state.locked_sections.append(
        LockedSection(
            section_id=section_id,
            course_id=course_id,
            reason=reason,
            locked_at=_utcnow(),
        )
    )


def _locked_section_ids(session) -> set[str]:
    return {section.section_id for section in session.state.locked_sections}


def _apply_preference(session, preference: dict[str, Any] | None) -> None:
    if not preference:
        raise ValueError("A temporary preference is required.")
    key = str(preference.get("key") or preference.get("preference_key"))
    if not key:
        raise ValueError("Temporary preference requires a key.")
    session.state.preferences.temporary = [
        existing for existing in session.state.preferences.temporary if existing.key != key
    ] + [TemporaryPreference(key=key, value=preference.get("value"))]


def _remove_preference(session, preference: dict[str, Any] | None) -> None:
    if not preference:
        raise ValueError("A temporary preference is required.")
    key = str(preference.get("key") or preference.get("preference_key"))
    session.state.preferences.temporary = [
        existing for existing in session.state.preferences.temporary if existing.key != key
    ]


def _snapshot(session) -> dict:
    return deepcopy(session.state.model_dump(mode="json"))


def _append_session_history(session, description: str, *, previous_state: dict | None = None) -> None:
    from app.student.domains.scheduling.services.session_service import _append_history

    _append_history(
        session,
        SessionHistoryAction.REGENERATED,
        description,
        previous_state=previous_state,
    )


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


schedule_revision_service = ScheduleRevisionService()
