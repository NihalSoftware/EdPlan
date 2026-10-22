"""Lossless page-level PDF evidence; intentionally not a degree-rule inference engine."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path


def extract_pdf(path: Path, destination: Path) -> dict:
    from pypdf import PdfReader

    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    checksum = digest.hexdigest()
    manifest_path = destination / "pdf-manifest.json"
    pages_path = destination / "pdf-pages.jsonl"
    if manifest_path.exists() and pages_path.exists():
        old = json.loads(manifest_path.read_text(encoding="utf-8"))
        if old.get("sha256") == checksum:
            return old
    destination.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(path)
    printed_pages, declared_totals = [], []
    retrieved = datetime.now(UTC).isoformat()
    temporary = pages_path.with_suffix(".jsonl.tmp")
    with temporary.open("w", encoding="utf-8") as target:
        for index, page in enumerate(reader.pages):
            text = page.extract_text(extraction_mode="layout") or ""
            footer = re.findall(r"(?m)^\s*(\d+)\s*/\s*(\d+)\s*$", text)
            printed, total = (int(v) for v in footer[-1]) if footer else (None, None)
            printed_pages.append(printed)
            declared_totals.append(total)
            target.write(
                json.dumps(
                    {
                        "source_type": "supplied_pdf",
                        "source_name": path.name,
                        "sha256": checksum,
                        "retrieved_at": retrieved,
                        "pdf_page_index": index,
                        "pdf_page_number": index + 1,
                        "printed_page": printed,
                        "declared_catalog_pages": total,
                        "text": text,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    temporary.replace(pages_path)
    known = [p for p in printed_pages if p is not None]
    manifest = {
        "source_name": path.name,
        "sha256": checksum,
        "retrieved_at": retrieved,
        "pdf_pages": len(reader.pages),
        "first_printed_page": printed_pages[0],
        "last_printed_page": printed_pages[-1],
        "declared_catalog_pages": max((p for p in declared_totals if p), default=None),
        "pages_without_printed_number": sum(p is None for p in printed_pages),
        "complete_catalog": bool(
            known
            and known[0] == 1
            and len(known) == max(known)
            and max(known) == max(p for p in declared_totals if p)
        ),
        "warning": "Page references are read from each footer, not calculated with an offset.",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(extract_pdf(args.pdf, args.output), indent=2))


if __name__ == "__main__":
    main()
