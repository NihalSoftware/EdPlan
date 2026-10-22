"""Explicit department insertion and academic REVIEW staging; never publishes courses/programs."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path

import asyncpg
from dotenv import dotenv_values
from sqlalchemy.engine import make_url

from scripts.nmt_catalog.baseline import save_json
from scripts.nmt_catalog.database_staging import apply_staging, validated_stage


async def run(args):
    stage, source = validated_stage(args.output, args.expected_stage_hash)
    config = {**dotenv_values(".env"), **os.environ}
    url = make_url(config["DATABASE_URL"])
    connection = await asyncpg.connect(
        url.set(drivername="postgresql").render_as_string(hide_password=False), timeout=15
    )
    try:
        report = await apply_staging(connection, stage, source, args.expected_university_id)
    finally:
        await connection.close()
    report_name = (
        "database-staging-repeat-report.json"
        if report["already_applied"]
        else "database-staging-apply-report.json"
    )
    save_json(args.output / report_name, report)
    print(json.dumps({k: v for k, v in report.items() if k != "summary"}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("artifacts/nmt/2026-2027"))
    parser.add_argument("--expected-stage-hash", required=True)
    parser.add_argument("--expected-university-id", required=True)
    parser.add_argument("--apply-departments-and-review-only", action="store_true", required=True)
    args = parser.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
