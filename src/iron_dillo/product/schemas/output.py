"""Output schema for standardized readiness brief artifacts."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field

from .intake import EmployeeCountBand
from .scenarios import Scenario


class SeverityBand(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConfidenceBand(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ChecklistStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Persona(BaseModel):
    role: str = "owner_operator"
    organization_type: str


class IntakeSummary(BaseModel):
    employee_count_band: EmployeeCountBand
    critical_systems: list[str] = Field(default_factory=list)
    concern: str
    safeguards: list[str] = Field(default_factory=list)
    urgency: str


class Classification(BaseModel):
    risk_category: str
    severity: SeverityBand
    affected_domains: list[str] = Field(default_factory=list)
    likely_controls: list[str] = Field(default_factory=list)


class Score(BaseModel):
    value: int = Field(ge=0, le=100)
    band: SeverityBand
    confidence: ConfidenceBand


class Finding(BaseModel):
    finding: str
    impact: str


class ImmediateAction(BaseModel):
    action: str
    owner: str
    due: str


class SevenDayPlanItem(BaseModel):
    day_range: str
    objective: str
    tasks: list[str] = Field(default_factory=list)


class LongTermRecommendation(BaseModel):
    recommendation: str
    rationale: str


class ChecklistItem(BaseModel):
    item: str
    status: ChecklistStatus = ChecklistStatus.NOT_STARTED


class FollowUp(BaseModel):
    review_date: date
    escalate_if: str


class ReadinessBrief(BaseModel):
    brief_id: str
    created_at: datetime
    persona: Persona
    scenario: Scenario
    intake_summary: IntakeSummary
    classification: Classification
    score: Score
    executive_summary: str = Field(max_length=1200)
    top_findings: list[Finding] = Field(default_factory=list)
    immediate_actions: list[ImmediateAction] = Field(default_factory=list, max_length=5)
    seven_day_plan: list[SevenDayPlanItem] = Field(default_factory=list)
    long_term_recommendations: list[LongTermRecommendation] = Field(default_factory=list)
    printable_checklist: list[ChecklistItem] = Field(default_factory=list)
    follow_up: FollowUp


__all__ = [
    "ChecklistItem",
    "ChecklistStatus",
    "Classification",
    "ConfidenceBand",
    "Finding",
    "FollowUp",
    "ImmediateAction",
    "IntakeSummary",
    "LongTermRecommendation",
    "Persona",
    "ReadinessBrief",
    "Score",
    "SevenDayPlanItem",
    "SeverityBand",
]
