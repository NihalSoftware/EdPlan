"""Three-valued checks for the supported subset; never silently pass unknown rules.

This is an importer QA helper, NOT wired into the existing academic planner.
Grades, permission, unresolved sets and free text return None (manual review).
"""

from __future__ import annotations

from decimal import Decimal


def _all(values):
    values = list(values)
    if any(v is False for v in values):
        return False
    return None if not values or any(v is None for v in values) else True


def _any(values):
    values = list(values)
    if any(v is True for v in values):
        return True
    return None if not values or any(v is None for v in values) else False


def evaluate(node, completed, concurrent=(), credit_values=None, timing="before"):
    completed, concurrent = set(completed), set(concurrent)
    op = node.get("op")
    if op == "COURSE":
        eligible = (
            completed | concurrent
            if timing == "before_or_concurrent"
            else concurrent
            if timing == "concurrent"
            else completed
        )
        return node["code"] in eligible
    if op in {"ALL", "ANY", "GROUP", "CATALOG_RULES", "ENROLLED"}:
        next_timing = node.get("timing") or timing
        values = (
            evaluate(c, completed, concurrent, credit_values, next_timing)
            for c in node.get("children", [])
        )
        return _any(values) if op == "ANY" else _all(values)
    if op == "AT_LEAST":
        values = [
            evaluate(c, completed, concurrent, credit_values, timing) for c in node["children"]
        ]
        yes, unknown = values.count(True), values.count(None)
        if yes >= node["count"]:
            return True
        return None if yes + unknown >= node["count"] else False
    if op == "MIN_CREDITS":
        if credit_values is None:
            return None
        # Unknown credits must not become zero. Count each eligible completed course once.
        codes = {c["code"] for g in node["eligible_groups"] for c in g["children"]}
        earned = codes & completed
        if any(credit_values.get(c) is None for c in earned):
            return None
        return sum((Decimal(str(credit_values[c])) for c in earned), Decimal(0)) >= Decimal(
            node["credits"]
        )
    return None
