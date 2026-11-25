from __future__ import annotations

import json
import uuid
from collections import Counter
from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.orchestrator.llm import (
    BaseLLMProvider,
    LLMProviderError,
    LLMMessage,
    LLMRequest,
    LLMResponse,
    OpenRouterProvider,
)
from app.orchestrator.modules.base_module import BaseModule
from app.orchestrator.schemas.module_response import ModuleResponse
from app.orchestrator.schemas.student_context import StudentContext
from app.student.domains.discovery.models import (
    Course,
    CourseCorequisite,
    CoursePrerequisite,
    Program,
)
from app.student.domains.planning.models import EdPlan, PlanCourse
from app.student.domains.planning.tools.registry import PLANNING_TOOLS

MODULE_NAME = "academic_planning"

MODULE_DESCRIPTION = "Manage student education plans and graduation pathways."

ACADEMIC_PLANNING_ADVISOR_PROMPT = (
    "You are EdPlan's Academic Planning Advisor. Act as a university academic advisor. "
    "Prioritize graduation feasibility, prerequisite compliance, corequisite compliance, "
    "and realistic academic load. Use only the exposed academic planning tools when "
    "information is required. Never invent completed courses, degree requirements, "
    "prerequisites, corequisites, validation results, or audit findings. If information "
    "is missing, retrieve it through tools or ask the student for the missing information. "
    "Prefer validated plans over assumptions. For complex advising workflows, attempt to "
    "compare Aggressive Plan, Balanced Plan, and Low-Risk Plan alternatives when sufficient "
    "information exists. Each plan should include semesters, courses, credit loads, "
    "prerequisite compliance, graduation impact, tradeoffs, and a ranked recommendation. "
    "For graduation acceleration requests: determine remaining requirements, prerequisite "
    "constraints, and corequisite constraints; generate multiple feasible plans when possible; "
    "validate plans before recommending; rank alternatives; explain tradeoffs; and state the "
    "expected graduation timeline. For planning/advising questions, prefer this format when "
    "enough information exists: Summary; Aggressive Plan with semesters and graduation "
    "estimate; Balanced Plan with semesters and graduation estimate; Low-Risk Plan with "
    "semesters and graduation estimate; Recommended Option; Reasoning. Do not force this "
    "format for simple CRUD requests."
)

SUPPORTED_TOOL_NAMES = {
    "create_plan",
    "update_plan",
    "delete_plan",
    "get_plan",
    "add_course",
    "remove_course",
    "move_course",
    "validate_plan",
    "audit_plan",
    "get_remaining_courses",
    "get_course_details",
    "get_prerequisites",
    "get_corequisites",
    "get_program_requirements",
    "get_available_terms",
}


def get_tools():
    return PLANNING_TOOLS


