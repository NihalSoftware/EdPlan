"""Answer-first orchestration. Only typed, read-only adapters are reachable on a turn."""

import asyncio
import logging
import re
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.mesa import catalog
from app.mesa.routing import SPEC, edits, followups, route, simplify, TWO_CREDENTIALS
from app.mesa.schemas import Action, Answer, IntentId, ResultTable, Source
from app.orchestrator.llm.llm_models import LLMMessage, LLMRequest
from app.orchestrator.llm.openrouter_provider import OpenRouterProvider
from app.student.domains.comparison.repositories.comparison_repository import comparison_repository

log = logging.getLogger(__name__)

# These capabilities need integrations. Ordinary suggestion buttons exclude them.
UNAVAILABLE = {"M23", "M24", "M25", "M28", "M29", "M32", "M33", "M34"}

class ClassifiedIntent(BaseModel):
    intent: IntentId


async def model_classify(message, fallback):
    if not settings.mesa_model_routing or not settings.openrouter_api_key or fallback != "M37":
        return fallback
    # Send taxonomy keywords, not the student's message or transcript, to the provider.
    from app.mesa.routing import SUBJECTS
    text = simplify(message)
    words = [word for word in ("compare", "college", "program", "degree", "credits", "cost", "tuition",
        "prerequisites", "transfer", "schedule", "career", "budget", "application", "aid", "enrollment",
        "semester", "online", "gpa", "retake", "employer", "internship", "advisor", "graduation", "plan")
        if re.search(r"\b" + word + r"\b", text)]
    words.extend(subject for subject, pattern in SUBJECTS.items() if re.search(pattern, text))
    if not words:
        return fallback
    request = LLMRequest(system_prompt="Return JSON with only an intent field. Classify these education taxonomy keywords. "
        + "; ".join(f"{key}: {value['label']}" for key, value in SPEC.items()),
        messages=[LLMMessage(role="user", content=", ".join(words))], temperature=0, max_tokens=50)
    try:
        result = await asyncio.wait_for(OpenRouterProvider().generate_structured(request, ClassifiedIntent), timeout=5)
        # Model classification cannot initiate private actions or modify baseline preferences.
        return result.intent if result.intent in {"M01", "M03", "M04", "M05", "M06", "M07", "M08", "M09", "M10",
                                                  "M11", "M12", "M13", "M14", "M15", "M35", "M37"} else fallback
    except Exception:
        return fallback


def partial(intent, text, *, link=None, label=None, sources=None, clarification=None, status="partial"):
    return Answer(intent=intent, text=text, status=status, link=link, link_label=label,
                  sources=sources or [], clarification=clarification)


async def respond(db, message, context, *, user_id, prior_intent=None, choice=None, previous=()):
    intent = choice.intent if choice else await model_classify(message, route(message, prior_intent))
    text = simplify(message)
    if intent == "M36" and context.scenario is None and re.search(r"budget|credits|campus|credential", text):
        intent = prior_intent if prior_intent in {"M04", "M05", "M09", "M10", "M11"} else "M36"
    context = edits(message, context, intent)
    if choice and choice.program_id:
        program = await catalog.selected_program(db, choice.program_id)
        if program:
            context = context.model_copy(update={"program_id": program.program_id, "campus": program.university.university_name})
    if choice and choice.plan_id:
        context = context.model_copy(update={"plan_id": choice.plan_id})
    try:
        # A data provider error rolls back only the read adapter savepoint.
        async with db.begin_nested():
            answer = await handle(db, intent, text, context, user_id)
    except (SQLAlchemyError, TimeoutError):
        log.warning("mesa.catalog_unavailable intent=%s", intent)
        answer = partial(intent, "The catalog service is unavailable for this turn. Your selections are still available. You can retry or browse official college information.",
                         link="/uni", label="Browse colleges", status="unavailable")
    ranked = followups(intent, context, message, previous, UNAVAILABLE)
    answer.suggestions, answer.follow_more = ranked[:5], ranked[5:]
    return context, answer


