"""Lightweight risk triage helper for Iron Dillo engagements."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

_IMPACT_WEIGHTS: Dict[str, int] = {"low": 1, "medium": 2, "high": 3}
_LIKELIHOOD_WEIGHTS: Dict[str, int] = {"unlikely": 1, "possible": 2, "likely": 3}

_BASE_RECOMMENDATIONS: Dict[str, List[str]] = {
    "low": [
        "Document the finding, assign an owner, and monitor quarterly.",
        "Confirm baseline controls remain effective and evidence is retained.",
    ],
    "moderate": [
        "Schedule remediation within the next sprint or 30 days.",
        "Track mitigation in a risk register with executive visibility.",
        "Add the scenario to quarterly tabletop drills.",
    ],
    "high": [
        "Escalate to leadership and activate the incident response plan.",
        "Contain affected systems and preserve forensic artifacts.",
        "Initiate external notification workflows required by policy or regulation.",
    ],
}

_AUDIENCE_TIPS: Dict[str, str] = {
    "individuals": "Use password managers, passkeys, and tested backups for critical accounts.",
    "small_businesses": "Validate vendor access, finance controls, and privileged account hygiene.",
    "rural_operations": "Coordinate with co-op and field technology partners on failover and response testing.",
}


@dataclass(frozen=True)
class RiskReport:
    """Summarized output from :func:`assess_risk`."""

    level: str
    score: int
    recommendations: List[str]


def _normalize_scale(value: str, valid: Dict[str, int], label: str) -> str:
    key = value.strip().lower()
    if key not in valid:
        raise ValueError(f"Unknown {label} '{value}'. Expected one of {sorted(valid)}")
    return key


def assess_risk(
    *,
    audience: str,
    impact: str,
    likelihood: str,
    description: str | None = None,
) -> RiskReport:
    """Estimate qualitative risk and return mitigation suggestions.

    Parameters
    ----------
    audience:
        Persona requesting help – individuals, small_businesses, or rural_operations.
    impact:
        Potential business impact (low, medium, high).
    likelihood:
        Chance of occurrence (unlikely, possible, likely).
    description:
        Optional text included in returned recommendations for context.
    """

    normalized_audience = audience.strip().lower()
    if normalized_audience not in _AUDIENCE_TIPS:
        raise ValueError(
            f"Unknown audience '{audience}'. Expected one of {sorted(_AUDIENCE_TIPS)}"
        )

    impact_key = _normalize_scale(impact, _IMPACT_WEIGHTS, "impact")
    likelihood_key = _normalize_scale(likelihood, _LIKELIHOOD_WEIGHTS, "likelihood")

    score = _IMPACT_WEIGHTS[impact_key] * _LIKELIHOOD_WEIGHTS[likelihood_key]

    if score <= 2:
        level = "low"
    elif score <= 4:
        level = "moderate"
    else:
        level = "high"

    recommendations = list(_BASE_RECOMMENDATIONS[level])

    if description:
        recommendations.insert(0, f"Context: {description.strip()}")

    recommendations.append(_AUDIENCE_TIPS[normalized_audience])

    return RiskReport(level=level, score=score, recommendations=recommendations)


__all__ = ["RiskReport", "assess_risk"]
