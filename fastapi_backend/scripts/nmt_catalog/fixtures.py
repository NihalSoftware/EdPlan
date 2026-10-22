"""Save small, academically relevant official SSR fixtures from the existing local cache."""

from __future__ import annotations

import argparse
from pathlib import Path

from .baseline import save_json
from .normalize import raw_academics
from .pipeline import record_from_page
from .sources import ORIGIN, PublicCatalogClient


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    client = PublicCatalogClient(args.cache, offline=True)
    try:
        for kind, slug in (
            ("program", "BS-BIOLOGY"),
            ("program", "BS-BMS"),
            ("program", "MS-BIOLOGY"),
            ("course", "BIOL2110L"),
        ):
            html, source = client.fetch(f"{ORIGIN}/{kind}s/{slug}")
            record, _, _ = record_from_page(html, kind, "2026-2027")
            save_json(
                args.output / f"{slug}.json",
                {
                    "kind": kind,
                    "source": source,
                    "catalog_year": "2026-2027",
                    "record": raw_academics(record),
                },
            )
    finally:
        client.close()


if __name__ == "__main__":
    main()
