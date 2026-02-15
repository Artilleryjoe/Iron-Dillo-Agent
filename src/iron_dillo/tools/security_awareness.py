"""Security awareness coaching tips tailored for Iron Dillo clients."""

from __future__ import annotations

from typing import Dict, List

# Each audience receives topic-specific messaging to keep recommendations actionable
_TIPS: Dict[str, Dict[str, Dict[str, List[str]]]] = {
    "individuals": {
        "identity": {
            "summary": "Monitor credit and enable alerts to catch fraud early.",
            "actions": [
                "Freeze credit with the major bureaus to block unauthorized loans.",
                "Set up SMS alerts on bank accounts for transactions over $50.",
                "Use password managers to generate unique credentials for every site.",
            ],
        },
        "devices": {
            "summary": "Keep phones and laptops patched and backed up.",
            "actions": [
                "Schedule automatic updates on mobile devices weekly.",
                "Install reputable antivirus and allow real-time scanning.",
                "Enable encrypted backups to a trusted cloud provider.",
            ],
        },
        "cloud": {
            "summary": "Protect cloud accounts with hardened authentication and alerting.",
            "actions": [
                "Enable phishing-resistant MFA wherever passkeys are supported.",
                "Turn on impossible-travel and suspicious-login alerts.",
                "Review third-party app access to email and storage quarterly.",
            ],
        },
        "incident_response": {
            "summary": "Prepare simple but practiced response steps before an emergency.",
            "actions": [
                "Keep an offline contact sheet for banks, providers, and family stakeholders.",
                "Document account recovery steps for critical services in a secure vault.",
                "Practice one yearly ransomware and identity theft tabletop scenario.",
            ],
        },
    },
    "small_businesses": {
        "identity": {
            "summary": "Protect payroll and invoicing systems from takeover attempts.",
            "actions": [
                "Require MFA for accounting and banking portals.",
                "Review vendor change requests by phone before approving.",
                "Limit admin rights on finance workstations to dedicated users.",
            ],
        },
        "devices": {
            "summary": "Harden point-of-sale and office endpoints in busy storefronts.",
            "actions": [
                "Deploy endpoint detection with centralized alerting.",
                "Isolate point-of-sale networks from guest Wi-Fi segments.",
                "Maintain an asset inventory with warranty and patch status.",
            ],
        },
        "cloud": {
            "summary": "Establish a zero-trust baseline for SaaS and cloud administration.",
            "actions": [
                "Enforce conditional access for privileged roles and remote admins.",
                "Route cloud audit logs to a SIEM with 12+ months retention.",
                "Require just-in-time elevation for finance and HR cloud tenants.",
            ],
        },
        "supply_chain": {
            "summary": "Reduce third-party cyber exposure through measurable vendor controls.",
            "actions": [
                "Inventory critical suppliers and assign a cyber risk tier to each.",
                "Add contract clauses for breach notification and vulnerability disclosure.",
                "Verify software updates using signed packages and approved repositories.",
            ],
        },
        "incident_response": {
            "summary": "Operationalize incident response with executive and legal readiness.",
            "actions": [
                "Maintain a 24/7 escalation tree that includes legal and communications leads.",
                "Define evidence handling steps to preserve forensic timelines.",
                "Run quarterly tabletops that include ransomware, BEC, and cloud takeover playbooks.",
            ],
        },
    },
    "rural_operations": {
        "identity": {
            "summary": "Defend co-op shared accounts from password reuse attacks.",
            "actions": [
                "Rotate shared passwords every 90 days and store in a vault.",
                "Require call-back verification for wire transfer approvals.",
                "Provide phishing simulations before harvest and tax seasons.",
            ],
        },
        "devices": {
            "summary": "Fortify operational equipment that depends on remote access.",
            "actions": [
                "Place firewalls in front of irrigation and SCADA controllers.",
                "Use LTE failover with VPN tunnels for remote sites.",
                "Schedule quarterly tabletop exercises for outage response.",
            ],
        },
        "cloud": {
            "summary": "Secure distributed cloud operations for remote facilities and co-ops.",
            "actions": [
                "Segment farm management SaaS identities from operational administrator accounts.",
                "Mirror cloud logs to low-bandwidth friendly storage for continuity.",
                "Validate backup restore procedures before peak planting and harvest windows.",
            ],
        },
        "supply_chain": {
            "summary": "Prepare for supplier disruption and compromised service providers.",
            "actions": [
                "Map dependencies for seed, fuel, and logistics platforms with cyber contacts.",
                "Require MFA and least privilege for contractor remote maintenance tools.",
                "Develop contingency playbooks for telecom and satellite service outages.",
            ],
        },
        "incident_response": {
            "summary": "Coordinate cyber incident response across distributed rural teams.",
            "actions": [
                "Pre-stage incident communication templates for low-connectivity sites.",
                "Assign a response captain for each region and test handoffs twice a year.",
                "Capture lessons learned after every outage and update SOPs within 10 business days.",
            ],
        },
    },
}


def get_security_tip(audience: str, topic: str = "identity") -> Dict[str, List[str]]:
    """Return tailored security awareness guidance.

    Parameters
    ----------
    audience:
        Target persona: "individuals", "small_businesses", or "rural_operations".
    topic:
        Area of focus such as "identity" or "devices". Defaults to identity protection.

    Raises
    ------
    ValueError
        If the audience or topic is not recognized.
    """

    normalized_audience = audience.strip().lower()
    normalized_topic = topic.strip().lower()

    if normalized_audience not in _TIPS:
        raise ValueError(f"Unknown audience '{audience}'. Expected one of {sorted(_TIPS)}")

    audience_topics = _TIPS[normalized_audience]

    if normalized_topic not in audience_topics:
        raise ValueError(
            f"Unknown topic '{topic}' for audience '{normalized_audience}'. "
            f"Expected one of {sorted(audience_topics)}"
        )

    tip = audience_topics[normalized_topic]
    return {
        "audience": normalized_audience,
        "topic": normalized_topic,
        "summary": tip["summary"],
        "actions": list(tip["actions"]),
    }


__all__ = ["get_security_tip"]
