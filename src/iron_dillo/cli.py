"""Command line interface for the Iron Dillo Cybersecurity Buddy."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from .agent_model import AgentResponse, AgentTurn, ToolCall
from .buddy_facts import get_random_fact
from .config import Settings, get_settings, load_settings
from .logging_utils import configure_logging, get_logger
from .tools import assess_risk, get_compliance_guide, get_security_tip

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
    """Generate a briefing that blends tips, compliance, and risk insights."""

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

    turn = AgentTurn(prompt=prompt, audience=audience, include_fact=include_fact)

    tip = get_security_tip(turn.audience, topic)

    risk_report = assess_risk(
        audience=turn.audience,
        impact=impact,
        likelihood=likelihood,
        description=turn.prompt,
    )

    message_lines = [
        f"Audience: {turn.audience.replace('_', ' ').title()}",
        f"Prompt: {turn.prompt}",
        "",
        f"Focus area ({tip['topic']}): {tip['summary']}",
    ]

    message_lines.append("Key actions:")
    message_lines.extend(f"- {action}" for action in tip["actions"])

    message_lines.append("")
    message_lines.append(
        f"Risk rating: {risk_report.level.title()} (score {risk_report.score})"
    )
    message_lines.append("Risk recommendations:")
    message_lines.extend(f"- {item}" for item in risk_report.recommendations)

    tool_calls = [
        ToolCall(name="security_awareness", arguments={"audience": turn.audience, "topic": topic}),
        ToolCall(
            name="risk_assessor",
            arguments={
                "audience": turn.audience,
                "impact": impact,
                "likelihood": likelihood,
                "description": turn.prompt,
            },
        ),
    ]

    if compliance_standard:
        guide = get_compliance_guide(compliance_standard)
        message_lines.append("")
        message_lines.append(f"Compliance ({guide['title']}):")
        message_lines.extend(f"- {item}" for item in guide["checklist"])
        tool_calls.append(
            ToolCall(
                name="compliance_guides",
                arguments={"standard": compliance_standard},
            )
        )
    else:
        guide = None

    fact: Optional[str] = get_random_fact() if turn.include_fact else None

    logger.debug(
        "Brief assembled",
        extra={
            "tool_calls": [call.name for call in tool_calls],
            "fact_included": fact is not None,
        },
    )

    return AgentResponse(
        message="\n".join(message_lines),
        fact=fact,
        tool_calls=tool_calls,
    )


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
