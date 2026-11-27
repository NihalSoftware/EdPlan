from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Label = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
IntentId = Annotated[str, StringConstraints(pattern=r"^M(?:0[1-9]|[12][0-9]|3[0-8])$")]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Preferences(Contract):
    subject: Label | None = None
    education_stage: Label | None = None
    campus: Label | None = None
    city: Label | None = None
    credential: Literal["certificate", "associate", "bachelor", "master", "doctorate"] | None = None
    tuition_category: Literal["resident", "nonresident", "international"] | None = None
    budget_annual: int | None = Field(None, ge=0, le=1_000_000)
    budget_basis: Literal["tuition", "attendance"] | None = None
    credits_per_term: int | None = Field(None, ge=1, le=40)
    max_drive_minutes: int | None = Field(None, ge=1, le=600)
    online_only: bool | None = None
    public_only: bool | None = None
    sort_by: Literal["tuition", "graduation_rate", "credits"] | None = None


class Scenario(Preferences):
    baseline_credits: int | None = Field(None, ge=1, le=40)
    remaining_credits: int | None = Field(None, ge=0, le=999)
    include_summer: bool | None = None
    live_at_home: bool | None = None


class Context(Preferences):
    scenario: Scenario | None = None
    program_id: UUID | None = None
    plan_id: UUID | None = None


class TurnInput(Contract):
    request_id: UUID
    message: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)] | None = None
    choice_id: UUID | None = None

    @model_validator(mode="after")
    def check_choice(self):
        if (self.message is None) == (self.choice_id is None):
            raise ValueError("Provide a message or one server-issued choice")
        return self


class Choice(Contract):
    id: UUID
    label: str
    intent: IntentId
    kind: Literal["suggestion", "clarification"] = "suggestion"
    program_id: UUID | None = None
    plan_id: UUID | None = None


class Source(Contract):
    title: str
    url: str | None = None
    observed: str | None = None


class ResultTable(Contract):
    title: str
    columns: list[str]
    rows: list[list[str | int | float | None]]


class Action(Contract):
    id: UUID
    description: str
    preview: ResultTable
    expires_at: str


class Answer(Contract):
    intent: IntentId
    text: str
    status: Literal["answered", "partial", "clarification", "unavailable", "sensitive"] = "answered"
    sources: list[Source] = Field(default_factory=list)
    tables: list[ResultTable] = Field(default_factory=list)
    clarification: str | None = None
    choices: list[Choice] = Field(default_factory=list)
    suggestions: list[Choice] = Field(default_factory=list)
    follow_more: list[Choice] = Field(default_factory=list)
    link: str | None = None
    link_label: str | None = None
    action: Action | None = None


class Turn(Contract):
    id: UUID
    message: str
    answer: Answer
    context: Context


class Consent(Contract):
    retain_history: bool = False


class SessionView(Contract):
    id: UUID
    guest_token: str | None = None
    retain_history: bool
    expires_at: str
    context: Context
    turns: list[Turn]
