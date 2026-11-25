import asyncio

import pytest

from app.orchestrator.llm import LLMHealthCheck, LLMRequest, LLMResponse
from app.orchestrator.llm.base_provider import BaseLLMProvider
from app.orchestrator.llm.prompt_registry import PromptRegistry
from app.orchestrator.modules.module_registry import ModuleRegistry
from app.orchestrator.router.module_selector import COLLEGE_COMPARISON, ModuleSelector
from app.orchestrator.schemas.intent_result import IntentResult
from app.orchestrator.schemas.student_context import StudentContext
from app.student.api.router import get_student_router
from app.student.domains.comparison import module
from app.student.domains.comparison.module import CollegeComparisonModule
from app.student.domains.comparison.registry import MODULE_REGISTRY_NAME, register_module
from app.student.domains.comparison.schemas.comparison import (
    CareerPathCompareRequest,
    ProgramCompareRequest,
    ProgramSearchRequest,
    UniversityCompareRequest,
    UniversitySearchRequest,
)
from app.student.domains.comparison.services.comparison_service import ComparisonService
from app.student.domains.comparison.tools import (
    COMPARISON_TOOLS,
    CompareCareerPathsTool,
    CompareProgramsTool,
    CompareUniversitiesTool,
    SearchProgramsTool,
    SearchUniversitiesTool,
)

EXPECTED_TOOL_NAMES = [
    "search_universities",
    "compare_universities",
    "search_programs",
    "compare_programs",
    "compare_career_paths",
]

UNIVERSITY_A = "11111111-1111-1111-1111-111111111111"
UNIVERSITY_B = "22222222-2222-2222-2222-222222222222"
PROGRAM_A = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
PROGRAM_B = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"


class _Repository:
    def __init__(self):
        self.calls = []

    async def search_universities(self, db, **filters):
        self.calls.append(("search_universities", db, filters))
        alpha = {
            "university_id": UNIVERSITY_A,
            "university_name": "Alpha University",
            "city": "Albuquerque",
            "state": "NM",
            "website": "https://alpha.example.edu",
            "available_programs": [{"program_id": PROGRAM_A, "program_name": "Computer Science"}],
            "program_count": 1,
            "public_private": None,
        }
        beta = {
            "university_id": UNIVERSITY_B,
            "university_name": "Beta University",
            "city": "Santa Fe",
            "state": "NM",
            "website": "https://beta.example.edu",
            "available_programs": [{"program_id": PROGRAM_B, "program_name": "Computer Science"}],
            "program_count": 1,
            "public_private": None,
        }
        name = (filters.get("name") or "").lower()
        if "beta" in name:
            return [beta]
        if "alpha" in name:
            return [alpha]
        return [alpha, beta]

    async def get_universities_by_ids(self, db, university_ids):
        self.calls.append(("get_universities_by_ids", db, university_ids))
        universities = {
            UNIVERSITY_A: {
                "university_id": UNIVERSITY_A,
                "university_name": "Alpha University",
                "program_count": 1,
                "city": "Albuquerque",
                "state": "NM",
            },
            UNIVERSITY_B: {
                "university_id": UNIVERSITY_B,
                "university_name": "Beta University",
                "program_count": 2,
                "city": "Santa Fe",
                "state": "NM",
            },
        }
        return [universities[item] for item in university_ids if item in universities]

    async def search_programs(self, db, **filters):
        self.calls.append(("search_programs", db, filters))
        university_id = filters.get("university_id")
        if university_id == UNIVERSITY_B:
            return [{"program_id": PROGRAM_B, "program_name": "Computer Science", "degree": "BS"}]
        return [{"program_id": PROGRAM_A, "program_name": "Computer Science", "degree": "BS"}]

    async def get_programs_by_ids(self, db, program_ids):
        self.calls.append(("get_programs_by_ids", db, program_ids))
        programs = {
            PROGRAM_A: {
                "program_id": PROGRAM_A,
                "program_name": "Computer Science",
                "degree": "BS",
                "total_credit_hours": 120,
                "required_courses": [{"course_code": "CS101", "credits": 3}],
                "course_count": 1,
                "duration": None,
                "description": None,
                "university": {
                    "university_id": UNIVERSITY_A,
                    "university_name": "Alpha University",
                    "city": "Albuquerque",
                    "state": "NM",
                },
            },
            PROGRAM_B: {
                "program_id": PROGRAM_B,
                "program_name": "Computer Science",
                "degree": "BS",
                "total_credit_hours": 124,
                "required_courses": [{"course_code": "DS101", "credits": 3}],
                "course_count": 1,
                "duration": None,
                "description": None,
                "university": {
                    "university_id": UNIVERSITY_B,
                    "university_name": "Beta University",
                    "city": "Santa Fe",
                    "state": "NM",
                },
            },
        }
        return [programs[item] for item in program_ids if item in programs]

    async def get_careers_for_programs(self, db, program_ids):
        self.calls.append(("get_careers_for_programs", db, program_ids))
        return {
            PROGRAM_A: [
                {"career_id": "career-shared", "career_name": "Software Engineer"},
                {"career_id": "career-a", "career_name": "Systems Analyst"},
            ],
            PROGRAM_B: [
                {"career_id": "career-shared", "career_name": "Software Engineer"},
                {"career_id": "career-b", "career_name": "Data Analyst"},
            ],
        }