async def handle(db, intent, text, context, user_id):
    if intent == "M38":
        return partial(intent, "If you’re in immediate danger, contact local emergency services now. If you can, reach out to someone you trust who can stay with you. For an urgent school decision or a personal concern, your college’s counseling or student support office can help directly.", status="sensitive")
    if intent == "M01":
        return Answer(intent=intent, text="I can help you explore careers, find New Mexico programs, compare costs, and turn a catalog into a course plan. What would you like to explore today?")
    if intent == "M35":
        if "credit" in text:
            explanation = "A credit hour measures academic work attached to a course. A two-credit course normally contributes two credits toward eligible requirements. A degree is a credential earned by completing the full program, including its required courses and credits."
        elif "net price" in text:
            explanation = "Net price is cost of attendance minus grant and scholarship aid. An institution’s published average net price summarizes a student cohort. Your own net price depends on your costs and grant aid."
        elif "gpa" in text:
            explanation = "GPA divides total grade points by graded credits. Multiply each grade’s points by the course’s credits before adding them. Check your institution’s rules for repeats and exclusions."
        elif "corequisite" in text or "prerequisite" in text:
            explanation = "A prerequisite must generally be completed before the course. A corequisite is generally taken in the same term or previously completed if the catalog allows it."
        elif "information" in text or "privacy" in text:
            explanation = "Mesa keeps conversation context temporarily. Signed-in students can choose to keep a conversation for 30 days and delete it sooner. Conversation choices do not edit your permanent student profile."
        else:
            explanation = "Mesa labels the source of catalog and Scorecard figures. Check the institution’s source for the current year, metric definition, and official requirements."
        return Answer(intent=intent, text=explanation)
    if intent == "M02":
        if context.education_stage == "GED":
            suffix = " Nursing programs may have additional admission steps and prerequisites." if context.subject == "nursing" else ""
            return Answer(intent=intent, text="I’ll use your GED as your education stage for this conversation. Many colleges consider a GED for general admission. Verify acceptance and program-specific requirements with the college." + suffix)
        if context.tuition_category == "international":
            return Answer(intent=intent, text="I’ll keep international student status as self-reported context. An institution’s official policy determines your tuition classification and any additional fees.")
        return Answer(intent=intent, text="You can explore without creating a profile. Mesa can use your education stage, goals, and study preferences in this conversation.",
                      link="/intake", link_label="Open student onboarding")
    if intent == "M36":
        return Answer(intent=intent, text="I’ve applied your correction to this conversation. You can review or clear individual preferences in the context panel.")
    if intent in {"M04", "M08", "M09", "M10", "M14", "M15"}:
        from app.mesa.routing import CAMPUS_ALIASES
        campuses = [name for name, pattern in CAMPUS_ALIASES.items() if re.search(pattern, text)]
        return await catalog.compare(db, context, intent, bool(context.subject or context.credential), text, campuses)
    if intent in {"M05", "M06", "M07", "M16", "M17"}:
        if intent == "M07" and not context.campus and not context.subject:
            return partial(intent, "College admission and entry into a specific program may have different requirements. A college’s admissions office can confirm eligibility and deadlines.",
                           clarification="Which college and program are you considering?")
        if context.program_id:
            program = await catalog.selected_program(db, context.program_id)
            if program:
                if intent == "M07":
                    return partial(intent, f"Check {program.university.university_name} for the official {program.program_name} application dates and admission requirements. The catalog data here cannot verify eligibility or open seats.",
                                   sources=catalog.institution_sources([program.university]))
                return await catalog.program_detail(db, program, intent)
        if intent == "M05" and context.subject == "nursing" and context.credential == "associate" and "pathway" in text:
            return Answer(intent=intent, text="An ADN pathway generally includes college admission, published prerequisites, nursing program admission, clinical training, and licensure steps. Choose the college’s current catalog for exact sequencing.")
        if not (context.subject or context.campus or context.credential):
            return partial(intent, "I can use your college’s catalog and program requirements to find a program or prepare a course-plan preview.",
                           clarification="Which subject, credential, or college should I look up?")
        answer = await catalog.compare(db, context, intent, True, text)
        if intent in {"M07", "M16", "M17"} and answer.choices:
            answer.clarification = "Which program should I look at?"
            answer.choices = [item.model_copy(update={"intent": intent}) for item in answer.choices]
        return answer
    if intent in {"M03", "M13", "M26"}:
        if context.subject == "nursing":
            intro = "Registered nursing commonly has associate (ADN) and bachelor’s (BSN) routes. Both require program-specific preparation and licensure. An ADN is an associate credential. A BSN is a bachelor’s credential with a broader degree curriculum."
        else:
            intro = "Start with the kind of work you want to do, then compare programs that prepare you for it."
        programs = await catalog.find_programs(db, context, limit=6) if context.subject or context.program_id else []
        ids = [str(item.program_id) for item in programs]
        careers = await comparison_repository.get_careers_for_programs(db, ids) if ids else {}
        rows = [[p.program_name, career["career_name"]] for p in programs
                for career in careers.get(str(p.program_id), [])][:18]
        answer = partial(intent, intro + (" Program-to-career mappings are shown below." if rows else ""),
                         link="/career", label="Browse career pathways",
                         sources=[Source(title="Bureau of Labor Statistics Occupational Outlook Handbook", url=catalog.OCCUPATIONS)])
        if rows:
            answer.tables = [ResultTable(title="Catalog career mappings", columns=["Program", "Occupation"], rows=rows)]
        if intent == "M13":
            answer.text += " Compare wages for a specific occupation, place, and reporting period. Mesa cannot estimate your personal earnings or return from a degree."
        return answer
    if intent == "M11":
        answer = partial(intent, "Tuition is based on your institution’s rate category, academic year, and credit load. Mandatory fees and program charges may be separate. Residency and international classifications follow the college’s published policy.")
        if context.campus or context.subject:
            result = await catalog.compare(db, context, intent, bool(context.subject and not context.campus), text)
            answer.text += "\n\n" + result.text
            answer.tables, answer.sources = result.tables, result.sources
            answer.clarification = result.clarification
        else:
            answer.clarification = "Which college should I use for the estimate?"
        return answer
    if intent == "M12":
        return partial(intent, "Compare grants and scholarships before loans. The FAFSA helps participating schools determine federal aid. New Mexico aid programs have their own current rules. An aid office can review your eligibility and award.",
                       link="/financial-aid", label="Open Financial Aid", sources=[
                           Source(title="Federal Student Aid", url=catalog.FEDERAL_AID), Source(title="New Mexico Higher Education Department", url=catalog.NM_AID)])
    if intent in {"M19", "M20"}:
        return partial(intent, "Start with the receiving institution’s course equivalencies and degree rules. Credit acceptance, placement, and applicability to your program are separate decisions. Bring your official record to the registrar for an evaluation.",
                       sources=[Source(title="New Mexico common course numbering", url=catalog.TRANSFER)], link="/intake", label="Open student onboarding")
    if intent in {"M18", "M21", "M22", "M27", "M34"}:
        plan = await catalog.owned_plan(db, user_id, context.plan_id)
        if intent in {"M27", "M34"}:
            return await simulate_credits(db, intent, text, context, user_id, plan)
        if intent == "M18":
            return partial(intent, "Course offerings depend on the term and available catalog sections. Use Schedule Generator to see time and conflict checks for your selected plan.",
                           link="/schedule-generator", label="Open Schedule Generator")
        if not plan:
            answer = await catalog.list_owned_plans(db, user_id, intent)
            if "advisor" in text:
                answer.text = "Choose a plan to prepare for advisor review. Mesa needs a verified recipient and delivery integration to send it. " + answer.text
            if re.search(r"\bsave (?:this|my).*plan", text) and context.program_id:
                answer.link, answer.link_label = f"/educationplan?program_id={context.program_id}", "Review and save in Education Planner"
            return answer
        answer = await catalog.plan_preview(db, plan, intent)
        if "advisor" in text:
            answer.text += " Open the saved plan to review or download a copy for your advisor. Mesa has no verified advisor recipient for this account."
            answer.status = "partial"
        return answer
    if intent == "M30":
        return partial(intent, "I’ve kept the What-If assumptions separate from your actual student status. Compare published rate categories and verified fees with the financial aid office. A change in location alone does not establish your tuition classification.", link="/financial-aid", label="Open Financial Aid")
    if intent == "M31":
        return gpa_answer(intent, text)
    if intent in {"M23", "M24", "M25"}:
        return partial(intent, "Mesa has no verified employer-site, routing, or vacancy feed for this search. Use the state job portal for current listings. A nearby employer may have no open positions or clinical partnership.",
                       sources=[Source(title="New Mexico Department of Workforce Solutions job portal", url="https://www.jobs.dws.nm.gov/vosnet/default.aspx")],
                       status="unavailable")
    if intent in {"M28", "M29", "M32", "M33"}:
        return partial(intent, "This scenario needs more verified inputs than Mesa has for the selected baseline. Review the relevant requirements and offerings in the planner before comparing outcomes.",
                       link="/educationplan", label="Open Education Planner", status="unavailable")
    return partial(intent, "Choose a college, program, education plan, or scenario so I can connect your question to the right data.", clarification="What would you like to evaluate?")


