"""Read-only Mesa adapters over EdPlan catalog and planning services."""

import asyncio
from math import ceil
from urllib.parse import urlencode, urlsplit
from uuid import uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from app.mesa.schemas import Answer, Choice, ResultTable, Source
from app.student.domains.discovery.clients.college_scorecard import client as college_scorecard_client
from app.student.domains.discovery.models import Course, Program, University
from app.student.domains.planning.models.normalized_plan import EdPlan, PlanCourse
from app.student.domains.planning.services.graduation_audit_service import graduation_audit_service
from app.student.domains.planning.services.planning_validation_service import planning_validation_service

SCORECARD = "https://collegescorecard.ed.gov/data/"
FEDERAL_AID = "https://studentaid.gov/"
NM_AID = "https://hed.nm.gov/free-college-for-new-mexico"
TRANSFER = "https://hed.nm.gov/resources-for-schools/public_schools/nm-course-numbering-system"
OCCUPATIONS = "https://www.bls.gov/ooh/"
NM_STATES = ("nm", "new mexico")
TERM_ORDER = {"Fall": 0, "Winter": 1, "Spring": 2, "Summer": 3}
CREDENTIALS = {
    "associate": ("associate", "adn", "aas", "a.a.s.", "as", "a.s."),
    "bachelor": ("bachelor", "bsn", "bs", "b.s.", "ba", "b.a."),
    "certificate": ("certificate",),
    "master": ("master",),
    "doctorate": ("doctor", "phd"),
}


def safe_url(value):
    if not isinstance(value, str):
        return None
    try:
        url = urlsplit(value)
        if url.scheme == "https" and url.hostname and not url.username and not url.password:
            return value
    except ValueError:
        pass
    return None


def institution_sources(universities):
    sources = []
    for item in universities:
        url = safe_url(item.website)
        if url and all(source.url != url for source in sources):
            sources.append(Source(title=item.university_name, url=url))
    return sources[:8]


async def find_programs(db, context, limit=30, campuses=()):
    query = select(Program).join(University).options(selectinload(Program.university)).where(
        func.lower(University.state).in_(NM_STATES)
    )
    if context.subject:
        terms = ("health", "nursing", "medical") if context.subject == "healthcare" else (context.subject,)
        query = query.where(or_(*(Program.program_name.ilike(
            "%" + term.replace("%", "").replace("_", "") + "%"
        ) for term in terms)))
    names = campuses or ((context.campus,) if context.campus else ())
    if names:
        query = query.where(or_(*(University.university_name.ilike("%" + name.replace("%", "").replace("_", "") + "%") for name in names)))
    elif context.city and not context.max_drive_minutes:
        query = query.where(func.lower(University.city) == context.city.lower())
    if context.credential:
        credential = func.lower(Program.degree)
        labels = CREDENTIALS[context.credential]
        query = query.where(or_(credential.contains(labels[0]), credential.in_(labels)))
    return (await db.scalars(query.order_by(Program.program_name, University.university_name).limit(limit))).all()


async def find_universities(db, context, campuses=()):
    query = select(University).where(func.lower(University.state).in_(NM_STATES))
    names = campuses or ((context.campus,) if context.campus else ())
    if names:
        query = query.where(or_(*(University.university_name.ilike("%" + name.replace("%", "").replace("_", "") + "%") for name in names)))
    elif context.city and not context.max_drive_minutes:
        query = query.where(func.lower(University.city) == context.city.lower())
    return (await db.scalars(query.order_by(University.university_name).limit(30))).all()


async def public_metrics(universities):
    profiles = [{"name": u.university_name, "city": u.city, "state": u.state} for u in universities]
    try:
        records = await asyncio.wait_for(college_scorecard_client.find_schools_by_profiles(profiles), timeout=6)
    except Exception:
        records = []
    return {u.university_id: (records[i] or {}) if i < len(records) else {} for i, u in enumerate(universities)}


