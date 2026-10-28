export const NORTHERN_PLANNER_URL = "/educationplan?college=nnmc";

// Explicit internal destinations only: never trust an arbitrary return URL.
const HOME_DESTINATIONS = new Set(["/compare", "/uni", NORTHERN_PLANNER_URL]);

export const homeActionUrl = (authenticated, destination) =>
  authenticated ? destination : `/login?next=${encodeURIComponent(destination)}`;

export const loginDestination = (search) => {
  const requested = new URLSearchParams(search).get("next");
  return HOME_DESTINATIONS.has(requested) ? requested : "/eduai";
};

export const plannerUniversity = (search) =>
  new URLSearchParams(search).get("college") === "nnmc" ? "Northern New Mexico College" : "";