class _LegacyRepository:
    def __init__(self):
        self.calls = []

    async def search_universities(self, db, **filters):
        self.calls.append(("search_universities", db, filters))
        return [
            {
                "university_id": UNIVERSITY_A,
                "university_name": "Alpha University",
                "location": {"city": "Albuquerque", "state": "NM"},
                "website": "https://alpha.example.edu",
                "available_programs": [{"program_id": PROGRAM_A, "program_name": "Computer Science"}],
                "program_count": 1,
                "public_private": None,
            }
        ]

    async def get_universities_by_ids(self, db, university_ids):
        self.calls.append(("get_universities_by_ids", db, university_ids))
        return [
            {"university_id": UNIVERSITY_A, "university_name": "Alpha University", "program_count": 1},
            {"university_id": UNIVERSITY_B, "university_name": "Beta University", "program_count": 2},
        ]

    async def search_programs(self, db, **filters):
        self.calls.append(("search_programs", db, filters))
        return [{"program_id": PROGRAM_A, "program_name": "Computer Science", "degree": "BS"}]

    async def get_programs_by_ids(self, db, program_ids):
        self.calls.append(("get_programs_by_ids", db, program_ids))
        return [
            {
                "program_id": PROGRAM_A,
                "program_name": "Computer Science",
                "total_credit_hours": 120,
                "required_courses": [{"course_code": "CS101", "credits": 3}],
                "duration": None,
                "description": None,
            },
            {
                "program_id": PROGRAM_B,
                "program_name": "Data Science",
                "total_credit_hours": 124,
                "required_courses": [{"course_code": "DS101", "credits": 3}],
                "duration": None,
                "description": None,
            },
        ]

    async def get_careers_for_programs(self, db, program_ids):
        self.calls.append(("get_careers_for_programs", db, program_ids))
        return {
            PROGRAM_A: [
                {"career_id": "career-shared", "career_name": "Software Engineer"},
                {"career_id": "career-a", "career_name": "Systems Analyst"},
            ],
            PROGRAM_B: [
                {"career_id": "career-shared", "career_name": "Software Engineer"},
                {"career_id": "career-b", "career_name": "Data Analyst"},
            ],
        }


