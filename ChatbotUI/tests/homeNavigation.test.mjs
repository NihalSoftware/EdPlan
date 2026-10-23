import assert from "node:assert/strict";
import test from "node:test";
import { homeActionUrl, loginDestination, NORTHERN_PLANNER_URL, plannerUniversity } from "../src/utils/homeNavigation.js";

test("guest comparison CTA retains the intended destination through login", () => {
  assert.equal(homeActionUrl(false, "/compare"), "/login?next=%2Fcompare");
  assert.equal(loginDestination("?next=%2Fcompare"), "/compare");
});

test("guest Northern planner CTA returns to the pre-chosen college", () => {
  const loginUrl = homeActionUrl(false, NORTHERN_PLANNER_URL);
  assert.equal(loginDestination(new URL(loginUrl, "https://edplan.invalid").search), NORTHERN_PLANNER_URL);
  assert.equal(plannerUniversity("?college=nnmc"), "Northern New Mexico College");
});

test("authenticated users go directly to the existing workflows", () => {
  assert.equal(homeActionUrl(true, "/compare"), "/compare");
  assert.equal(homeActionUrl(true, NORTHERN_PLANNER_URL), NORTHERN_PLANNER_URL);
});

test("default login and other planner entry points keep existing behavior", () => {
  assert.equal(loginDestination(""), "/eduai");
  assert.equal(plannerUniversity(""), "");
  assert.equal(plannerUniversity("?college=other"), "");
});

test("untrusted return URLs cannot introduce an open redirect", () => {
  for (const next of ["https://example.com", "//example.com", "javascript:alert(1)", "/login", "/compare/../admin"]) {
    assert.equal(loginDestination(`?next=${encodeURIComponent(next)}`), "/eduai");
  }
});

test("signup's existing shared login form retains the same destination query", () => {
  assert.equal(loginDestination("?next=%2Feducationplan%3Fcollege%3Dnnmc"), NORTHERN_PLANNER_URL);
});