async def compare(db, context, intent, program_search, message, campuses=()):
    programs = await find_programs(db, context, campuses=campuses) if program_search else []
    universities = list({p.university_id: p.university for p in programs}.values()) if program_search else await find_universities(db, context, campuses)
    if not universities:
        return Answer(intent=intent, status="partial", text="No catalog records match the current subject, credential, and campus filters. Try removing one filter or checking a college’s official catalog.")
    if context.max_drive_minutes or context.online_only:
        missing = "driving-time" if context.max_drive_minutes else "online delivery"
        return Answer(intent=intent, status="partial",
                      text=f"Your filters are retained. The current sources cannot verify {missing} for these results, so Mesa cannot list any as confirmed matches.",
                      clarification="Which city or ZIP should I use as the starting point?" if context.max_drive_minutes and not context.city else None,
                      sources=institution_sources(universities))
    metrics_requested = intent in {"M09", "M10", "M11", "M13", "M14"} or context.budget_annual is not None
    metrics = await public_metrics(universities) if metrics_requested or context.public_only else {}
    if context.public_only:
        unfiltered_universities = universities
        universities = [
            u for u in universities
            if metrics.get(u.university_id, {}).get("organization_type") == "Public"
        ]
        if not universities:
            return Answer(intent=intent, status="partial",
                          text="The available sources do not verify public-college matches for these filters.",
                          sources=institution_sources(unfiltered_universities))
    tuition_key = {"resident": "in_state_tuition", "nonresident": "out_of_state_tuition"}.get(context.tuition_category)
    cost_key = tuition_key if context.budget_basis == "tuition" else "average_annual_cost"
    if context.budget_annual is not None and context.budget_basis is None:
        return Answer(intent=intent, status="clarification",
                      text="Your annual budget is saved for this conversation. A college’s published tuition and a student’s full annual cost measure different things.",
                      clarification="Does your budget cover published tuition only or annual cost of attendance?")
    if context.budget_annual is not None and not cost_key:
        return Answer(intent=intent, status="clarification", text="Your annual tuition budget is retained.",
                      clarification="Which tuition category should I use: in-state or out-of-state?")
    if context.budget_annual is not None:
        universities = [u for u in universities if isinstance(metrics[u.university_id].get(cost_key), (int, float))
                        and metrics[u.university_id][cost_key] <= context.budget_annual]
    ids = {u.university_id for u in universities}
    programs = [p for p in programs if p.university_id in ids]
    if not universities:
        return Answer(intent=intent, status="partial", text="No row with a published rate meets the annual budget and your other filters. Rows with unknown rates cannot be counted as matches.")
    if context.sort_by == "tuition" and tuition_key:
        def order(u):
            value = metrics.get(u.university_id, {}).get(tuition_key)
            return (value is None, value or 0, u.university_name)
    elif context.sort_by == "graduation_rate":
        def order(u):
            value = metrics.get(u.university_id, {}).get("graduation_rate")
            return (value is None, -(value or 0), u.university_name)
    else:
        def order(u):
            return (u.university_name,)
    universities.sort(key=order)
    if context.sort_by == "credits":
        programs.sort(key=lambda p: (p.total_credit_hours is None, p.total_credit_hours or 0, *order(p.university)))
    else:
        programs.sort(key=lambda p: (*order(p.university), p.program_name))
    table = ResultTable(title="New Mexico catalog matches", columns=["Institution", "City"], rows=[])
    choices = []
    if programs:
        table.columns += ["Program", "Credential", "Credits"]
        for program in programs[:12]:
            u = program.university
            table.rows.append([u.university_name, u.city, program.program_name, program.degree, program.total_credit_hours])
            if len(choices) < 6:
                choices.append(Choice(id=uuid4(), label=f"{program.program_name} · {u.university_name}", intent="M05",
                                      kind="clarification", program_id=program.program_id))
    else:
        table.rows = [[u.university_name, u.city] for u in universities[:12]]
    if metrics_requested:
        cost = ResultTable(title="Published institution-level measures",
            columns=["Institution", "Data year", "In-state tuition ($)", "Out-of-state tuition ($)",
                     "Average annual cost ($)", "Graduation rate (%)", "Retention rate (%)", "Median earnings ($)"],
            rows=[[u.university_name, metrics.get(u.university_id, {}).get("year"),
                   metrics.get(u.university_id, {}).get("in_state_tuition"),
                   metrics.get(u.university_id, {}).get("out_of_state_tuition"),
                   metrics.get(u.university_id, {}).get("average_annual_cost"),
                   percent(metrics.get(u.university_id, {}).get("graduation_rate")),
                   percent(metrics.get(u.university_id, {}).get("first_year_return_rate")),
                   metrics.get(u.university_id, {}).get("median_earnings")] for u in universities[:12]])
    sources = [Source(title="EdPlan institutional catalog")] + institution_sources(universities)
    if metrics_requested:
        sources.append(Source(title="U.S. Department of Education College Scorecard", url=SCORECARD))
    description = "Here are matching records from the EdPlan institutional catalog."
    if metrics_requested:
        if context.budget_basis == "attendance":
            description += " The budget filter uses published institution averages. Actual costs depend on housing, fees, and aid."
        description += " Published annual tuition and outcomes describe the institution. Program fees, deadlines, and individual aid require the institution’s current official information."
        if not any(metrics.values()):
            description += " Scorecard figures are currently unavailable."
    if context.sort_by == "tuition" and not tuition_key:
        description += " Choose a tuition category before ranking by cost."
    return Answer(intent=intent, text=description, status="partial" if metrics_requested else "answered", sources=sources,
                  tables=[table, cost] if metrics_requested else [table], choices=choices,
                  link="/compare" if metrics_requested else "/uni",
                  link_label="Open college comparison" if metrics_requested else "Browse colleges")