class _Provider(BaseLLMProvider):
    provider_name = "test"

    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    async def generate(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        return self.responses.pop(0)

    async def generate_structured(self, request, response_model):
        raise NotImplementedError

    async def health_check(self):
        return LLMHealthCheck(provider=self.provider_name, ok=True, message="ok")


def test_comparison_tool_registry_matches_beta_v1_order():
    assert [tool.name for tool in COMPARISON_TOOLS] == EXPECTED_TOOL_NAMES
    assert all(isinstance(tool.description, str) and tool.description for tool in COMPARISON_TOOLS)
    assert all(callable(tool.execute) for tool in COMPARISON_TOOLS)


def test_college_comparison_module_metadata_and_tools():
    comparison_module = CollegeComparisonModule(db=object())

    assert module.MODULE_NAME == "college_comparison"
    assert module.MODULE_DESCRIPTION == "Help students compare universities and academic programs using existing EdPlan data."
    assert comparison_module.name == "college_comparison"
    assert comparison_module.available_tool_names == EXPECTED_TOOL_NAMES
    assert [schema["function"]["name"] for schema in comparison_module.tool_schemas] == EXPECTED_TOOL_NAMES


def test_register_module_uses_existing_selector_alias_without_changing_intrinsic_name():
    registry = ModuleRegistry()
    registered = register_module(registry, db=object())

    assert registered.name == "college_comparison"
    assert MODULE_REGISTRY_NAME == COLLEGE_COMPARISON
    assert registry.exists(COLLEGE_COMPARISON)
    assert registry.get(COLLEGE_COMPARISON) is registered

    selection = ModuleSelector(registry=registry).select(
        IntentResult(intent="college_comparison", confidence=0.9, target_modules=[COLLEGE_COMPARISON])
    )
    assert selection.selected_modules == [COLLEGE_COMPARISON]
    assert selection.unavailable_modules == []


def test_comparison_prompts_are_registered():
    prompt_registry = PromptRegistry()

    assert prompt_registry.get("comparison.default").template == "College comparison context: {context}"
    advisor = prompt_registry.get("comparison.advisor")
    assert "Never invent rankings" in advisor.template
    assert "current EdPlan database" in advisor.template


def test_comparison_api_routes_are_registered():
    paths = {route.path for route in get_student_router().routes}

    assert "/api/comparison/universities/search" in paths
    assert "/api/comparison/programs/compare" in paths


def test_comparison_service_searches_universities_with_existing_data():
    repository = _LegacyRepository()
    service = ComparisonService(repository)
    db = object()

    result = asyncio.run(service.search_universities(db, state="NM", name="Alpha"))

    assert result["metadata"] == {"count": 1, "source": "edplan_database"}
    assert result["results"][0]["available_programs"][0]["program_name"] == "Computer Science"
    assert repository.calls[-1] == (
        "search_universities",
        db,
        {"state": "NM", "city": None, "name": "Alpha", "limit": 10},
    )


def test_comparison_service_compares_universities_without_rankings():
    service = ComparisonService(_LegacyRepository())

    result = asyncio.run(service.compare_universities(object(), [UNIVERSITY_A, UNIVERSITY_B]))

    assert [item["university_name"] for item in result["universities"]] == ["Alpha University", "Beta University"]
    assert "rankings" in result["metadata"]["unavailable_fields"]
    assert "tuition" in result["metadata"]["unavailable_fields"]


def test_comparison_service_searches_programs():
    repository = _LegacyRepository()
    service = ComparisonService(repository)

    result = asyncio.run(service.search_programs(object(), university_id=UNIVERSITY_A, degree="BS", name="Computer"))

    assert result["results"][0]["program_name"] == "Computer Science"
    assert repository.calls[-1][2]["university_id"] == UNIVERSITY_A


def test_comparison_service_compares_programs_and_attaches_careers():
    service = ComparisonService(_LegacyRepository())

    result = asyncio.run(service.compare_programs(object(), [PROGRAM_A, PROGRAM_B]))

    assert result["programs"][0]["total_credit_hours"] == 120
    assert result["programs"][0]["available_careers"][0]["career_name"] == "Software Engineer"
    assert "salaries" in result["metadata"]["unavailable_fields"]


def test_comparison_service_compares_career_paths():
    service = ComparisonService(_LegacyRepository())

    result = asyncio.run(service.compare_career_paths(object(), [PROGRAM_A, PROGRAM_B]))

    assert result["overlapping_careers"] == [{"career_id": "career-shared", "career_name": "Software Engineer"}]
    assert result["unique_careers"][PROGRAM_A] == [{"career_id": "career-a", "career_name": "Systems Analyst"}]
    assert result["metadata"]["message"] is None


def test_comparison_tools_delegate_to_service():
    service = ComparisonService(_LegacyRepository())
    db = object()

    assert isinstance(
        asyncio.run(SearchUniversitiesTool(service).execute(db, {"state": "NM"}))["results"],
        list,
    )
    assert isinstance(
        asyncio.run(SearchProgramsTool(service).execute(db, {"name": "Computer"}))["results"],
        list,
    )
    assert asyncio.run(CompareUniversitiesTool(service).execute(db, [UNIVERSITY_A, UNIVERSITY_B]))["metadata"]["found_count"] == 2
    assert asyncio.run(CompareProgramsTool(service).execute(db, [PROGRAM_A, PROGRAM_B]))["metadata"]["found_count"] == 2
    assert "mapped_careers" in asyncio.run(CompareCareerPathsTool(service).execute(db, [PROGRAM_A, PROGRAM_B]))


def test_comparison_service_builds_deterministic_advising_comparison():
    service = ComparisonService(_Repository())

    result = asyncio.run(
        service.build_advising_comparison(
            object(),
            student_context={"program": {"program_name": "Computer Science"}},
            query="Compare Alpha and Beta for computer science.",
        )
    )

    assert result["summary"]["status"] == "ready"
    assert result["summary"]["recommended_university"] == "Alpha University"
    assert [row["university_name"] for row in result["comparison_table"]] == [
        "Alpha University",
        "Beta University",
    ]
    assert result["ranked_recommendations"][0]["score"] >= result["ranked_recommendations"][1]["score"]


def test_comparison_service_asks_for_context_when_request_is_underspecified():
    service = ComparisonService(_Repository())

    result = asyncio.run(
        service.build_advising_comparison(
            object(),
            student_context={},
            query="Which university is best?",
        )
    )

    assert result["summary"]["status"] == "needs_context"
    assert result["validation"]["missing"] == ["universities_or_programs_to_compare"]
    assert result["recommendations"][0].startswith("Please name at least two universities")


@pytest.mark.asyncio
async def test_college_comparison_advisor_explains_deterministic_comparison():
    class _AdvisingService:
        def __init__(self):
            self.calls = []

        async def build_advising_comparison(self, db, *, student_context, query):
            self.calls.append((db, student_context, query))
            return {
                "summary": {
                    "status": "ready",
                    "query": query,
                    "university_count": 2,
                    "program_count": 2,
                    "recommended_university": "Alpha University",
                    "program_focus": "Computer Science",
                },
                "student_context": student_context,
                "universities": [
                    {"university_id": UNIVERSITY_A, "university_name": "Alpha University"},
                    {"university_id": UNIVERSITY_B, "university_name": "Beta University"},
                ],
                "programs": [],
                "recommended_university": {
                    "rank": 1,
                    "university_id": UNIVERSITY_A,
                    "university_name": "Alpha University",
                    "score": 85,
                    "reasons": ["offers matching program data"],
                    "programs": [],
                    "unavailable_fields": ["tuition"],
                },
                "comparison_table": [
                    {
                        "university_id": UNIVERSITY_A,
                        "university_name": "Alpha University",
                        "matching_programs": [],
                    },
                    {
                        "university_id": UNIVERSITY_B,
                        "university_name": "Beta University",
                        "matching_programs": [],
                    },
                ],
                "ranked_recommendations": [
                    {
                        "rank": 1,
                        "university_id": UNIVERSITY_A,
                        "university_name": "Alpha University",
                        "score": 85,
                        "reasons": ["offers matching program data"],
                    }
                ],
                "pros": [],
                "cons": [],
                "advisor_notes": [],
                "recommendations": ["Review transfer rules with an advisor."],
                "validation": {"status": "valid", "warnings": []},
                "warnings": [],
                "career_paths": {},
                "multi_agent_context": {},
            }

    service = _AdvisingService()
    provider = _Provider(
        [
            LLMResponse(model="test", content="Alpha and Beta differ by catalog programs; career overlap is Software Engineer."),
        ]
    )
    comparison_module = CollegeComparisonModule(
        db=object(),
        llm_provider=provider,
        service=service,
    )

    response = await comparison_module.execute(
        StudentContext(),
        "Compare Alpha and Beta for computer science.",
    )

    assert response.content.startswith("Alpha and Beta")
    assert response.data["comparison_plan"]["summary"]["recommended_university"] == "Alpha University"
    assert response.metadata["deterministic_comparison"] is True
    assert response.metadata["advisor_prompt"] == "comparison.advisor"
    assert provider.requests[0].tools == []
    assert service.calls[0][2] == "Compare Alpha and Beta for computer science."


def test_comparison_request_schemas_accept_beta_v1_payloads():
    assert UniversitySearchRequest(state="NM").state == "NM"
    assert UniversityCompareRequest(university_ids=[UNIVERSITY_A, UNIVERSITY_B]).university_ids[0] == UNIVERSITY_A
    assert ProgramSearchRequest(name="Computer Science").name == "Computer Science"
    assert ProgramCompareRequest(program_ids=[PROGRAM_A, PROGRAM_B]).program_ids == [PROGRAM_A, PROGRAM_B]
    assert CareerPathCompareRequest(program_ids=[PROGRAM_A, PROGRAM_B]).program_ids == [PROGRAM_A, PROGRAM_B]
