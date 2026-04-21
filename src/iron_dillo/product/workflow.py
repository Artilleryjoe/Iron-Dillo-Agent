"""Product workflow orchestration for readiness brief generation."""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

from ..agent_model import AgentResponse, ToolCall
from ..buddy_facts import get_random_fact
from ..tools import assess_risk, get_compliance_guide, get_security_tip
from .artifact_renderer import render_markdown_brief
from .intake_normalizer import normalize_intake
from .score_calculator import calculate_score
from .schemas import (
    ChecklistItem,
    FollowUp,
    GuidedIntake,
    ImmediateAction,
    IntakeSummary,
    LongTermRecommendation,
    Persona,
    ReadinessBrief,
    SevenDayPlanItem,
)
from .triage_engine import triage_intake


def generate_readiness_brief(
    intake: GuidedIntake,
    *,
    topic: str = "identity",
    compliance_standard: str | None = None,
    include_fact: bool = True,
) -> tuple[ReadinessBrief, AgentResponse]:
    intake, completeness = normalize_intake(intake)
    classification = triage_intake(intake)
    score = calculate_score(classification, completeness)

    tip = get_security_tip(intake.audience, topic)
    risk_report = assess_risk(
        audience=intake.audience,
        impact="high" if score.band.value in {"high", "critical"} else "medium",
        likelihood="likely" if score.value >= 70 else "possible",
        description=intake.concern,
    )

    immediate_actions = [
        ImmediateAction(action=action, owner="operations_lead", due="within 24h")
        for action in tip["actions"][:3]
    ]
    immediate_actions.extend(
        ImmediateAction(action=item, owner="security_owner", due="within 24h")
        for item in risk_report.recommendations[:2]
    )

    brief = ReadinessBrief(
        brief_id=f"brief-{uuid4().hex[:8]}",
        created_at=datetime.utcnow(),
        persona=Persona(organization_type=intake.business_type),
        scenario=intake.scenario,
        intake_summary=IntakeSummary(
            employee_count_band=intake.employee_count_band,
            critical_systems=intake.critical_systems,
            concern=intake.concern,
            safeguards=intake.safeguards,
            urgency=intake.urgency.value,
        ),
        classification=classification,
        score=score,
        executive_summary=(
            f"{intake.business_type.title()} reported {intake.concern}. "
            f"Current posture is classified as {classification.severity.value} severity across "
            f"{', '.join(classification.affected_domains)} domains with a normalized score of {score.value}."
        ),
        top_findings=[
            {
                "finding": f"Primary risk category: {classification.risk_category}",
                "impact": "Potential for business disruption and data exposure if left unresolved.",
            },
            {
                "finding": f"Intake confidence is {score.confidence.value}",
                "impact": "Unknown inputs can mask hidden dependencies and increase uncertainty.",
            },
        ],
        immediate_actions=immediate_actions[:5],
        seven_day_plan=[
            SevenDayPlanItem(
                day_range="Day 1-3",
                objective="Stabilize highest-risk pathways",
                tasks=classification.likely_controls[:3],
            ),
            SevenDayPlanItem(
                day_range="Day 4-7",
                objective="Confirm controls and ownership",
                tasks=["Run validation checks", "Document residual risk", "Schedule leadership review"],
            ),
        ],
        long_term_recommendations=[
            LongTermRecommendation(
                recommendation="Adopt a quarterly readiness review rhythm",
                rationale="Prevents drift and improves confidence in incident response execution.",
            )
        ],
        printable_checklist=[ChecklistItem(item=action.action) for action in immediate_actions[:5]],
        follow_up=FollowUp(
            review_date=(datetime.utcnow() + timedelta(days=7)).date(),
            escalate_if="Any material control remains incomplete after 7 days or signs of active compromise emerge.",
        ),
    )

    tool_calls = [
        ToolCall(name="security_awareness", arguments={"audience": intake.audience, "topic": topic}),
        ToolCall(name="risk_assessor", arguments={"audience": intake.audience, "severity": score.band.value}),
    ]

    if compliance_standard:
        _ = get_compliance_guide(compliance_standard)
        tool_calls.append(ToolCall(name="compliance_guides", arguments={"standard": compliance_standard}))

    response = AgentResponse(
        message=render_markdown_brief(brief),
        fact=get_random_fact() if include_fact else None,
        tool_calls=tool_calls,
    )
    return brief, response


__all__ = ["generate_readiness_brief"]