def percent(value):
    return round(value * 100, 1) if isinstance(value, (int, float)) and 0 <= value <= 1 else value


async def selected_program(db, program_id):
    return (await db.scalars(select(Program).options(selectinload(Program.university)).where(
        Program.program_id == program_id
    ))).one_or_none()


async def program_detail(db, program, intent):
    courses = (await db.scalars(select(Course).where(Course.program_id == program.program_id)
        .options(selectinload(Course.prerequisite_links), selectinload(Course.corequisite_links))
        .order_by(Course.course_code))).all()
    eligible = [c for c in courses if c.default_plan_eligible]
    ordered = sorted(eligible, key=lambda c: (c.recommended_year, TERM_ORDER.get(c.recommended_semester, 99), c.course_code))
    positions = {c.course_id: (c.recommended_year, TERM_ORDER.get(c.recommended_semester, 99)) for c in ordered}
    by_id = {c.course_id: c.course_code for c in courses}
    warnings = []
    for course in ordered:
        position = positions[course.course_id]
        for link in course.prerequisite_links:
            required = link.prerequisite_course_id
            if required not in positions or positions[required] >= position:
                warnings.append(f"{course.course_code} requires {by_id.get(required, 'an earlier prerequisite')}.")
        for link in course.corequisite_links:
            required = link.corequisite_course_id
            if required not in positions or positions[required] != position:
                warnings.append(f"{course.course_code} needs a corequisite in the same term.")
    totals = {}
    for course in ordered:
        key = positions[course.course_id]
        totals[key] = totals.get(key, 0) + course.credits
    if any(credits > 18 for credits in totals.values()):
        warnings.append("At least one catalog term exceeds 18 credits.")
    table = ResultTable(title="Catalog sequence preview", columns=["Year", "Term", "Course", "Credits"],
                        rows=[[c.recommended_year, c.recommended_semester, f"{c.course_code} · {c.course_name}", c.credits]
                              for c in ordered[:80]])
    if intent == "M17":
        table = ResultTable(title="Recorded course dependencies", columns=["Course", "Prerequisites", "Corequisites"],
            rows=[[c.course_code,
                   ", ".join(by_id.get(link.prerequisite_course_id, "See catalog") for link in c.prerequisite_links) or None,
                   ", ".join(by_id.get(link.corequisite_course_id, "See catalog") for link in c.corequisite_links) or None]
                  for c in courses if c.prerequisite_links or c.corequisite_links][:80])
    metadata = program.metadata_json or {}
    catalog_url = safe_url(metadata.get("official_source_url") or metadata.get("catalog_url"))
    sources = institution_sources([program.university])
    if catalog_url:
        sources.insert(0, Source(title="Official program catalog", url=catalog_url,
                                 observed=str(metadata.get("catalog_year") or "") or None))
    text = f"{program.program_name} at {program.university.university_name} lists {program.total_credit_hours} total credits for its {program.degree} credential."
    text += " The preview uses available catalog recommendations. Confirm minimum grades, required electives, catalog year, and actual term offerings with the college."
    if warnings and intent != "M05":
        text += "\n\nRecorded sequencing issues:\n" + "\n".join(f"- {item}" for item in warnings[:8])
    if not table.rows:
        text += " This catalog record does not include the course details needed for this view."
    return Answer(intent=intent, text=text, status="partial", tables=[table] if table.rows else [],
                  sources=[Source(title="EdPlan institutional catalog"), *sources],
                  link="/educationplan?" + urlencode({"program_id": str(program.program_id)}),
                  link_label="Open this program in Education Planner")


