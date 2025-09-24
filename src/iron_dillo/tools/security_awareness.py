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
