from __future__ import annotations

import re
from dataclasses import dataclass

from app.orchestrator.router.module_selector import (
    ACADEMIC_PLANNING,
    ACADEMIC_SUCCESS,
    CAREER,
    COLLEGE_COMPARISON,
    FINANCE,
    SCHEDULING,
)
from app.orchestrator.schemas.intent_result import IntentResult
from app.orchestrator.schemas.student_context import StudentContext


@dataclass(frozen=True)
class IntentRule:
    """Deterministic rule for mapping query text to an intent and modules."""

    intent: str
    target_modules: tuple[str, ...]
    keywords: tuple[str, ...]
    patterns: tuple[str, ...] = ()


class IntentRouter:
    """Rule-based first-pass router for student orchestrator queries."""

    def __init__(self, rules: tuple[IntentRule, ...] | None = None) -> None:
        self.rules = rules or DEFAULT_INTENT_RULES

    def route(self, query: str, context: StudentContext | None = None) -> IntentResult:
        """Classify a query and return target modules without executing module work."""
        normalized_query = self._normalize(query)
        if not normalized_query:
            return self._general_result("Empty query received.")

        matches = self._match_rules(normalized_query)
        matched_modules = self._ordered_modules(matches)
        if len(matched_modules) > 1:
            total_matches = sum(score for _, score in matches)
            return IntentResult(
                intent="multi_module",
                confidence=self._multi_module_confidence(total_matches, len(matched_modules)),
                target_modules=matched_modules,
                reasoning="Query matched multiple module routing rules.",
            )

        if matches:
            best_rule, best_score = max(matches, key=lambda item: item[1])
            return IntentResult(
                intent=best_rule.intent,
                confidence=self._single_module_confidence(best_score),
                target_modules=list(best_rule.target_modules),
                reasoning=f"Query matched {best_score} deterministic routing signal(s).",
            )

        return self._general_result("No deterministic routing rule matched.")

    def _match_rules(self, normalized_query: str) -> list[tuple[IntentRule, int]]:
        matches: list[tuple[IntentRule, int]] = []
        for rule in self.rules:
            score = self._score_rule(rule, normalized_query)
            if score > 0:
                matches.append((rule, score))
        return matches

    @staticmethod
    def _score_rule(rule: IntentRule, normalized_query: str) -> int:
        score = 0
        for keyword in rule.keywords:
            if keyword in normalized_query:
                score += 1
        for pattern in rule.patterns:
            if re.search(pattern, normalized_query):
                score += 1
        return score

    @staticmethod
    def _ordered_modules(matches: list[tuple[IntentRule, int]]) -> list[str]:
        modules: list[str] = []
        for rule, _ in matches:
            for module_name in rule.target_modules:
                if module_name not in modules:
                    modules.append(module_name)
        return modules

    @staticmethod
    def _normalize(query: str) -> str:
        return " ".join(query.lower().strip().split())

    @staticmethod
    def _single_module_confidence(score: int) -> float:
        return min(0.95, 0.65 + (score * 0.08))

    @staticmethod
    def _multi_module_confidence(total_matches: int, module_count: int) -> float:
        return min(0.95, 0.70 + (total_matches * 0.04) + (module_count * 0.04))

    @staticmethod
    def _general_result(reasoning: str) -> IntentResult:
        return IntentResult(
            intent="general_question",
            confidence=0.35,
            target_modules=[],
            reasoning=reasoning,
        )


DEFAULT_INTENT_RULES: tuple[IntentRule, ...] = (
    IntentRule(
        intent="academic_planning",
        target_modules=(ACADEMIC_PLANNING,),
        keywords=(
            "create plan",
            "new education plan",
            "new academic plan",
            "update plan",
            "edit plan",
            "add course",
            "remove course",
            "move course",
            "validate plan",
            "graduation audit",
            "what courses should i take",
            "courses should i take",
            "next semester",
            "academic plan",
            "degree plan",
            "plan my courses",
            "prerequisite",
        ),
        patterns=(
            r"\b(create|update|edit|validate)\b.*\b(plan|degree plan|academic plan)\b",
            r"\b(add|remove|move)\b.*\b(course|class)\b",
            r"\b(course|class|classes)\b.*\b(take|plan|next)\b",
        ),
    ),
    IntentRule(
        intent="course_recommendation",
        target_modules=(ACADEMIC_PLANNING,),
        keywords=(
            "recommend courses",
            "course recommendation",
            "recommend classes",
            "which course",
            "which class",
            "elective",
        ),
    ),
    IntentRule(
        intent="schedule_generation",
        target_modules=(SCHEDULING,),
        keywords=(
            "schedule",
            "timetable",
            "calendar",
            "time conflict",
            "availability",
            "build my spring schedule",
            "build my fall schedule",
        ),
        patterns=(r"\b(build|create|make)\b.*\bschedule\b",),
    ),
    IntentRule(
        intent="graduation_check",
        target_modules=(ACADEMIC_PLANNING,),
        keywords=(
            "graduation check",
            "graduation audit",
            "graduate on time",
            "degree audit",
            "graduation requirement",
            "on track to graduate",
        ),
    ),
    IntentRule(
        intent="career_guidance",
        target_modules=(CAREER,),
        keywords=(
            "career",
            "careers",
            "job",
            "internship",
            "resume",
            "profession",
            "employment",
            "machine learning",
        ),
    ),
    IntentRule(
        intent="finance_assistance",
        target_modules=(FINANCE,),
        keywords=(
            "scholarship",
            "scholarships",
            "financial aid",
            "tuition",
            "fafsa",
            "grant",
            "loan",
            "cost",
        ),
    ),
    IntentRule(
        intent="academic_success",
        target_modules=(ACADEMIC_SUCCESS,),
        keywords=(
            "gpa",
            "grades",
            "grade",
            "falling",
            "struggling",
            "tutoring",
            "study skills",
            "academic probation",
            "failed",
        ),
    ),
    IntentRule(
        intent="college_comparison",
        target_modules=(COLLEGE_COMPARISON,),
        keywords=(
            "compare colleges",
            "compare universities",
            "college comparison",
            "university comparison",
            "versus",
            " vs ",
            "better school",
            "better college",
        ),
        patterns=(r"\bcompare\b.*\b(and|with|to)\b", r"\b\w+\b\s+vs\s+\b\w+\b"),
    ),
)
