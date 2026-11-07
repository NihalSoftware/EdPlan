import csv
import io
from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.analytics import Dashboard, Filters, build_dashboard, require_management
from app.db.session import get_db
from app.security.auth import get_current_user

router = APIRouter(prefix="/admin/analytics", tags=["management analytics"])


def parse_filters(period: Literal["7", "30", "90", "custom", "all"] = "30",
                  start: date | None = None, end: date | None = None,
                  institution: str | None = Query(None, max_length=256),
                  program: str | None = Query(None, max_length=256),
                  degree: str | None = Query(None, max_length=128)) -> Filters:
    try:
        return Filters(period=period, start=start, end=end, institution=institution,
                       program=program, degree=degree)
    except ValidationError:
        raise HTTPException(422, "Invalid reporting range: provide ordered custom dates within 366 days") from None


async def administrator(user=Depends(get_current_user)):
    require_management(user)
    return user


@router.get("/access")
async def access(response: Response, user=Depends(administrator)):
    response.headers["Cache-Control"] = "no-store"
    return {"authorized": True, "scope": "aggregate platform analytics only"}


@router.get("/summary", response_model=Dashboard)
async def summary(response: Response, filters: Filters = Depends(parse_filters),
                  user=Depends(administrator), db: AsyncSession = Depends(get_db)):
    response.headers["Cache-Control"] = "no-store"
    return await build_dashboard(db, user, filters)


def csv_safe(value):
    value = str(value) if value is not None else ""
    # Catalog labels can be legacy free text; prevent spreadsheet formula execution.
    return "'" + value if value.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")) else value


@router.get("/export")
async def export(filters: Filters = Depends(parse_filters), user=Depends(administrator),
                 db: AsyncSession = Depends(get_db)):
    data = await build_dashboard(db, user, filters)
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(["Reporting population", data.population])
    writer.writerow(["UTC period start", data.period_start or "All time"])
    writer.writerow(["UTC period end (exclusive)", data.period_end_exclusive])
    writer.writerow(["Refreshed at", data.refreshed_at])
    writer.writerow(["Plan filters", csv_safe(filters.model_dump_json())])
    writer.writerow(["Coverage", data.coverage])
    writer.writerow(["Privacy", data.privacy])
    writer.writerow(["Pillar", "Metric", "Value", "Status", "Definition", "Source"])
    for metric in data.metrics:
        writer.writerow([csv_safe(v) for v in (metric.pillar, metric.label, metric.value,
                         metric.status, metric.definition, metric.source)])
    writer.writerow([])
    writer.writerow(["Dimension", "Group", "Plans", "Distinct students"])
    for dimension in ("programs", "institutions", "degrees"):
        for row in getattr(data, dimension):
            writer.writerow([dimension, csv_safe(row.label), row.plans, row.students])
    writer.writerow([])
    writer.writerow(["UTC date", "Plans created", "Distinct students creating plans"])
    for row in data.trend:
        writer.writerow([row["date"], row["plans"], row["students"]])
    return Response(stream.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="edplan-aggregate-report.csv"',
                             "Cache-Control": "no-store"})
