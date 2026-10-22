from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx

from scripts.nmt_catalog.evaluate import evaluate
from scripts.nmt_catalog.matching import match_record, merge_nonempty
from scripts.nmt_catalog.normalize import (
    canonical_hash,
    credit_range,
    internal_conflicts,
    normalize,
    requirement_tree,
    rule_node,
    walk,
)
from scripts.nmt_catalog.pipeline import program_link
from scripts.nmt_catalog.sources import (
    ORIGIN,
    PageParser,
    PublicCatalogClient,
    approved_url,
    decode_nuxt,
)

FIXTURES = Path(__file__).parent / "fixtures" / "nmt"


def fixture(code):
    return json.loads((FIXTURES / f"{code}.json").read_text(encoding="utf-8"))


class SourceSafetyTests(unittest.TestCase):
    def test_allowlist_blocks_private_external_credentials_query_and_protocol(self):
        for url in (
            "http://catalog.nmt.edu/courses/X",
            "https://evil.test/x",
            "https://catalog.nmt.edu.evil.test/x",
            "https://user:pass@catalog.nmt.edu/x",
            "https://catalog.nmt.edu:444/x",
            "https://catalog.nmt.edu/x?token=secret",
            "file:///etc/passwd",
            "http://127.0.0.1/",
        ):
            with self.assertRaises(ValueError):
                approved_url(url)
        self.assertEqual(approved_url("/courses/BIOL2110L#x"), ORIGIN + "/courses/BIOL2110L")

    def test_ssr_parser_only_reads_data_and_real_links(self):
        page = PageParser(
            '<script>danger()</script><script id="__NUXT_DATA__">[{"x":1},"yes"]'
            '</script><a href="/programs/opaque">program</a>'
        )
        self.assertEqual(decode_nuxt(page.nuxt), {"x": "yes"})
        self.assertNotIn("danger", "".join(page.text))
        self.assertEqual(page.links[0]["href"], "/programs/opaque")

    def test_devalue_nested_refs_wrappers_and_false_zero(self):
        raw = json.dumps(
            [{"obj": 1, "flag": 4, "zero": 5}, ["Reactive", 2], {"value": 3}, "A", False, 0]
        )
        self.assertEqual(decode_nuxt(raw), {"obj": {"value": "A"}, "flag": False, "zero": 0})

    def test_tabs_are_not_duplicate_programs(self):
        self.assertTrue(program_link("/programs/BS-BIOLOGY"))
        self.assertTrue(program_link("/programs/opaque"))
        self.assertFalse(program_link("/programs/BS-BIOLOGY/learning-outcomes-abc"))

    @patch("scripts.nmt_catalog.sources.time.sleep")
    def test_robots_cache_offline_and_descriptive_agent(self, _sleep):
        calls = []

        def response(request):
            calls.append(request)
            if request.url.path == "/robots.txt":
                return httpx.Response(200, text="User-agent: *\nAllow: /\n")
            return httpx.Response(200, text="<html>official</html>")

        with tempfile.TemporaryDirectory() as folder:
            client = httpx.Client(
                transport=httpx.MockTransport(response),
                headers={"User-Agent": "EdPlan-NMT-Catalog-Importer/1.0"},
            )
            reader = PublicCatalogClient(Path(folder), client=client)
            first = reader.fetch(ORIGIN + "/courses/BIOL2110L")
            self.assertEqual(reader.fetch(ORIGIN + "/courses/BIOL2110L"), first)
            self.assertEqual(len(calls), 2)
            self.assertIn("EdPlan", calls[0].headers["User-Agent"])
            reader.close()
            offline = PublicCatalogClient(Path(folder), offline=True)
            self.assertEqual(offline.fetch(ORIGIN + "/courses/BIOL2110L"), first)
            with self.assertRaises(FileNotFoundError):
                offline.fetch(ORIGIN + "/courses/NOT-CACHED")
            offline.close()

    @patch("scripts.nmt_catalog.sources.time.sleep")
    def test_robots_disallow_and_external_redirect_never_followed(self, _sleep):
        for disallow in (True, False):
            calls = []

            def response(request, calls=calls, disallow=disallow):
                calls.append(str(request.url))
                if request.url.path == "/robots.txt":
                    return httpx.Response(
                        200,
                        text="User-agent: *\n" + ("Disallow: /\n" if disallow else "Allow: /\n"),
                    )
                return httpx.Response(302, headers={"Location": "https://evil.test/x"})

            with tempfile.TemporaryDirectory() as folder:
                reader = PublicCatalogClient(
                    Path(folder), client=httpx.Client(transport=httpx.MockTransport(response))
                )
                with self.assertRaises((PermissionError, ValueError)):
                    reader.fetch(ORIGIN + "/courses/X")
                self.assertFalse(any("evil.test" in url for url in calls))
                self.assertEqual(len(calls), 1 if disallow else 2)
                reader.close()

    @patch("scripts.nmt_catalog.sources.time.sleep")
    def test_retries_transient_failure_but_not_access_control(self, _sleep):
        for status, expected in ((503, 3), (403, 1), (405, 1), (429, 1)):
            calls = []

            def response(request, calls=calls, status=status):
                if request.url.path == "/robots.txt":
                    return httpx.Response(200, text="User-agent: *\nAllow: /\n")
                calls.append(1)
                return httpx.Response(status)

            with tempfile.TemporaryDirectory() as folder:
                reader = PublicCatalogClient(
                    Path(folder), client=httpx.Client(transport=httpx.MockTransport(response))
                )
                with self.assertRaises((httpx.HTTPStatusError, PermissionError)):
                    reader.fetch(ORIGIN + "/courses/X")
                self.assertEqual(len(calls), expected)
                if status != 503:
                    with self.assertRaises(PermissionError):
                        reader.fetch(ORIGIN + "/courses/OTHER")
                    self.assertEqual(len(calls), expected)
                reader.close()