async def simulate_credits(db, intent, text, context, user_id, plan):
    scenario = context.scenario
    changed = scenario.credits_per_term if scenario else None
    base = (scenario.baseline_credits if scenario else None) or context.credits_per_term or 15
    remaining = scenario.remaining_credits if scenario else None
    if remaining is None and plan and plan.program:
        completed = sum(item.course.credits for item in plan.courses if item.course and item.status.lower() == "completed")
        remaining = max(0, plan.program.total_credit_hours - completed)
    validation = None
    if plan:
        validation = await catalog.planning_validation_service.validate_plan(db, str(plan.plan_id))
    if remaining is None or changed is None:
        answer = partial(intent, "A smaller credit load can increase the minimum number of terms needed. An actual schedule also depends on course prerequisites and offerings.",
                         clarification="How many credits are left, and how many would you take per term?")
        if user_id is not None and plan is None:
            answer.choices = (await catalog.list_owned_plans(db, user_id, intent)).choices
            answer.choices = [item.model_copy(update={"intent": intent}) for item in answer.choices]
        return answer
    table = catalog.credit_scenario(remaining, base, changed)
    result = partial(intent, f"This comparison uses {remaining} remaining credits and a baseline of {base} credits per term. The term count is a lower bound. It depends on actual course sequencing, prerequisites, and offerings.",
                     sources=[Source(title="Owned plan and recorded completed courses" if plan else "Student-provided scenario assumptions")])
    result.tables = [table]
    if scenario and scenario.include_summer:
        result.text += " Summer sections are unverified, so the projection does not assume summer availability."
    if validation and validation.get("issues"):
        result.text += " The baseline has recorded rule issues. Review the saved plan before scheduling."
    return result


