"""Offline verification of a staged catalog, without any database connection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.nmt_catalog.baseline import save_json
from scripts.nmt_catalog.normalize import canonical_hash
from scripts.nmt_catalog.pipeline import validation_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog-year", choices=["2026-2027"], required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path("artifacts") / "nmt" / args.catalog_year
    stage = json.loads((output / "staged-catalog.json").read_text(encoding="utf-8"))
    expected = stage.pop("stage_hash")
    if canonical_hash(stage) != expected or stage["catalog_year"] != args.catalog_year:
        raise ValueError("Stage checksum or catalog year mismatch")
    stage["stage_hash"] = expected
    for kind in ("programs", "courses"):
        identities = [(r["institution"], r["catalog_year"], r["external_id"]) for r in stage[kind]]
        if len(identities) != len(set(identities)):
            raise ValueError("Duplicate institution/catalog scoped identity")
        if any(
            r["institution"] != "NMT" or r["catalog_year"] != args.catalog_year for r in stage[kind]
        ):
            raise ValueError("Cross-institution/catalog contamination")
    report = validation_report(stage)
    save_json(output / "validation-report.json", report)
    print(
        json.dumps(
            {
                "stage_integrity": "passed",
                "production_ready": False,
                "blocking_issues": report["blocking_issues"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
