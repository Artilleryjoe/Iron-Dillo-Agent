"""Validation and normalization for guided intake payloads."""

from __future__ import annotations

from .scenario_selector import get_scenario_profile
from .schemas import GuidedIntake


def normalize_intake(intake: GuidedIntake) -> tuple[GuidedIntake, float]:
    profile = get_scenario_profile(intake.scenario)

    completeness_hits = 0
    for field_name in profile.required_fields:
        value = getattr(intake, field_name, None)
        if isinstance(value, list):
            completeness_hits += 1 if value else 0
        elif isinstance(value, str):
            completeness_hits += 1 if value.strip() and value != "unknown" else 0
        else:
            completeness_hits += 1 if value is not None else 0

    completeness = completeness_hits / max(len(profile.required_fields), 1)
    if not intake.critical_systems:
        intake.critical_systems = ["unknown"]
    if not intake.safeguards:
        intake.safeguards = ["unknown"]

    return intake, completeness


__all__ = ["normalize_intake"]
