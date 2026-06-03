from pydantic import BaseModel


class DiversityStats(BaseModel):
    white: float | None = None
    black: float | None = None
    hispanic: float | None = None
    asian: float | None = None
    two_or_more: float | None = None
    non_resident: float | None = None


class SocioEconomicStats(BaseModel):
    first_generation_share: float | None = None
    pell_grant_rate: float | None = None


class FamilyIncomeNetPrice(BaseModel):
    source: str | None = None
    breakdown: dict[str, float | None] | None = None


class CollegeInfo(BaseModel):
    type: str | None = None
    setting: str | None = None
    website: str | None = None
    location: str | None = None


class University(BaseModel):
    unit_id: int | None = None
    name: str | None = None
    city: str | None = None
    state: str | None = None
    website: str | None = None
    year: int | None = None
    organization_type: str | None = None
    size: int | None = None
    location_type: str | None = None
    graduation_rate: float | None = None
    average_annual_cost: float | None = None
    median_earnings: float | None = None
    financial_aid_debt: float | None = None
    typical_earnings: float | None = None
    campus_diversity: DiversityStats | None = None
    socioeconomic_diversity: SocioEconomicStats | None = None
    family_income_net_price: FamilyIncomeNetPrice | None = None
    college_info: CollegeInfo | None = None
    sat_reading_25th: float | None = None
    sat_reading_75th: float | None = None
    act_score: float | None = None
    act_score_25th: float | None = None
    act_score_75th: float | None = None
    acceptance_rate: float | None = None
    first_year_return_rate: float | None = None
    full_time_enrollment: int | None = None
    part_time_enrollment: int | None = None
    student_faculty_ratio: float | None = None
    federal_loan_rate: float | None = None
    median_debt: float | None = None
    typical_monthly_payment: float | None = None
    repayment_rate: float | None = None
    percent_more_than_hs: float | None = None


class CompareRequest(BaseModel):
    unit_ids: list[int]
