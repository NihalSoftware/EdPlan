"""Read-only analytics over a deduplicated plan projection. Never select plan payloads."""
from datetime import date, datetime, timedelta, timezone
from typing import Literal

from fastapi import HTTPException
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import case, distinct, exists, func, select, union_all
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.models.education_plan import EducationPlan
from app.student.domains.planning.models.normalized_plan import EdPlan
from app.student.domains.discovery.models.program import Program, University

MIN_CELL_SIZE = 5  # Product disclosure policy, NOT a statutory FERPA threshold.


def require_management(user):
    if user.role != UserRole.ADMIN or not user.is_active or user.is_deactivated:
        raise HTTPException(403, "Management analytics requires an active administrator")


class Filters(BaseModel):
    period: Literal["7", "30", "90", "custom", "all"] = "30"
    start: date | None = None
    end: date | None = None
    institution: str | None = Field(None, max_length=256)
    program: str | None = Field(None, max_length=256)
    degree: str | None = Field(None, max_length=128)

    @model_validator(mode="after")
    def valid_dates(self):
        if self.period == "custom":
            if not self.start or not self.end or self.end < self.start:
                raise ValueError("Custom range requires ordered start and end dates")
            if (self.end - self.start).days > 365:
                raise ValueError("Custom range must be at most 366 days")
        elif self.start or self.end:
            raise ValueError("Dates are only accepted for a custom range")
        return self

    def bounds(self, now: datetime):
        # Complete UTC days; avoid comparing today's partial day to a complete day.
        end = datetime.combine(now.date(), datetime.min.time(), timezone.utc)
        if self.period == "all":
            return None, now
        if self.period == "custom":
            return (datetime.combine(self.start, datetime.min.time(), timezone.utc),
                    datetime.combine(self.end + timedelta(days=1), datetime.min.time(), timezone.utc))
        return end - timedelta(days=int(self.period)), end


class Metric(BaseModel):
    id: str
    label: str
    pillar: Literal["Engagement", "Progress", "Impact"]
    value: float | int | None = None
    status: Literal["available", "unavailable", "suppressed"] = "available"
    definition: str
    source: str
    delta: float | None = None
    unit: str = "count"


class Breakdown(BaseModel):
    label: str
    plans: int
    students: int


class Dashboard(BaseModel):
    population: str
    refreshed_at: datetime
    period_start: datetime | None
    period_end_exclusive: datetime
    timezone: str = "UTC"
    coverage: str
    filters: Filters
    privacy: str
    metrics: list[Metric]
    trend: list[dict]
    programs: list[Breakdown]
    institutions: list[Breakdown]
    degrees: list[Breakdown]
    options: dict[str, list[str]]
    attention: list[dict]
    decision_note: list[str]
    unavailable: dict[str, str]


def clean(column):
    return func.lower(func.coalesce(func.nullif(func.trim(column), ""), "Not provided"))


def institution_name(column):
    value = clean(column)
    return case(
        (value == "new mexico state university-main campus", "new mexico state university"),
        (value == "university of new mexico-main campus", "university of new mexico"),
        else_=value,
    )


def plan_projection():
    legacy, modern = EducationPlan.__table__, EdPlan.__table__
    programs, universities = Program.__table__, University.__table__
    # A linked normalized plan represents its legacy row, including when deactivated.
    old = select(
        legacy.c.user_id, institution_name(legacy.c.university_name).label("institution"),
        clean(legacy.c.program_name).label("program"), clean(legacy.c.degree).label("degree"),
        legacy.c.created_at, legacy.c.updated_at,
    ).where(~exists(select(1).where(modern.c.legacy_education_plan_id == legacy.c.id)))
    joined = modern.outerjoin(legacy, modern.c.legacy_education_plan_id == legacy.c.id).outerjoin(
        programs, modern.c.program_id == programs.c.program_id
    ).outerjoin(universities, modern.c.university_id == universities.c.university_id)
    new = select(
        modern.c.user_id, institution_name(universities.c.university_name).label("institution"),
        clean(programs.c.program_name).label("program"), clean(programs.c.degree).label("degree"),
        func.coalesce(legacy.c.created_at, modern.c.created_at).label("created_at"),
        case((legacy.c.updated_at > modern.c.updated_at, legacy.c.updated_at),
             else_=modern.c.updated_at).label("updated_at"),
    ).select_from(joined).where(modern.c.is_active.is_(True))
    plans = union_all(old, new).subquery("deduplicated_plans")
    users = User.__table__
    return select(plans).join(users, users.c.id == plans.c.user_id).where(
        users.c.role == UserRole.CUSTOMER, users.c.is_active.is_(True),
        users.c.is_deactivated.is_(False),
    ).subquery("eligible_plans")


