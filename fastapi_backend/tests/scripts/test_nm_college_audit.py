"""Offline regression checks; never connects to a database or official website."""

import ast
import csv
import inspect
import json
from collections import Counter
from pathlib import Path

from scripts.audit_nm_colleges import (
    collect,
    csv_write,
    normalized,
    public_metadata,
    reconcile,
    stored_source_url,
)
from scripts.nm_audit_analysis import code_key, cyclic_components, decimal_equal

REPORTS = Path(__file__).resolve().parents[3] / "reports/nm-college-audit"


def test_directory_has_exact_agreed_scope():
    directory = json.loads((REPORTS / "institution-directory.json").read_text(encoding="utf-8"))
    assert len(directory) == len({i["key"] for i in directory}) == 20
    assert Counter(i["category"] for i in directory) == {
        "public_four_year": 7,
        "independent_public": 9,
        "tribal": 4,
    }
    dine = next(i for i in directory if i["key"] == "dine")
    assert (dine["city"], dine["state"], dine["nm_service_location"]) == (
        "Tsaile",
        "Arizona",
        "Shiprock",
    )


def test_branch_cannot_satisfy_missing_parent():
    directory = [
        {"key": "dine", "name": "Diné College", "aliases": [], "domains": ["dinecollege.edu"]}
    ]
    db = [
        {
            "university_id": "center",
            "university_name": "Diné College - Shiprock",
            "website": "https://www.dinecollege.edu/",
        }
    ]
    items, extras = reconcile(directory, db)
    assert items[0]["institution_status"] == "MISSING_IN_DB"
    assert items[0]["parents"] == []
    assert len(items[0]["related"]) == 1
    assert extras == []


def test_duplicates_are_not_merged_and_sipi_alias_is_not_correct_spelling():
    directory = [
        {
            "key": "unm",
            "name": "University of New Mexico",
            "aliases": ["University of New Mexico-Main Campus"],
            "domains": ["unm.edu"],
        },
        {
            "key": "sipi",
            "name": "Southwestern Indian Polytechnic Institute",
            "aliases": ["Southwest Indian Polytechnic Institute"],
            "domains": ["sipi.edu"],
        },
    ]
    db = [
        {
            "university_id": "a",
            "university_name": "University of New Mexico",
            "website": "https://unm.edu",
        },
        {
            "university_id": "b",
            "university_name": "University of New Mexico-Main Campus",
            "website": "https://unm.edu",
        },
        {
            "university_id": "c",
            "university_name": "Southwest Indian Polytechnic Institute",
            "website": "https://sipi.edu",
        },
    ]
    rows, _ = reconcile(directory, db)
    assert rows[0]["institution_status"] == "POSSIBLE_DUPLICATE"
    assert [p["university_id"] for p in rows[0]["parents"]] == ["a", "b"]
    assert rows[1]["institution_status"] == "MISMATCH"


def test_normalization_preserves_evidence_but_compares_accents_whitespace():
    assert normalized("Diné College") == normalized("Dine College")
    assert code_key("ACCT 2110x") == "ACCT2110X"
    assert code_key("BIOL 1110/L") != code_key("BIOL 1110L")


def test_missing_is_not_zero_and_decimal_display_is_equal():
    assert decimal_equal("3.00", 3)
    assert decimal_equal("0.50", ".5")
    assert not decimal_equal(None, 0)
    assert not decimal_equal("3-6", 3)
    assert not decimal_equal(2, 3)


def test_cycles_are_components_not_automatic_errors():
    assert cyclic_components([("a", "b"), ("b", "a"), ("b", "c")]) == [["a", "b"]]
    assert cyclic_components([("a", "b"), ("b", "c")]) == []
    assert cyclic_components([("a", "a")]) == []  # self edges reported separately
    assert cyclic_components([(str(i), str(i + 1)) for i in range(2000)]) == []


def test_metadata_whitelist_excludes_arbitrary_fields():
    result = public_metadata(
        {"catalog_year": "2026-2027", "student_name": "not exportable", "prerequisite": "A OR B"}
    )
    assert "student_name" not in {k for k in result if k != "_original_metadata_keys"}
    assert result["prerequisite"] == "A OR B"
    assert public_metadata(None) == {}


def test_csv_formula_protection_and_unknown_blank(tmp_path):
    target = tmp_path / "findings.csv"
    csv_write(target, ["name", "credits"], [{"name": "=FORMULA()", "credits": None}])
    with target.open(encoding="utf-8-sig", newline="") as stream:
        assert list(csv.DictReader(stream)) == [{"name": "'=FORMULA()", "credits": ""}]


def test_json_provenance_is_not_mistaken_for_absent_source():
    assert stored_source_url(
        {"metadata_json": {"catalog_url": "https://catalog.example.edu/program"}}
    )
    assert not stored_source_url({"metadata_json": {"catalog_source": "filename.pdf"}})


def test_observed_graduation_audit_counts_planned_as_completed():
    """Reproduce the reported limitation, not a claim that this policy is correct."""
    from types import SimpleNamespace

    from app.student.domains.planning.services.graduation_audit_service import _build_audit

    course = SimpleNamespace(course_id="course", credits=3)
    program = SimpleNamespace(
        program_id="program", program_name="Synthetic", degree="Certificate", total_credit_hours=3
    )
    plan = SimpleNamespace(
        plan_id="plan",
        program=program,
        courses=[SimpleNamespace(course_id="course", course=course, status="planned")],
    )
    result = _build_audit(plan, [course])
    assert result["graduation_ready"] is True
    assert result["courses"]["completed"] == 1


def test_collector_requires_readonly_and_has_no_dml_literals():
    source = inspect.getsource(collect)
    assert 'transaction(readonly=True, isolation="repeatable_read")' in source
    assert '"default_transaction_read_only": "on"' in source
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            first = node.value.strip().split(" ", 1)[0].upper()
            assert first not in {
                "INSERT",
                "UPDATE",
                "DELETE",
                "DROP",
                "ALTER",
                "TRUNCATE",
                "CREATE",
            }


def test_report_outputs_have_20_rows_when_generated():
    path = REPORTS / "institutions.csv"
    if not path.exists():
        return
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == len({r["key"] for r in rows}) == 20
    assert next(r for r in rows if r["key"] == "dine")["institution_status"] == "MISSING_IN_DB"
    assert next(r for r in rows if r["key"] == "sipi")["institution_status"] == "MISMATCH"