async def owned_plan(db, user_id, plan_id):
    if user_id is None or plan_id is None:
        return None
    return (await db.scalars(select(EdPlan).options(
        selectinload(EdPlan.courses).selectinload(PlanCourse.course), selectinload(EdPlan.program)
    ).where(EdPlan.plan_id == plan_id, EdPlan.user_id == user_id, EdPlan.is_active.is_(True)))).one_or_none()


async def list_owned_plans(db, user_id, intent):
    if user_id is None:
        return Answer(intent=intent, status="partial", text="Sign in to view your saved education plans.",
                      link="/login?next=%2Fmesa", link_label="Sign in")
    plans = (await db.scalars(select(EdPlan).where(EdPlan.user_id == user_id, EdPlan.is_active.is_(True))
                              .order_by(EdPlan.updated_at.desc()).limit(8))).all()
    if not plans:
        return Answer(intent=intent, status="partial", text="You don’t have a saved normalized plan Mesa can review. Choose a catalog program to prepare a draft.",
                      link="/view", link_label="Open saved plans")
    return Answer(intent=intent, text="Select one of your saved plans to preview and validate it.",
                  choices=[Choice(id=uuid4(), label=p.plan_name, intent=intent, kind="clarification", plan_id=p.plan_id)
                           for p in plans])


async def plan_preview(db, plan, intent):
    validation = await planning_validation_service.validate_plan(db, str(plan.plan_id))
    issues = validation.get("issues") or []
    courses = [[item.course.course_code, item.course.course_name, item.course.credits, item.status]
               for item in plan.courses if item.course]
    text = f"Here is your saved plan, {plan.plan_name}."
    text += f" The current rule checker reported {len(issues)} issue(s). Review college requirements before relying on this plan."
    if issues:
        text += "\n" + "\n".join(f"- {issue.get('message', 'Review this course requirement')}" for issue in issues[:8])
    if intent == "M22":
        audit = await graduation_audit_service.get_audit(db, str(plan.plan_id))
        if audit.get("remaining_credits") is not None:
            text += f" The plan audit lists {audit['remaining_credits']} remaining credits."
    return Answer(intent=intent, text=text, tables=[
        ResultTable(title="Saved plan preview", columns=["Code", "Course", "Credits", "Recorded status"], rows=courses)
    ], sources=[Source(title="Owned EdPlan record and current catalog rules")], link="/view", link_label="Open saved plans")


def credit_scenario(remaining, base_load, new_load):
    return ResultTable(title="Credit-load scenario", columns=["Measure", "Baseline", "Scenario", "Difference"], rows=[
        ["Credits per term", base_load, new_load, new_load - base_load],
        ["Remaining credits", remaining, remaining, 0],
        ["Minimum terms by credit load", ceil(remaining / base_load), ceil(remaining / new_load),
         ceil(remaining / new_load) - ceil(remaining / base_load)],
    ])
