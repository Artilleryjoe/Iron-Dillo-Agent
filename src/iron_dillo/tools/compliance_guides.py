"""Compliance guidance for modern and common business standards."""

from __future__ import annotations

from typing import Dict, List

_GUIDES: Dict[str, Dict[str, List[str]]] = {
    "nist-csf": {
        "title": "NIST Cybersecurity Framework 2.0",
        "checklist": [
            "Identify critical assets, business services, and mission dependencies.",
            "Protect with phishing-resistant MFA, encryption, and least privilege.",
            "Detect through centralized telemetry, EDR, and continuous monitoring.",
            "Respond with tested playbooks, legal notification paths, and communications plans.",
            "Recover via immutable backups, restoration drills, and lessons-learned reviews.",
        ],
    },
    "iso-27001": {
        "title": "ISO/IEC 27001 ISMS",
        "checklist": [
            "Define ISMS scope, risk methodology, and statement of applicability.",
            "Assign asset owners and classify information by business impact.",
            "Implement Annex A controls with documented operating procedures.",
            "Track control effectiveness using internal audits and KPIs.",
            "Perform management review and continuous improvement cycles.",
        ],
    },
    "soc2": {
        "title": "SOC 2 Trust Services Criteria",
        "checklist": [
            "Map controls to Security, Availability, and Confidentiality criteria.",
            "Capture change management evidence for production systems.",
            "Harden identity lifecycle controls for joiner, mover, and leaver events.",
            "Retain logs and incident records to support auditor sampling.",
            "Run annual readiness assessments before Type II reporting windows.",
        ],
    },
    "cis-controls": {
        "title": "CIS Critical Security Controls v8",
        "checklist": [
            "Maintain complete enterprise and software asset inventories.",
            "Enforce secure configuration baselines for endpoints and cloud services.",
            "Apply vulnerability management with risk-based remediation SLAs.",
            "Protect data with encryption, DLP, and restricted administrative paths.",
            "Exercise incident response procedures and recovery validation.",
        ],
    },
    "nis2": {
        "title": "NIS2 Directive Readiness",
        "checklist": [
            "Establish governance accountability at board and executive levels.",
            "Implement supply-chain risk controls for critical ICT providers.",
            "Define incident reporting workflows for rapid regulatory notification.",
            "Harden business continuity and crisis communication procedures.",
            "Demonstrate security training and cyber hygiene for all personnel.",
        ],
    },
    "hipaa": {
        "title": "HIPAA Security Rule",
        "checklist": [
            "Document risk analysis covering ePHI storage and access.",
            "Assign a security officer to enforce policies.",
            "Encrypt laptops and mobile devices that handle patient data.",
            "Train staff annually on privacy and breach reporting.",
            "Sign Business Associate Agreements with all vendors.",
        ],
    },
    "pci-dss": {
        "title": "PCI-DSS Essentials",
        "checklist": [
            "Isolate cardholder data networks from guest Wi-Fi.",
            "Change default POS passwords and disable unused services.",
            "Quarterly vulnerability scans with an ASV provider.",
            "Maintain access logs for one year with 90 days immediately available.",
            "Run annual penetration tests or after major changes.",
        ],
    },
}


def get_compliance_guide(standard: str) -> Dict[str, List[str]]:
    """Return a high-level checklist for the requested compliance standard."""

    key = standard.strip().lower()
    if key not in _GUIDES:
        raise ValueError(f"Unknown standard '{standard}'. Expected one of {sorted(_GUIDES)}")

    guide = _GUIDES[key]
    return {
        "standard": key,
        "title": guide["title"],
        "checklist": list(guide["checklist"]),
    }


__all__ = ["get_compliance_guide"]
