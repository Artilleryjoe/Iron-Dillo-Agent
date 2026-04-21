"""Command line interface for the Iron Dillo Cybersecurity Buddy."""

from __future__ import annotations

import argparse
from pathlib import Path
from .agent_model import AgentResponse
from .config import Settings, get_settings, load_settings
from .logging_utils import configure_logging, get_logger
from .product import GuidedIntake, Scenario, generate_readiness_brief

__all__ = ["build_security_brief", "main"]


def build_security_brief(
    prompt: str,
    *,
    audience: str,
    topic: str = "identity",
    compliance_standard: str | None = None,
    impact: str = "medium",
    likelihood: str = "possible",
    include_fact: bool = True,
    settings: Settings | None = None,
) -> AgentResponse:
    """Generate a briefing through the product workflow with backward-compatible inputs."""

    settings = settings or get_settings()
    logger = get_logger("brief")
    logger.info(
        "Building security brief",
        extra={
            "audience": audience,
            "topic": topic,
            "compliance": compliance_standard,
            "impact": impact,
            "likelihood": likelihood,
            "environment": settings.environment,
        },
    )

    scenario = Scenario.GENERAL_READINESS_CHECK
    normalized_prompt = prompt.lower()
    if "phish" in normalized_prompt:
        scenario = Scenario.PHISHING_CONCERN
    elif "password" in normalized_prompt or "mfa" in normalized_prompt:
        scenario = Scenario.WEAK_PASSWORDS_MFA
    elif "remote" in normalized_prompt or "website" in normalized_prompt:
        scenario = Scenario.EXPOSED_WEBSITE_REMOTE_ACCESS
    elif "lost" in normalized_prompt or "stolen" in normalized_prompt:
        scenario = Scenario.DEVICE_LOSS
    elif "vendor" in normalized_prompt or "supplier" in normalized_prompt:
        scenario = Scenario.VENDOR_SOFTWARE_TRUST_CONCERN

    intake = GuidedIntake(
        scenario=scenario,
        business_type="small business",
        employee_count_band="11_50",
        critical_systems=[topic],
        concern=prompt,
        safeguards=[],
        urgency="high" if impact == "high" or likelihood == "likely" else "medium",
        audience=audience,
    )

    _, response = generate_readiness_brief(
        intake,
        topic=topic,
        compliance_standard=compliance_standard,
        include_fact=include_fact,
    )

    logger.debug(
        "Brief assembled",
        extra={
            "tool_calls": [call.name for call in response.tool_calls],
            "fact_included": response.fact is not None,
        },
    )
    return response


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", help="Question or concern to brief the assistant on")
    parser.add_argument(
        "--audience",
        default="small_businesses",
        choices=["individuals", "small_businesses", "rural_operations"],
        help="Persona to tailor the response for",
    )
    parser.add_argument(
        "--topic",
        default="identity",
        choices=["identity", "devices", "cloud", "supply_chain", "incident_response"],
        help="Security focus area",
    )
    parser.add_argument(
        "--compliance",
        help="Optional compliance framework such as nist-csf, iso-27001, soc2, cis-controls, nis2, hipaa, pci-dss",
    )
    parser.add_argument(
        "--impact",
        default="medium",
        choices=["low", "medium", "high"],
        help="Estimated business impact",
    )
    parser.add_argument(
        "--likelihood",
        default="possible",
        choices=["unlikely", "possible", "likely"],
        help="Estimated likelihood",
    )
    parser.add_argument(
        "--no-fact",
        action="store_true",
        help="Disable rotating armadillo facts",
    )
    parser.add_argument(
        "--config",
        action="append",
        type=Path,
        help="Optional path to a JSON or TOML configuration file",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    settings = (
        load_settings(override_files=args.config)
        if args.config
        else get_settings()
    )
    logger = configure_logging(settings)
    logger.info(
        "Iron Dillo CLI started",
        extra={"environment": settings.environment, "log_level": settings.log_level},
    )

    response = build_security_brief(
        prompt=args.prompt,
        audience=args.audience,
        topic=args.topic,
        compliance_standard=args.compliance,
        impact=args.impact,
        likelihood=args.likelihood,
        include_fact=not args.no_fact,
        settings=settings,
    )

    print(response.message)
    if response.fact:
        print("\nFun fact:")
        print(response.fact)


if __name__ == "__main__":
    main()
