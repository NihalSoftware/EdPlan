"""Offline tests of the exact public-browser index snapshot; never call the website."""

import copy
import json
import tempfile
from pathlib import Path

import pytest

from scripts.wnmu_catalog import FIXTURE, INDEX, approved_source, build_stage


def test_full_inventory_and_department_scope():
    stage = build_stage()
    assert len(stage["programs"]) == 234
    assert len(stage["departments"]) == 12
    assert len(stage["academic_units"]) == 14
    assert len({r["official_source_id"] for r in stage["programs"]}) == 234
    assert not any(d["official_name"] == "College of Education" for d in stage["departments"])
    assert not any(d["official_name"] == "Academic Affairs" for d in stage["departments"])
    assert build_stage() == stage


def test_official_names_and_relationships_not_merged():
    stage = build_stage()
    items = [p for p in stage["programs"] if p["official_name"] == "Sustainable Development, B.A."]
    assert len(items) == 4
    assert len({p["academic_unit_source_id"] for p in items}) == 4
    item = next(p for p in stage["programs"] if p["official_source_id"] == "catoid=8:poid=2752")
    assert item["official_name"] == "Graphic Design, A.A."
    assert item["academic_unit_source_id"] == "catoid=8:ent302"
    assert item["official_source_url"].endswith("poid=2752&returnto=612")


def test_unknowns_and_approval_are_never_invented():
    stage = build_stage()
    for p in stage["programs"]:
        assert p["total_credit_hours"] is None
        assert p["officially_active"] is None
        assert p["duration"] is None
    pending = [p for p in stage["programs"] if p["catalog_wording"] == "pending_approval"]
    assert len(pending) == 1
    assert "(Pending Approval)" in pending[0]["official_name"]
    assert stage["publication_complete"] is False


@pytest.mark.parametrize(
    "url",
    [
        "http://catalog.wnmu.edu/content.php?catoid=8&navoid=612",
        "https://catalog.wnmu.edu.evil.test/content.php?catoid=8&navoid=612",
        "https://user:pass@catalog.wnmu.edu/content.php?catoid=8&navoid=612",
        "https://catalog.wnmu.edu:8443/content.php?catoid=8&navoid=612",
        "https://catalog.wnmu.edu/content.php?catoid=9&navoid=612",
        INDEX + "&private=true",
        INDEX + "#unexpected",
        "https://catalog.wnmu.edu/preview_program.php?catoid=8&poid=2752&returnto=612&poid=99",
    ],
)
def test_unapproved_urls_rejected(url):
    with pytest.raises(ValueError):
        approved_source(url)


def test_duplicate_official_id_rejected():
    capture = json.loads(FIXTURE.read_text())
    capture["universityPrograms"] = copy.deepcopy([capture["units"][2][2][0][1][0]])
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "duplicate.json"
        path.write_text(json.dumps(capture))
        with pytest.raises(ValueError, match="Duplicate"):
            build_stage(path)


def test_snapshot_transfer_matches_observed_browser_projection():
    capture = json.loads(FIXTURE.read_text())
    projection = json.dumps(
        {k: capture[k] for k in ("catalog", "units", "universityPrograms")},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    value = 2166136261
    for char in projection:
        value = ((value ^ ord(char)) * 16777619) & 0xFFFFFFFF
    # Transfer check, not a cryptographic authenticity claim. Stage uses SHA-256 separately.
    assert len(projection) == 11979
    assert value == 0xCC257B03