def period_query(plans, filters, start, end):
    query = select(plans).where(
        ((plans.c.created_at < end) | plans.c.created_at.is_(None)) if start is None
        else plans.c.created_at < end
    )
    if start:
        query = query.where(plans.c.created_at >= start)
    for key in ("institution", "program", "degree"):
        value = getattr(filters, key)
        if value:
            query = query.where(plans.c[key] == value.strip().lower())
    return query.subquery()


def utc_day(db, column):
    # PostgreSQL timestamptz date extraction must not depend on session timezone.
    value = func.timezone("UTC", column) if db.bind.dialect.name == "postgresql" else column
    return func.date(value)


async def cohort_is_releasable(db, plans):
    # Fixed atomic cells cover every allowed date/dimension partition. Withholding
    # any report containing a small cell prevents subtraction using wider filters.
    cells = select(func.count(distinct(plans.c.user_id)).label("students")).group_by(
        utc_day(db, plans.c.created_at), plans.c.institution, plans.c.program, plans.c.degree
    ).subquery()
    small = (await db.execute(select(func.count()).select_from(cells).where(
        cells.c.students < MIN_CELL_SIZE
    ))).scalar_one()
    return small == 0


async def totals(db, plans):
    row = (await db.execute(select(func.count(), func.count(distinct(plans.c.user_id)))
                            .select_from(plans))).one()
    return int(row[0]), int(row[1])


async def breakdown(db, plans, field):
    col = plans.c[field]
    rows = (await db.execute(select(col, func.count(), func.count(distinct(plans.c.user_id)))
                            .group_by(col).order_by(func.count().desc(), col))).all()
    # Withhold the entire panel when a small cell exists: no residual 'Other' leaks.
    if any(row[2] < MIN_CELL_SIZE for row in rows):
        return []
    return [Breakdown(label=r[0], plans=r[1], students=r[2]) for r in rows]