class NormalizationTests(unittest.TestCase):
    def test_missing_credits_remain_unknown_and_fractional_credits_preserved(self):
        self.assertIsNone(credit_range({})["min"])
        self.assertEqual(credit_range({"min": 0.5, "max": 6})["min"], "0.5")
        self.assertEqual(credit_range({"min": 0})["min"], "0")
        self.assertIsNone(credit_range({"min": False})["min"])

    def test_unknown_fields_do_not_overwrite_valid_values(self):
        old = {"description": "Valid", "credits": 3, "metadata": {"source": "old"}}
        self.assertEqual(
            merge_nonempty(old, {"description": None, "credits": "", "metadata": {}}), old
        )
        self.assertEqual(
            merge_nonempty(old, {"metadata": {"source": None, "new": 1}})["metadata"],
            {"source": "old", "new": 1},
        )

    def test_placeholders_not_importable(self):
        for title in ("undefined", "Untitled Course Set", "", "course"):
            with self.assertRaises(ValueError):
                normalize(
                    "course", {"id": "A", "code": "BIOL2110L", "name": title}, {}, "2026-2027"
                )

    def test_course_sets_and_permission_stay_review(self):
        self.assertEqual(
            rule_node(
                {
                    "condition": "completedAllOf",
                    "value": {
                        "condition": "courseSets",
                        "values": [{"value": ["opaque"], "logic": "and"}],
                    },
                }
            )["op"],
            "REVIEW",
        )
        self.assertIsNone(
            evaluate(
                rule_node({"condition": "freeformText", "value": "Permission of instructor"}), set()
            )
        )

    def test_unknown_grade_restrictions_are_not_silently_dropped(self):
        node = rule_node(
            {
                "condition": "completedAllOf",
                "minimumGrade": "C",
                "value": {
                    "condition": "courses",
                    "values": [{"value": ["BIOL2110"], "logic": "and"}],
                },
            }
        )
        self.assertEqual(node["op"], "REVIEW")

    def test_or_is_not_flattened_into_mandatory_courses(self):
        raw = {
            "condition": "completedAllOf",
            "value": {
                "condition": "courses",
                "values": [
                    {"value": ["BIOL2110L", "BIOL2141"], "logic": "or"},
                    {"value": ["BIOL2610", "BIOL2610L"], "logic": "and"},
                ],
            },
        }
        node = rule_node(raw)
        self.assertTrue(evaluate(node, {"BIOL2141", "BIOL2610", "BIOL2610L"}))
        self.assertFalse(evaluate(node, {"BIOL2110L", "BIOL2610"}))

    def test_credit_pool_does_not_require_all_choices_or_double_count(self):
        raw = {
            "condition": "minimumCredits",
            "credits": 3,
            "value": {
                "condition": "courses",
                "values": [{"value": ["BIOL2110", "BIOL2110L"], "logic": "and"}],
            },
        }
        node = rule_node(raw)
        self.assertTrue(evaluate(node, {"BIOL2110"}, credit_values={"BIOL2110": 3}))
        self.assertIsNone(evaluate(node, {"BIOL2110"}, credit_values={"BIOL2110": None}))

    def test_conservative_identity_matching_and_institution_isolation(self):
        source = {
            "institution": "NMT",
            "catalog_year": "2026-2027",
            "code": "BIOL2110L",
            "external_id": "official",
            "title": "Lab",
            "source": {"url": ORIGIN + "/courses/BIOL2110L"},
        }
        nnmc = {**source, "institution": "NNMC", "record_id": "other"}
        self.assertEqual(match_record(source, [nnmc])["action"], "proposed_insertion")
        row = {**source, "record_id": "one"}
        self.assertEqual(match_record(source, [row])["confidence"], "high")
        self.assertEqual(match_record(source, [row, row])["action"], "review")
        self.assertEqual(match_record(source, [{**row, "catalog_year": None}])["action"], "review")

    def test_hash_is_order_independent(self):
        self.assertEqual(canonical_hash({"a": 1, "b": 2}), canonical_hash({"b": 2, "a": 1}))

    def test_apply_refuses_before_any_connection(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.import_nmt_catalog",
                "--catalog-year",
                "2026-2027",
                "--apply",
            ],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("APPLY BLOCKED", result.stderr)