def gpa_answer(intent, text):
    match = re.search(r"gpa (?:of )?(\d(?:\.\d{1,3})?) .*?(\d{1,3}) (?:graded )?credits.*?\b([abcd][+-]?|f)\b (?:in|for) (\d{1,2}) credits", text)
    if not match:
        return partial(intent, "GPA projections weight each grade by the credits attached to it.",
                       clarification="What is your current GPA and number of graded credits, and what grade and credits should I model?")
    gpa, credits, grade, new_credits = float(match[1]), int(match[2]), match[3], int(match[4])
    if not (0 <= gpa <= 4 and credits > 0 and new_credits > 0):
        return partial(intent, "Provide a GPA from 0 to 4 and positive graded credit counts.")
    points = {"a": 4, "b": 3, "c": 2, "d": 1, "f": 0}[grade[0]]
    points = min(4, max(0, points + (0.3 if grade.endswith("+") else -0.3 if grade.endswith("-") else 0)))
    new = round((gpa * credits + points * new_credits) / (credits + new_credits), 3)
    return Answer(intent=intent, text="This uses a standard four-point model and the grades you provided. Your institution may use different grade or repeat policies.", tables=[
        ResultTable(title="GPA projection", columns=["Baseline", "Scenario", "Difference"], rows=[[gpa, new, round(new-gpa, 3)]])
    ], sources=[Source(title="Student-provided scenario assumptions")])


def scenario_save(preview):
    return Action(id=uuid4(), description="Save a separate What-If scenario to this conversation.", preview=preview,
                  expires_at=(datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat())
