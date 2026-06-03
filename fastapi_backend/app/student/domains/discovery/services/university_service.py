from app.student.domains.discovery.repositories import college_scorecard_repository


async def search_universities(
    *,
    search: str | None = None,
    state: str | None = None,
    page: int = 0,
    per_page: int = 10,
) -> dict:
    return await college_scorecard_repository.search_schools(
        search=search,
        state=state,
        page=page,
        per_page=per_page,
    )


async def get_university(unit_id: str) -> dict | None:
    return await college_scorecard_repository.get_school(unit_id)


async def compare_universities(unit_ids: list[int]) -> list[dict]:
    return await college_scorecard_repository.compare_schools(unit_ids[:5])
