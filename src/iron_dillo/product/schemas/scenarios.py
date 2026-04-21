"""Scenario contracts and defaults for the product workflow."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Scenario(str, Enum):
    PHISHING_CONCERN = "phishing_concern"
    WEAK_PASSWORDS_MFA = "weak_passwords_mfa"
    EXPOSED_WEBSITE_REMOTE_ACCESS = "exposed_website_remote_access"
    DEVICE_LOSS = "device_loss"
    VENDOR_SOFTWARE_TRUST_CONCERN = "vendor_software_trust_concern"
    GENERAL_READINESS_CHECK = "general_readiness_check"


class ScenarioProfile(BaseModel):
    scenario: Scenario
    required_fields: list[str] = Field(default_factory=list)
    default_domains: list[str] = Field(default_factory=list)
    default_controls: list[str] = Field(default_factory=list)
    default_severity: str = "medium"


__all__ = ["Scenario", "ScenarioProfile"]
