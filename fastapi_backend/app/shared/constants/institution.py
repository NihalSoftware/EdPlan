"""Canonical institution identity for the NNMC-dedicated application."""

NORTHERN_NEW_MEXICO_COLLEGE_NAME = "Northern New Mexico College"
NORTHERN_NEW_MEXICO_COLLEGE_SCORECARD_ID = "188058"
NORTHERN_NEW_MEXICO_COLLEGE_CITY = "Española"
NORTHERN_NEW_MEXICO_COLLEGE_STATE = "New Mexico"
NORTHERN_NEW_MEXICO_COLLEGE_STATE_CODE = "NM"


def is_northern_new_mexico_college(value: str | None) -> bool:
    return (value or "").strip().casefold() == NORTHERN_NEW_MEXICO_COLLEGE_NAME.casefold()


def state_filter_aliases(value: str | None) -> tuple[str, ...]:
    cleaned = (value or "").strip()
    if cleaned.casefold() in {"nm", "new mexico"}:
        return (
            NORTHERN_NEW_MEXICO_COLLEGE_STATE,
            NORTHERN_NEW_MEXICO_COLLEGE_STATE_CODE,
        )
    return (cleaned,) if cleaned else ()
