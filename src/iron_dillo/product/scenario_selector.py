"""Scenario selection and default policy profiles."""

from __future__ import annotations

from .schemas import Scenario, ScenarioProfile

_SCENARIO_PROFILES: dict[Scenario, ScenarioProfile] = {
    Scenario.PHISHING_CONCERN: ScenarioProfile(
        scenario=Scenario.PHISHING_CONCERN,
        required_fields=["business_type", "employee_count_band", "concern", "urgency"],
        default_domains=["identity", "data"],
        default_controls=["mfa", "email_filtering", "security_awareness_training"],
        default_severity="high",
    ),
    Scenario.WEAK_PASSWORDS_MFA: ScenarioProfile(
        scenario=Scenario.WEAK_PASSWORDS_MFA,
        required_fields=["business_type", "employee_count_band", "critical_systems"],
        default_domains=["identity"],
        default_controls=["password_manager", "mfa", "access_reviews"],
        default_severity="medium",
    ),
    Scenario.EXPOSED_WEBSITE_REMOTE_ACCESS: ScenarioProfile(
        scenario=Scenario.EXPOSED_WEBSITE_REMOTE_ACCESS,
        required_fields=["business_type", "critical_systems", "concern", "urgency"],
        default_domains=["network", "endpoint"],
        default_controls=["external_attack_surface_scan", "vpn", "patching"],
        default_severity="high",
    ),
    Scenario.DEVICE_LOSS: ScenarioProfile(
        scenario=Scenario.DEVICE_LOSS,
        required_fields=["business_type", "critical_systems", "safeguards"],
        default_domains=["endpoint", "data"],
        default_controls=["full_disk_encryption", "remote_wipe", "mdm"],
        default_severity="medium",
    ),
    Scenario.VENDOR_SOFTWARE_TRUST_CONCERN: ScenarioProfile(
        scenario=Scenario.VENDOR_SOFTWARE_TRUST_CONCERN,
        required_fields=["business_type", "critical_systems", "concern"],
        default_domains=["vendor", "data"],
        default_controls=["vendor_risk_review", "least_privilege", "contractual_security_clauses"],
        default_severity="medium",
    ),
    Scenario.GENERAL_READINESS_CHECK: ScenarioProfile(
        scenario=Scenario.GENERAL_READINESS_CHECK,
        required_fields=["business_type", "employee_count_band", "critical_systems"],
        default_domains=["identity", "endpoint", "network", "vendor", "data"],
        default_controls=["asset_inventory", "backup_testing", "incident_response_plan"],
        default_severity="low",
    ),
}


def get_scenario_profile(scenario: Scenario) -> ScenarioProfile:
    return _SCENARIO_PROFILES[scenario]


__all__ = ["get_scenario_profile"]
