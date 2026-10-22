"""NMT source extraction and dry-run review. No production database mutations."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog-year", choices=["2026-2027"], required=True)
    parser.add_argument("--pdf", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument(
        "--max-courses",
        type=int,
        default=0,
        help="0 = all discovered candidates; a limit is reported as incomplete",
    )
    parser.add_argument("--max-programs", type=int, default=0)
    parser.add_argument("--database-baseline", action="store_true")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.apply:
        parser.error(
            "APPLY BLOCKED: reconcile missing migrations 0011-0014, verify a test database, "
            "resolve academic review and implement reviewed publication before any write. "
            "This command does not contain a production write path."
        )
    if args.max_courses < 0 or args.max_programs < 0:
        parser.error("Crawl limits cannot be negative")
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    output = args.output or Path("artifacts") / "nmt" / args.catalog_year
    output.mkdir(parents=True, exist_ok=True)
    logging.getLogger().addHandler(logging.FileHandler(output / "crawl.log", encoding="utf-8"))
    if args.pdf:
        from scripts.nmt_catalog.pdf_evidence import extract_pdf

        extract_pdf(args.pdf, output)
    from scripts.nmt_catalog.baseline import baseline, save_json

    if args.database_baseline:
        data = asyncio.run(baseline(Path(".env")))
        save_json(output / "database-baseline.json", data)
    from scripts.nmt_catalog.pipeline import build_stage

    stage, report = build_stage(
        output,
        args.catalog_year,
        offline=args.offline,
        max_courses=args.max_courses,
        max_programs=args.max_programs,
    )
    baseline_path = output / "database-baseline-after.json"
    if not baseline_path.exists():
        baseline_path = output / "database-baseline.json"
    if baseline_path.exists():
        from scripts.nmt_catalog.matching import dry_run_report

        data = json.loads(baseline_path.read_text(encoding="utf-8"))
        save_json(output / "dry-run-report.json", dry_run_report(stage, data))
    print(
        json.dumps(
            {
                k: report[k]
                for k in (
                    "programs_staged",
                    "courses_staged",
                    "departments_staged",
                    "source_conflict_count",
                    "sample_plans_staged_unverified",
                    "database_apply_executed",
                    "production_ready",
                )
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
