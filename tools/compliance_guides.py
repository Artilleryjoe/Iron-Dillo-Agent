"""Compliance guidance for common East Texas business standards."""

from __future__ import annotations

from typing import Dict, List

_GUIDES: Dict[str, Dict[str, List[str]]] = {
    "nist-csf": {
        "title": "NIST Cybersecurity Framework",
        "checklist": [
            "Identify critical assets and data owners.",
            "Protect with MFA, encryption at rest, and least privilege.",
            "Detect by enabling centralized logging and alert triage.",
            "Respond through a written incident response playbook.",
            "Recover using tested backups and post-incident reviews.",
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
