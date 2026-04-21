"""Render standardized readiness artifacts."""

from __future__ import annotations

from .schemas import ReadinessBrief


def render_markdown_brief(brief: ReadinessBrief) -> str:
    lines = [
        f"# Readiness Brief {brief.brief_id}",
        "",
        "## Executive summary",
        brief.executive_summary,
        "",
        f"## Score and severity\n- Score: {brief.score.value}/100 ({brief.score.band.value})\n- Confidence: {brief.score.confidence.value}",
        "",
        "## Top findings",
    ]
    lines.extend(f"- {item.finding}: {item.impact}" for item in brief.top_findings)
    lines.append("")
    lines.append("## Immediate actions (first 24h)")
    lines.extend(f"- {a.action} (Owner: {a.owner}, Due: {a.due})" for a in brief.immediate_actions)
    lines.append("")
    lines.append("## 7-day plan")
    lines.extend(f"- {item.day_range} {item.objective}: {', '.join(item.tasks)}" for item in brief.seven_day_plan)
    lines.append("")
    lines.append("## Longer-term recommendations")
    lines.extend(f"- {item.recommendation}: {item.rationale}" for item in brief.long_term_recommendations)
    lines.append("")
    lines.append("## Printable checklist")
    lines.extend(f"- [{ 'x' if item.status.value == 'done' else ' '}] {item.item}" for item in brief.printable_checklist)
    lines.append("")
    lines.append("## Next-action handoff")
    lines.append(f"- Review date: {brief.follow_up.review_date.isoformat()}")
    lines.append(f"- Escalate if: {brief.follow_up.escalate_if}")
    return "\n".join(lines)


__all__ = ["render_markdown_brief"]