async def build_dashboard(db: AsyncSession, user, filters: Filters, now=None) -> Dashboard:
    require_management(user)  # Defense in depth for direct service callers.
    now = now or datetime.now(timezone.utc)
    start, end = filters.bounds(now)
    if end > now:
        raise HTTPException(422, "Reporting range cannot include future days")
    source = plan_projection()
    current = period_query(source, filters, start, end)
    plan_count, student_count = await totals(db, current)
    suppressed = (0 < student_count < MIN_CELL_SIZE) or not await cohort_is_releasable(db, current)
    status = "suppressed" if suppressed else "available"
    metrics = []

    def metric(key, label, pillar, value, definition, provenance, **kwargs):
        metrics.append(Metric(id=key, label=label, pillar=pillar,
                              value=None if suppressed else value, status=status,
                              definition=definition, source=provenance, **kwargs))

    # Stock is intentionally scoped to eligible accounts, never to selected plan dimensions.
    u = User.__table__
    registered = int((await db.execute(select(func.count()).select_from(u).where(
        u.c.role == UserRole.CUSTOMER, u.c.is_active.is_(True), u.c.is_deactivated.is_(False)
    ))).scalar_one())
    metrics.append(Metric(id="students", label="Registered students", pillar="Engagement",
        value=registered if registered == 0 or registered >= MIN_CELL_SIZE else None,
        status="available" if registered == 0 or registered >= MIN_CELL_SIZE else "suppressed",
        definition="All-time active, non-deactivated customer accounts. Unaffected by plan/date filters; not monthly active users.", source="users.role, is_active, is_deactivated"))
    provenance = "education_plans + active ed_plans; linked copies counted once"
    metric("planning_students", "Students creating plans", "Engagement", student_count,
           "Distinct eligible student IDs with a plan created in the selected period and plan filters.", provenance)
    metric("plans", "Plans created", "Engagement", plan_count,
           "Stored plans created in this period; active normalized plans plus unlinked legacy plans. Not an intentional save milestone.", provenance)
    institution_count = int((await db.execute(select(func.count(distinct(current.c.institution))).where(
        current.c.institution != "not provided"
    ))).scalar_one())
    metric("institutions", "Universities selected", "Engagement", institution_count,
           "Distinct normalized institution names on plans in this cohort. Excludes unknown names; not partner institutions or enrollment.", provenance)
    ratio = round(plan_count / student_count, 2) if student_count else None
    metric("average", "Plans per planning student", "Engagement", ratio,
           "Plans created / distinct planning students in the same filtered period. No denominator means unavailable.", provenance, unit="ratio")
    if ratio is None:
        metrics[-1].status = "unavailable"
    unavailable = {
        "Monthly active students": "Not tracked: no reliable discovery, search, or repeat-visit event log.",
        "Saved plan milestone": "Not tracked: stored plans do not distinguish deliberate save actions.",
        "Plan completion / academic validity": "Not available: existing on-demand validators do not persist catalog-versioned, cohort-wide assessments.",
        "Advisor shares and review": "Not tracked: notification sending has no auditable delivery/review event table.",
        "Verified enrollment and outcomes": "Awaiting authorized partner integration; plans are not enrollment evidence.",
        "Regional participation": "Not reported: no approved, normalized student-location reporting source.",
        "Planning funnel": "Not tracked: historical discovery/start/validation/share events are unavailable.",
        "Activity feed": "No event history. Timestamps cannot reconstruct every edit or download.",
    }
    for key, label, pillar, reason in (
        ("quality", "Academically valid plans", "Progress", unavailable["Plan completion / academic validity"]),
        ("completion", "Plan completion rate", "Progress", unavailable["Plan completion / academic validity"]),
        ("shares", "Advisor shares", "Impact", unavailable["Advisor shares and review"]),
        ("enrollment", "Verified enrollment", "Impact", unavailable["Verified enrollment and outcomes"]),
    ):
        metrics.append(Metric(id=key, label=label, pillar=pillar, status="unavailable", definition=reason, source="No qualified measurement source"))

    programs = await breakdown(db, current, "program") if not suppressed else []
    institutions = await breakdown(db, current, "institution") if not suppressed else []
    degrees = await breakdown(db, current, "degree") if not suppressed else []
    # Daily counts, not event-history reconstruction. Never publish small day cohorts.
    day = utc_day(db, current.c.created_at)
    rows = (await db.execute(select(day, func.count(), func.count(distinct(current.c.user_id)))
                            .group_by(day).order_by(day))).all()
    trend = []
    if not suppressed and not any(r[2] < MIN_CELL_SIZE for r in rows):
        trend = [{"date": str(r[0]), "plans": r[1], "students": r[2]} for r in rows if r[0] is not None]
        if start:
            by_day = {r["date"]: r for r in trend}
            trend = [by_day.get((start.date() + timedelta(days=i)).isoformat(),
                      {"date": (start.date() + timedelta(days=i)).isoformat(), "plans": 0, "students": 0})
                     for i in range((end - start).days)]
    # A prior-period delta is released only for sufficiently sized comparable cohorts.
    if start and not suppressed:
        previous = period_query(source, filters, start - (end - start), start)
        previous_plans, previous_students = await totals(db, previous)
        if (previous_students >= MIN_CELL_SIZE and student_count >= MIN_CELL_SIZE
                and await cohort_is_releasable(db, previous)):
            metrics[1].delta = round((student_count - previous_students) / previous_students * 100, 1)
            metrics[2].delta = round((plan_count - previous_plans) / previous_plans * 100, 1)

    # Options derive only from safely released current cells, not student records.
    options = {"institution": [r.label for r in institutions], "program": [r.label for r in programs], "degree": [r.label for r in degrees]}
    attention = [{"title": "Plan quality is not yet measured", "evidence": "No persisted, versioned validation results", "action": "Arrange a catalog-versioned validation rollout with institutional data owners.", "owner": "Platform and institutional planning leads"},
                 {"title": "Outcome evidence is not connected", "evidence": "No approved institutional outcome feed", "action": "Establish an authorized cohort and integration before reporting enrollment or completion.", "owner": "Partnership and data governance leads"}]
    if suppressed:
        attention.insert(0, {"title": "Reporting cohort is too small", "evidence": "Aggregate values withheld under the disclosure policy", "action": "Use a broader reporting period or remove filters.", "owner": "Analytics administrator"})
    return Dashboard(population="EdPlan AI users — active student/customer accounts",
        refreshed_at=now, period_start=start, period_end_exclusive=end, filters=filters,
        coverage="Existing stored plans only. Not statewide enrollment or participating-institution coverage. Inactive normalized plans excluded; deletions can revise historical counts. Refresh is on request, not a real-time event feed.",
        privacy="Minimum distinct-student cell size: 5 (product policy, not a statutory rule). Counts are released only when every UTC day × institution × program × credential cell in the report meets the threshold, to protect against date/filter subtraction. Entire panels containing small cells are withheld. No regional/high-school filters or student drill-downs are exposed. Administrator access is limited to platform aggregates, not education records.",
        metrics=metrics, trend=trend, programs=programs, institutions=institutions, degrees=degrees,
        options=options, attention=attention[:5], unavailable=unavailable,
        decision_note=["What changed: " + ("Comparable prior-period counts are not available." if metrics[2].delta is None else f"Plan creation changed {metrics[2].delta:+g}% against the equal-length previous period."),
                       "Where attention is needed: quality assessments and verified outcomes remain unmeasured.",
                       "Recommended follow-up: review reporting coverage with data owners before adding new outcome measures."])
