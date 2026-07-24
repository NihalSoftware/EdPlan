import asyncio

from app.student.domains.discovery.clients.college_scorecard import (
    BASE_FIELDS,
    CollegeScorecardClient,
)


def test_scorecard_fields_include_shared_detail_and_compare_metrics():
    assert {
        "school.accreditor",
        "school.open_admissions_policy",
        "school.degrees_awarded.predominant",
        "school.degrees_awarded.highest",
        "latest.cost.tuition.in_state",
        "latest.cost.tuition.out_of_state",
        "latest.cost.roomboard.oncampus",
        "latest.cost.booksupply",
    }.issubset(BASE_FIELDS)


def test_map_school_exposes_shared_detail_and_compare_metrics():
    school = CollegeScorecardClient()._map_school(
        {
            "id": 188058,
            "school.name": "Northern New Mexico College",
            "school.open_admissions_policy": 1,
            "school.accreditor": "Higher Learning Commission",
            "school.degrees_awarded.predominant": 3,
            "school.degrees_awarded.highest": 4,
            "school.main_campus": 1,
            "school.branches": 1,
            "latest.cost.tuition.in_state": 5252,
            "latest.cost.tuition.out_of_state": 14902,
            "latest.cost.roomboard.oncampus": 7900,
            "latest.cost.booksupply": 1200,
        }
    )

    assert school["open_admissions_policy"] is True
    assert school["accreditor"] == "Higher Learning Commission"
    assert school["predominant_degree"] == "Predominantly bachelor's degree"
    assert school["highest_degree"] == "Graduate degree"
    assert school["main_campus"] is True
    assert school["branch_count"] == 1
    assert school["in_state_tuition"] == 5252
    assert school["out_of_state_tuition"] == 14902
    assert school["on_campus_room_and_board"] == 7900
    assert school["books_and_supplies"] == 1200

    selective_school = CollegeScorecardClient()._map_school(
        {
            "id": 188058,
            "school.name": "Northern New Mexico College",
            "school.open_admissions_policy": 2,
        }
    )
    assert selective_school["open_admissions_policy"] is False


def test_find_schools_by_profiles_uses_state_batch():
    client = CollegeScorecardClient()
    northern = client._map_school(
        {
            "id": 188058,
            "school.name": "Northern New Mexico College",
            "school.city": "Espanola",
            "school.state": "NM",
            "latest.student.size": 926,
        }
    )

    async def search_schools(**kwargs):
        assert kwargs == {"state": "NM", "per_page": 100}
        return {"results": [northern], "metadata": {"total": 1}}

    async def unexpected_individual_lookup(**kwargs):
        raise AssertionError("individual lookup should not be needed")

    client.search_schools = search_schools
    client.find_school_by_profile = unexpected_individual_lookup

    matches = asyncio.run(
        client.find_schools_by_profiles(
            [
                {
                    "name": "Northern New Mexico College",
                    "city": "Espanola",
                    "state": "New Mexico",
                }
            ]
        )
    )

    assert matches == [northern]