class OfficialFixtureTests(unittest.TestCase):
    def test_biology_minimum_120_and_credit_conflict_retained(self):
        f = fixture("BS-BIOLOGY")
        row = normalize(f["kind"], f["record"], f["source"], f["catalog_year"])
        self.assertEqual(row["minimum_credits"], "120")
        self.assertTrue(internal_conflicts(f["record"]))
        self.assertEqual(row["publication_status"], "staged_only")
        self.assertEqual(len(row["sample_plans"][0]["semesters"]), 8)
        self.assertEqual(row["sample_plans"][0]["semesters"][0]["semester"], "Fall")
        self.assertEqual(row["sample_plans"][0]["semesters"][0]["year"], "Year 1")

    def test_biology_core_preserves_or_labs(self):
        tree = requirement_tree(fixture("BS-BIOLOGY")["record"])
        options = [n for n in walk(tree) if isinstance(n, dict) and n.get("op") == "ANY"]
        self.assertTrue(
            any({c["code"] for c in n["children"]} == {"BIOL2110L", "BIOL2141"} for n in options)
        )

    def test_biol2110l_concurrent_not_earlier_only(self):
        tree = requirement_tree(fixture("BIOL2110L")["record"])
        self.assertTrue(evaluate(tree, set(), {"BIOL2110"}))
        self.assertFalse(evaluate(tree, {"BIOL2110"}, set()))

    def test_biol2610l_pre_or_core_and_core_are_distinct(self):
        # Synthetic semantics test, NOT a verified BIOL2610L live catalog fixture.
        # Its official page returned 405; publication must remain blocked.
        record = {
            "requisites": {
                "requisitesSimple": [
                    {
                        "name": "Pre or Corequisite Requirements",
                        "type": "Completion Requirement",
                        "rules": [
                            {
                                "condition": "completedAllOf",
                                "value": {
                                    "condition": "courses",
                                    "values": [{"value": ["BIOL2110L"], "logic": "and"}],
                                },
                            }
                        ],
                    },
                    {
                        "name": "Corequisite",
                        "type": "Corequisite",
                        "rules": [
                            {
                                "condition": "enrolledIn",
                                "value": {
                                    "condition": "courses",
                                    "values": [{"value": ["BIOL2610"], "logic": "and"}],
                                },
                            }
                        ],
                    },
                ]
            }
        }
        tree = requirement_tree(record)
        timings = {g.get("timing") for g in tree["children"]}
        self.assertIn("before_or_concurrent", timings)
        self.assertIn("concurrent", timings)
        self.assertTrue(evaluate(tree, {"BIOL2110L"}, {"BIOL2610"}))
        self.assertTrue(evaluate(tree, set(), {"BIOL2110L", "BIOL2610"}))
        self.assertFalse(evaluate(tree, {"BIOL2110L", "BIOL2610"}, set()))

    def test_biomedical_specializations_not_new_standalone_degrees(self):
        f = fixture("BS-BMS")
        row = normalize("program", f["record"], f["source"], "2026-2027")
        self.assertEqual(row["degree_designation"], "Bachelor of Science")
        self.assertTrue(row["specializations"] or row["requirement_tree"]["children"])
        self.assertTrue(row["raw_academic_record"].get("requisites"))

    def test_ms_biology_keeps_options_and_does_not_invent_credit_minimum(self):
        f = fixture("MS-BIOLOGY")
        row = normalize("program", f["record"], f["source"], "2026-2027")
        self.assertEqual(row["degree_designation"], "Master of Science")
        self.assertIn("Thesis", json.dumps(row["raw_academic_record"]))
        self.assertIsNone(row["minimum_credits"])


if __name__ == "__main__":
    unittest.main()
