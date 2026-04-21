"""Derive classification outputs from intake and scenario policy."""

from __future__ import annotations

from .scenario_selector import get_scenario_profile
from .schemas import Classification, GuidedIntake, SeverityBand


_SEVERITY_RANK = {SeverityBand.LOW: 1, SeverityBand.MEDIUM: 2, SeverityBand.HIGH: 3, SeverityBand.CRITICAL: 4}

_KEYWORDS = {
    "phishing": ("social_engineering", SeverityBand.HIGH, ["identity", "data"]),
    "ransomware": ("malware", SeverityBand.CRITICAL, ["endpoint", "data", "network"]),
    "mfa": ("identity_gap", SeverityBand.MEDIUM, ["identity"]),
    "remote access": ("external_exposure", SeverityBand.HIGH, ["network", "endpoint"]),
    "vendor": ("third_party", SeverityBand.MEDIUM, ["vendor", "data"]),
}


def triage_intake(intake: GuidedIntake) -> Classification:
    profile = get_scenario_profile(intake.scenario)
    concern = intake.concern.lower()

    risk_category = "general_readiness"
    severity = SeverityBand(profile.default_severity)
    affected_domains = list(profile.default_domains)

    for keyword, (category, key_severity, domains) in _KEYWORDS.items():
        if keyword in concern:
            risk_category = category
            severity = key_severity if _SEVERITY_RANK[key_severity] > _SEVERITY_RANK[severity] else severity
            affected_domains = sorted(set(affected_domains + domains))

    if intake.urgency.value == "high" and severity in {SeverityBand.LOW, SeverityBand.MEDIUM}:
        severity = SeverityBand.HIGH

    return Classification(
        risk_category=risk_category,
        severity=severity,
        affected_domains=affected_domains,
        likely_controls=list(profile.default_controls),
    )


__all__ = ["triage_intake"]
