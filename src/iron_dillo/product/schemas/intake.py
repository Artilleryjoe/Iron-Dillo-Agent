"""Intake schema for guided workflow."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator

from .scenarios import Scenario


class EmployeeCountBand(str, Enum):
    SOLO_1_10 = "1_10"
    SMALL_11_50 = "11_50"
    MEDIUM_51_250 = "51_250"
    LARGE_251_PLUS = "251_plus"
    UNKNOWN = "unknown"


class UrgencyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class GuidedIntake(BaseModel):
    scenario: Scenario
    business_type: str = Field(min_length=2)
    employee_count_band: EmployeeCountBand = EmployeeCountBand.UNKNOWN
    critical_systems: list[str] = Field(default_factory=list)
    concern: str = Field(min_length=3)
    safeguards: list[str] = Field(default_factory=list)
    urgency: UrgencyLevel = UrgencyLevel.MEDIUM
    audience: str = Field(default="small_businesses")

    @field_validator("business_type", "concern", mode="before")
    @classmethod
    def _clean_text(cls, value: str) -> str:
        return value.strip()


__all__ = ["GuidedIntake", "EmployeeCountBand", "UrgencyLevel"]