class AcademicPlanningModule(BaseModule):
    """Orchestrator module adapter for the existing academic planning tools."""

    name = MODULE_NAME
    description = MODULE_DESCRIPTION

    def __init__(
        self,
        db: AsyncSession | None = None,
        tools: list[Any] | None = None,
        llm_provider: BaseLLMProvider | None = None,
        max_tool_iterations: int = 6,
        max_total_tool_calls: int = 10,
        max_same_tool_calls: int = 2,
    ) -> None:
        self.db = db
        self.tools = {tool.name: tool for tool in tools or get_tools()}
        self.llm_provider = llm_provider or OpenRouterProvider()
        self.max_tool_iterations = max_tool_iterations
        self.max_total_tool_calls = max_total_tool_calls
        self.max_same_tool_calls = max_same_tool_calls

    async def execute(self, context: StudentContext, query: str) -> ModuleResponse:
        planning_context = await self._load_academic_planning_context(context)
        if planning_context["status"] == "needs_context":
            return self._clarification_response(planning_context)

        structured_plan = self._build_structured_academic_plan(planning_context, query)
        content, llm_status = await self._advisor_response(
            context,
            query,
            planning_context,
            structured_plan,
        )
        return ModuleResponse(
            module_name=self.name,
            content=content,
            data={
                "academic_plan": jsonable_encoder(structured_plan),
                "planning_summary": structured_plan["summary"],
                "student_context": jsonable_encoder(planning_context["student_context"]),
                "catalog": {
                    "program": planning_context["program"],
                    "university": planning_context["university"],
                    "required_course_count": len(planning_context["required_courses"]),
                },
            },
            confidence=0.9 if llm_status == "ok" else 0.72,
            metadata={
                "description": self.description,
                "advisor_prompt": "academic_planning.advisor",
                "llm_status": llm_status,
                "deterministic_validation": True,
                "status": "completed_with_warnings"
                if structured_plan["validation"]["warnings"]
                else "completed",
            },
        )

    async def _load_academic_planning_context(
        self,
        context: StudentContext,
    ) -> dict[str, Any]:
        missing: list[str] = []
        if self.db is None or not hasattr(self.db, "execute"):
            missing.append("database_session")

        plan_id = _parse_uuid((context.plan or {}).get("plan_id"))
        user_id = (context.user or {}).get("id")
        if plan_id is None:
            missing.append("active_education_plan")
        if not user_id:
            missing.append("student_profile")
        if missing:
            return {"status": "needs_context", "missing": missing}

        plan_model = await self._load_plan_model(plan_id, int(user_id))
        if plan_model is None:
            return {
                "status": "needs_context",
                "missing": ["active_education_plan"],
                "student_context": self._student_context_payload(context),
            }
        if plan_model.program is None:
            return {
                "status": "needs_context",
                "missing": ["program"],
                "student_context": self._student_context_payload(context),
            }
        if plan_model.university is None:
            return {
                "status": "needs_context",
                "missing": ["university"],
                "student_context": self._student_context_payload(context),
            }

        required_courses = [_course_payload(course) for course in plan_model.program.courses or []]
        completed_ids = {
            str(plan_course.course_id)
            for plan_course in plan_model.courses or []
            if (plan_course.status or "").lower() == "completed"
        }
        completed_codes = {
            str(course.get("code") or course.get("course_code")).upper()
            for course in context.completed_courses or []
            if course.get("code") or course.get("course_code")
        }
        for course in required_courses:
            if course["course_code"].upper() in completed_codes:
                completed_ids.add(course["course_id"])

        completed_courses = [
            course for course in required_courses if course["course_id"] in completed_ids
        ]
        remaining_courses = [
            course for course in required_courses if course["course_id"] not in completed_ids
        ]

        return {
            "status": "ready",
            "student_context": self._student_context_payload(context),
            "plan": {
                "plan_id": str(plan_model.plan_id),
                "plan_name": plan_model.plan_name,
                "description": plan_model.description,
                "is_active": plan_model.is_active,
            },
            "program": _program_payload(plan_model.program),
            "university": _university_payload(plan_model.university),
            "required_courses": required_courses,
            "completed_courses": completed_courses,
            "remaining_courses": remaining_courses,
            "completed_course_ids": completed_ids,
        }

    async def _load_plan_model(self, plan_id: uuid.UUID, user_id: int) -> EdPlan | None:
        result = await self.db.execute(
            select(EdPlan)
            .options(
                selectinload(EdPlan.university),
                selectinload(EdPlan.program)
                .selectinload(Program.courses)
                .selectinload(Course.prerequisite_links)
                .selectinload(CoursePrerequisite.prerequisite_course),
                selectinload(EdPlan.program)
                .selectinload(Program.courses)
                .selectinload(Course.corequisite_links)
                .selectinload(CourseCorequisite.corequisite_course),
                selectinload(EdPlan.courses).selectinload(PlanCourse.course),
            )
            .where(EdPlan.plan_id == plan_id, EdPlan.user_id == user_id)
        )
        return result.scalar_one_or_none()

    def _build_structured_academic_plan(
        self,
        planning_context: dict[str, Any],
        query: str,
    ) -> dict[str, Any]:
        completed_ids = set(planning_context["completed_course_ids"])
        remaining_courses = sorted(
            planning_context["remaining_courses"],
            key=_course_sort_key,
        )
        plan_courses, blocked_courses, planning_warnings = _schedule_remaining_courses(
            remaining_courses,
            completed_ids,
            query,
        )
        validation = _validate_structured_plan(
            completed_ids,
            plan_courses,
            blocked_courses,
            planning_warnings,
        )

        completed_credits = _sum_credits(planning_context["completed_courses"])
        planned_credits = sum(semester["credits"] for semester in plan_courses)
        total_required_credits = planning_context["program"].get("total_credit_hours") or (
            completed_credits + planned_credits
        )
        remaining_credits = max(int(total_required_credits) - completed_credits, 0)
        graduation_estimate = (
            f"{len(plan_courses)} remaining semester"
            f"{'' if len(plan_courses) == 1 else 's'}"
        )

        summary = {
            "program": planning_context["program"],
            "university": planning_context["university"],
            "total_credits": total_required_credits,
            "completed_credits": completed_credits,
            "remaining_credits": remaining_credits,
            "planned_credits": planned_credits,
            "completed_courses": len(planning_context["completed_courses"]),
            "remaining_courses": len(remaining_courses),
            "graduation_estimate": graduation_estimate,
        }
        prerequisite_notes = _prerequisite_notes(plan_courses, blocked_courses)
        recommendations = _academic_recommendations(validation, query)
        return {
            "summary": summary,
            "semesters": plan_courses,
            "total_credits": total_required_credits,
            "completed_credits": completed_credits,
            "remaining_credits": remaining_credits,
            "graduation_estimate": graduation_estimate,
            "important_prerequisite_notes": prerequisite_notes,
            "recommendations": recommendations,
            "validation": validation,
            "blocked_courses": blocked_courses,
        }

    async def _advisor_response(
        self,
        context: StudentContext,
        query: str,
        planning_context: dict[str, Any],
        structured_plan: dict[str, Any],
    ) -> tuple[str, str]:
        payload = {
            "student": {
                "user": planning_context["student_context"].get("user"),
                "preferences": planning_context["student_context"].get("preferences"),
                "career_goal": planning_context["student_context"].get("career_goal"),
            },
            "active_plan": planning_context["plan"],
            "university": planning_context["university"],
            "program": planning_context["program"],
            "degree_requirements": {
                "required_course_count": len(planning_context["required_courses"]),
                "completed_course_codes": [
                    course["course_code"] for course in planning_context["completed_courses"]
                ],
                "remaining_course_codes": [
                    course["course_code"] for course in planning_context["remaining_courses"]
                ],
            },
            "draft_academic_plan": structured_plan,
            "student_query": query,
        }
        messages = [
            LLMMessage(
                role="user",
                content=(
                    "Create an academic-advisor response using the structured context below. "
                    "Do not invent courses, credits, prerequisites, or graduation dates. "
                    "Reference the semester plan and validation warnings exactly. Keep the "
                    "answer specific, concise, and action-oriented.\n\n"
                    f"{json.dumps(jsonable_encoder(payload))}"
                ),
            )
        ]
        try:
            response = await self.llm_provider.generate(
                LLMRequest(
                    messages=messages,
                    system_prompt=ACADEMIC_PLANNING_ADVISOR_PROMPT,
                    tools=[],
                    temperature=0.2,
                    max_tokens=1800,
                    metadata={"module": self.name, "mode": "structured_academic_plan"},
                )
            )
        except LLMProviderError:
            return self._fallback_advisor_response(structured_plan), "unavailable"
        except Exception:
            return self._fallback_advisor_response(structured_plan), "failed"

        if not response.content:
            return self._fallback_advisor_response(structured_plan), "empty"
        return response.content, "ok"

    def _clarification_response(self, planning_context: dict[str, Any]) -> ModuleResponse:
        missing = planning_context.get("missing") or ["academic_context"]
        readable = ", ".join(str(item).replace("_", " ") for item in missing)
        return ModuleResponse(
            module_name=self.name,
            content=(
                "I can create a personalized academic plan once your academic context is "
                f"complete. I still need: {readable}. Please select or create an active "
                "education plan with a university and program first."
            ),
            data={"missing_context": missing},
            confidence=0.35,
            metadata={
                "description": self.description,
                "status": "needs_context",
                "deterministic_validation": True,
            },
        )

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
        }

    @staticmethod
    def _fallback_advisor_response(structured_plan: dict[str, Any]) -> str:
        summary = structured_plan["summary"]
        lines = [
            (
                "Here is a personalized academic plan based on your current program "
                f"requirements for {summary['program'].get('degree')} in "
                f"{summary['program'].get('program_name')}."
            ),
            "",
            (
                f"You have completed {summary['completed_credits']} credits and have "
                f"about {summary['remaining_credits']} credits remaining. The draft plan "
                f"covers {summary['planned_credits']} credits across "
                f"{summary['graduation_estimate']}."
            ),
            "",
            "Semester plan:",
        ]
        for semester in structured_plan["semesters"]:
            course_list = ", ".join(course["course_code"] for course in semester["courses"])
            lines.append(f"- {semester['label']} ({semester['credits']} credits): {course_list}")
        if structured_plan["validation"]["warnings"]:
            lines.append("")
            lines.append("Warnings to review with an advisor:")
            for warning in structured_plan["validation"]["warnings"][:5]:
                lines.append(f"- {warning['message']}")
        if structured_plan["recommendations"]:
            lines.append("")
            lines.append("Recommendations:")
            for recommendation in structured_plan["recommendations"][:4]:
                lines.append(f"- {recommendation}")
        return "\n".join(lines)

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

    def _initial_messages(self, context: StudentContext, query: str) -> list[LLMMessage]:
        planning_summary = self._planning_summary(context)
        context_payload = {
            "planning_summary": planning_summary,
            "user": context.user,
            "plan": context.plan,
            "program": context.program,
            "university": context.university,
            "completed_courses": context.completed_courses,
            "preferences": context.preferences,
            "memory": context.memory,
            "career_goal": context.career_goal,
            "available_tools": self.available_tool_names,
        }
        return [
            LLMMessage(
                role="user",
                content=(
                    f"Student query:\n{query}\n\n"
                    "Use this compact planning summary first to avoid unnecessary tool calls:\n"
                    f"{json.dumps(jsonable_encoder(planning_summary))}\n\n"
                    f"Known student context:\n{json.dumps(jsonable_encoder(context_payload))}"
                ),
            )
        ]

    def _planning_summary(self, context: StudentContext) -> dict[str, Any]:
        completed_courses = context.completed_courses or []
        plan = context.plan or {}
        payload = plan.get("payload") if isinstance(plan.get("payload"), dict) else {}
        planned_courses = payload.get("courses") if isinstance(payload, dict) else None
        if not isinstance(planned_courses, list):
            planned_courses = completed_courses

        completed_credits = _sum_credits(completed_courses)
        current_plan_credits = _sum_credits(planned_courses)
        return {
            "completed_courses": len(completed_courses),
            "remaining_courses": None,
            "completed_credits": completed_credits,
            "remaining_credits": None,
            "current_plan_courses": len(planned_courses),
            "current_plan_credits": current_plan_credits,
            "audit_status": "unknown_until_audit_tool_runs",
        }

    def _budgeted_tool_calls(
        self,
        tool_calls: list[dict[str, Any]],
        tool_counts: dict[str, int],
    ) -> list[dict[str, Any]]:
        allowed: list[dict[str, Any]] = []
        total_used = sum(tool_counts.values())
        for tool_call in tool_calls:
            if total_used + len(allowed) >= self.max_total_tool_calls:
                break
            tool_name = tool_call["name"]
            used_for_tool = tool_counts.get(tool_name, 0) + sum(
                1 for item in allowed if item["name"] == tool_name
            )
            if used_for_tool >= self.max_same_tool_calls:
                continue
            allowed.append(tool_call)
        return allowed

    async def _execute_tool_call(
        self,
        context: StudentContext,
        tool_call: dict[str, Any],
    ) -> dict[str, Any]:
        tool_name = tool_call["name"]
        if tool_name not in self.tools or tool_name not in SUPPORTED_TOOL_NAMES:
            return {
                "tool": tool_name,
                "success": False,
                "error": "Tool is not exposed to academic planning.",
            }
        if self.db is None:
            return {
                "tool": tool_name,
                "success": False,
                "error": "AcademicPlanningModule requires a database session.",
            }

        command = dict(tool_call["arguments"])
        try:
            result = await self._execute_tool(tool_name, context, command)
        except Exception as exc:
            return {
                "tool": tool_name,
                "success": False,
                "arguments": jsonable_encoder(command),
                "error": str(exc),
            }
        return {
            "tool": tool_name,
            "success": True,
            "arguments": jsonable_encoder(command),
            "result": jsonable_encoder(result),
        }

    def _tool_calls_from_response(self, response: LLMResponse) -> list[dict[str, Any]]:
        if response.tool_calls:
            return [
                {
                    "id": tool_call.id,
                    "name": tool_call.name,
                    "arguments": tool_call.arguments,
                }
                for tool_call in response.tool_calls
            ]

        parsed = self._command_payload(response.content)
        raw_calls = parsed.get("tool_calls")
        if not isinstance(raw_calls, list):
            return []

        tool_calls = []
        for item in raw_calls:
            if not isinstance(item, dict):
                continue
            name = item.get("name") or item.get("tool")
            arguments = item.get("arguments") or item.get("payload") or {}
            if isinstance(name, str) and isinstance(arguments, dict):
                tool_calls.append(
                    {
                        "id": item.get("id"),
                        "name": name,
                        "arguments": arguments,
                    }
                )
        return tool_calls

    async def _execute_tool(
        self,
        tool_name: str,
        context: StudentContext,
        command: dict[str, Any],
    ) -> Any:
        tool = self.tools[tool_name]
        payload = self._payload(command)

        if tool_name == "create_plan":
            return await tool.execute(self.db, self._create_plan_payload(context, command, payload))
        if tool_name == "update_plan":
            plan_id = self._plan_id(context, command)
            return await tool.execute(self.db, plan_id, self._update_plan_payload(command, payload))
        if tool_name == "delete_plan":
            return await tool.execute(self.db, self._plan_id(context, command))
        if tool_name == "get_plan":
            return await tool.execute(self.db, self._plan_id(context, command))
        if tool_name == "add_course":
            plan_id = self._plan_id(context, command)
            return await tool.execute(self.db, plan_id, self._course_create_payload(command, payload))
        if tool_name == "remove_course":
            return await tool.execute(
                self.db,
                self._plan_id(context, command),
                self._course_id(command, payload),
            )
        if tool_name == "move_course":
            return await tool.execute(
                self.db,
                self._plan_id(context, command),
                self._course_id(command, payload),
                self._course_update_payload(command, payload),
            )
        if tool_name == "validate_plan":
            return await tool.execute(self.db, self._plan_id(context, command), payload or None)
        if tool_name == "audit_plan":
            return await tool.execute(self.db, self._plan_id(context, command))
        if tool_name == "get_remaining_courses":
            return await tool.execute(self.db, self._plan_id(context, command))
        if tool_name == "get_course_details":
            return await tool.execute(self.db, self._course_id(command, payload))
        if tool_name == "get_prerequisites":
            return await tool.execute(self.db, self._course_id(command, payload))
        if tool_name == "get_corequisites":
            return await tool.execute(self.db, self._course_id(command, payload))
        if tool_name == "get_program_requirements":
            return await tool.execute(self.db, self._program_id(context, command, payload))
        if tool_name == "get_available_terms":
            return await tool.execute(self.db)

        raise ValueError(f"Unsupported academic planning tool: {tool_name}")

    @staticmethod
    def _command_payload(query: str) -> dict[str, Any]:
        stripped = query.strip()
        if not stripped:
            return {}
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            start = stripped.find("{")
            end = stripped.rfind("}")
            if start == -1 or end <= start:
                return {}
            try:
                parsed = json.loads(stripped[start : end + 1])
            except json.JSONDecodeError:
                return {}
        return parsed if isinstance(parsed, dict) else {}

    @staticmethod
    def _payload(command: dict[str, Any]) -> dict[str, Any]:
        payload = command.get("payload", command)
        return payload if isinstance(payload, dict) else {}

    @staticmethod
    def _plan_id(context: StudentContext, command: dict[str, Any]) -> str:
        plan = context.plan or {}
        plan_id = command.get("plan_id") or plan.get("plan_id")
        if not plan_id:
            raise ValueError("plan_id is required for this planning tool.")
        return str(plan_id)

    @staticmethod
    def _course_id(command: dict[str, Any], payload: dict[str, Any]) -> str:
        course_id = command.get("course_id") or payload.get("course_id")
        if not course_id:
            raise ValueError("course_id is required for this planning tool.")
        return str(course_id)

    @staticmethod
    def _program_id(
        context: StudentContext,
        command: dict[str, Any],
        payload: dict[str, Any],
    ) -> str:
        program = context.program or {}
        program_id = (
            command.get("program_id")
            or payload.get("program_id")
            or program.get("program_id")
        )
        if not program_id:
            raise ValueError("program_id is required for this planning tool.")
        return str(program_id)

    @staticmethod
    def _create_plan_payload(
        context: StudentContext,
        command: dict[str, Any],
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        user = context.user or {}
        university = context.university or {}
        program = context.program or {}
        return {
            "user_id": payload.get("user_id") or command.get("user_id") or user.get("id"),
            "university_id": (
                payload.get("university_id")
                or command.get("university_id")
                or university.get("university_id")
                or university.get("id")
            ),
            "program_id": (
                payload.get("program_id")
                or command.get("program_id")
                or program.get("program_id")
                or program.get("id")
            ),
            "plan_name": payload.get("plan_name") or command.get("plan_name") or "Academic Plan",
            "description": payload.get("description") or command.get("description"),
            "is_active": payload.get("is_active", command.get("is_active", True)),
        }

    @staticmethod
    def _update_plan_payload(command: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        return {
            key: value
            for key, value in {
                "plan_name": payload.get("plan_name") or command.get("plan_name"),
                "description": payload.get("description") or command.get("description"),
                "is_active": payload.get("is_active", command.get("is_active")),
            }.items()
            if value is not None
        }

    @staticmethod
    def _course_create_payload(command: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "course_id": payload.get("course_id") or command.get("course_id"),
            "planned_term_id": payload.get("planned_term_id") or command.get("planned_term_id"),
            "status": payload.get("status") or command.get("status") or "Planned",
            "notes": payload.get("notes") or command.get("notes"),
        }

    @staticmethod
    def _course_update_payload(command: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        return {
            key: value
            for key, value in {
                "planned_term_id": payload.get("planned_term_id")
                or command.get("planned_term_id"),
                "status": payload.get("status") or command.get("status"),
                "notes": payload.get("notes") or command.get("notes"),
            }.items()
            if value is not None
        }


def _sum_credits(courses: list[dict[str, Any]]) -> int:
    total = 0
    for course in courses:
        credits = course.get("credits")
        if isinstance(credits, int):
            total += credits
        elif isinstance(credits, str) and credits.isdigit():
            total += int(credits)
    return total


def _parse_uuid(value: Any) -> uuid.UUID | None:
    try:
        return uuid.UUID(str(value))
    except (TypeError, ValueError):
        return None


def _university_payload(university: Any) -> dict[str, Any]:
    return {
        "university_id": str(university.university_id),
        "university_name": university.university_name,
        "city": university.city,
        "state": university.state,
        "website": university.website,
    }


def _program_payload(program: Program) -> dict[str, Any]:
    return {
        "program_id": str(program.program_id),
        "university_id": str(program.university_id),
        "program_name": program.program_name,
        "degree": program.degree,
        "total_credit_hours": program.total_credit_hours,
    }


def _course_payload(course: Course) -> dict[str, Any]:
    return {
        "course_id": str(course.course_id),
        "program_id": str(course.program_id),
        "course_code": course.course_code,
        "course_name": course.course_name,
        "credits": course.credits,
        "recommended_year": course.recommended_year,
        "recommended_semester": course.recommended_semester,
        "description": course.description,
        "prerequisites": [
            _linked_course_payload(link.prerequisite_course)
            for link in course.prerequisite_links or []
            if link.prerequisite_course is not None
        ],
        "corequisites": [
            _linked_course_payload(link.corequisite_course)
            for link in course.corequisite_links or []
            if link.corequisite_course is not None
        ],
    }


def _linked_course_payload(course: Course) -> dict[str, Any]:
    return {
        "course_id": str(course.course_id),
        "course_code": course.course_code,
        "course_name": course.course_name,
        "credits": course.credits,
    }


def _course_sort_key(course: dict[str, Any]) -> tuple[int, int, str]:
    year = course.get("recommended_year")
    semester = str(course.get("recommended_semester") or "")
    semester_order = {"Fall": 1, "Winter": 2, "Spring": 3, "Summer": 4}
    return (
        year if isinstance(year, int) else 99,
        semester_order.get(semester, 9),
        str(course.get("course_code") or ""),
    )


def _schedule_remaining_courses(
    remaining_courses: list[dict[str, Any]],
    completed_ids: set[str],
    query: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    accelerated = any(
        token in query.lower()
        for token in ("accelerate", "early", "faster", "fast track", "graduate sooner")
    )
    target_credits = 16 if accelerated else 15
    max_credits = 18
    min_full_time_credits = 12

    remaining_by_id = {course["course_id"]: course for course in remaining_courses}
    unscheduled_ids = set(remaining_by_id)
    available_ids = set(completed_ids)
    semesters: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    for _ in range(16):
        if not unscheduled_ids:
            break

        eligible = [
            remaining_by_id[course_id]
            for course_id in unscheduled_ids
            if _prerequisites_met(remaining_by_id[course_id], available_ids)
        ]
        if not eligible:
            break

        selected: list[dict[str, Any]] = []
        selected_ids: set[str] = set()
        credits = 0
        for course in sorted(eligible, key=_course_sort_key):
            if course["course_id"] in selected_ids:
                continue
            course_credits = int(course.get("credits") or 0)
            if credits + course_credits > max_credits:
                continue
            selected.append(_planned_course_payload(course))
            selected_ids.add(course["course_id"])
            credits += course_credits

            for corequisite in course.get("corequisites", []):
                coreq_id = corequisite["course_id"]
                if coreq_id not in unscheduled_ids or coreq_id in selected_ids:
                    continue
                coreq = remaining_by_id[coreq_id]
                coreq_credits = int(coreq.get("credits") or 0)
                if credits + coreq_credits <= max_credits:
                    selected.append(_planned_course_payload(coreq))
                    selected_ids.add(coreq_id)
                    credits += coreq_credits

            if credits >= target_credits:
                break

        if not selected:
            break

        semester_number = len(semesters) + 1
        semesters.append(
            {
                "semester_number": semester_number,
                "label": _semester_label(semester_number),
                "credits": credits,
                "courses": selected,
            }
        )
        unscheduled_ids.difference_update(selected_ids)
        available_ids.update(selected_ids)

        if credits < min_full_time_credits and unscheduled_ids:
            warnings.append(
                {
                    "code": "LOW_CREDIT_LOAD",
                    "message": (
                        f"{_semester_label(semester_number)} has {credits} credits. "
                        "Review whether another eligible course can be added."
                    ),
                    "metadata": {"semester_number": semester_number, "credits": credits},
                }
            )

    blocked_courses = [
        remaining_by_id[course_id] for course_id in sorted(unscheduled_ids)
    ]
    for course in blocked_courses:
        missing = [
            prerequisite
            for prerequisite in course.get("prerequisites", [])
            if prerequisite["course_id"] not in available_ids
        ]
        warnings.append(
            {
                "code": "COURSE_BLOCKED_BY_PREREQUISITES",
                "message": (
                    f"{course['course_code']} could not be placed because prerequisite "
                    f"coursework is not yet satisfied."
                ),
                "metadata": {
                    "course_id": course["course_id"],
                    "course_code": course["course_code"],
                    "missing_prerequisites": missing,
                },
            }
        )
    return semesters, blocked_courses, warnings


def _prerequisites_met(course: dict[str, Any], available_ids: set[str]) -> bool:
    return all(
        prerequisite["course_id"] in available_ids
        for prerequisite in course.get("prerequisites", [])
    )


def _planned_course_payload(course: dict[str, Any]) -> dict[str, Any]:
    return {
        "course_id": course["course_id"],
        "course_code": course["course_code"],
        "course_name": course["course_name"],
        "credits": course["credits"],
        "prerequisites": course.get("prerequisites", []),
        "corequisites": course.get("corequisites", []),
    }


def _semester_label(semester_number: int) -> str:
    year = ((semester_number - 1) // 2) + 1
    term = "Fall" if semester_number % 2 == 1 else "Spring"
    return f"Year {year} {term}"


def _validate_structured_plan(
    completed_ids: set[str],
    semesters: list[dict[str, Any]],
    blocked_courses: list[dict[str, Any]],
    planning_warnings: list[dict[str, Any]],
) -> dict[str, Any]:
    warnings = list(planning_warnings)
    planned_ids: list[str] = []
    available_before_semester = set(completed_ids)

    for semester in semesters:
        semester_ids = {course["course_id"] for course in semester["courses"]}
        planned_ids.extend(semester_ids)
        if semester["credits"] > 18:
            warnings.append(
                {
                    "code": "CREDIT_OVERLOAD",
                    "message": (
                        f"{semester['label']} has {semester['credits']} credits, "
                        "which exceeds the 18-credit planning limit."
                    ),
                    "metadata": {
                        "semester_number": semester["semester_number"],
                        "credits": semester["credits"],
                    },
                }
            )

        for course in semester["courses"]:
            for prerequisite in course.get("prerequisites", []):
                if prerequisite["course_id"] not in available_before_semester:
                    warnings.append(
                        {
                            "code": "PREREQUISITE_SEQUENCE_WARNING",
                            "message": (
                                f"{course['course_code']} requires "
                                f"{prerequisite['course_code']} in an earlier semester."
                            ),
                            "metadata": {
                                "course_id": course["course_id"],
                                "prerequisite_course_id": prerequisite["course_id"],
                            },
                        }
                    )
            for corequisite in course.get("corequisites", []):
                coreq_id = corequisite["course_id"]
                if coreq_id not in completed_ids and coreq_id not in semester_ids:
                    warnings.append(
                        {
                            "code": "COREQUISITE_SEQUENCE_WARNING",
                            "message": (
                                f"{course['course_code']} should be planned with "
                                f"{corequisite['course_code']} in the same semester."
                            ),
                            "metadata": {
                                "course_id": course["course_id"],
                                "corequisite_course_id": coreq_id,
                            },
                        }
                    )
        available_before_semester.update(semester_ids)

    duplicate_ids = [
        course_id for course_id, count in Counter(planned_ids).items() if count > 1
    ]
    for course_id in duplicate_ids:
        warnings.append(
            {
                "code": "DUPLICATE_COURSE",
                "message": "A course appears more than once in the generated plan.",
                "metadata": {"course_id": course_id},
            }
        )

    return {
        "status": "warning" if warnings or blocked_courses else "valid",
        "warnings": warnings,
        "blocked_course_count": len(blocked_courses),
        "duplicate_course_count": len(duplicate_ids),
    }


def _prerequisite_notes(
    semesters: list[dict[str, Any]],
    blocked_courses: list[dict[str, Any]],
) -> list[str]:
    notes: list[str] = []
    for semester in semesters:
        for course in semester["courses"]:
            prerequisites = course.get("prerequisites", [])
            if prerequisites:
                codes = ", ".join(item["course_code"] for item in prerequisites)
                notes.append(
                    f"{course['course_code']} depends on prior completion of {codes}."
                )
    for course in blocked_courses:
        notes.append(
            f"{course['course_code']} needs advisor review before placement because "
            "its prerequisites are not satisfied by the available record."
        )
    return notes[:10]


def _academic_recommendations(validation: dict[str, Any], query: str) -> list[str]:
    recommendations = [
        "Confirm this sequence with your academic advisor before registration.",
        "Register for prerequisite-heavy courses as early as possible to avoid delaying later semesters.",
        "Keep each semester near 15 credits unless your advisor approves an accelerated load.",
    ]
    if validation["blocked_course_count"]:
        recommendations.insert(
            0,
            "Resolve blocked prerequisite records before finalizing the graduation timeline.",
        )
    if any(token in query.lower() for token in ("accelerate", "early", "faster")):
        recommendations.insert(
            0,
            "An accelerated path may require 16-18 credit semesters and careful prerequisite review.",
        )
    return recommendations
