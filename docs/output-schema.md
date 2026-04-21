# Output Schema (v1)

This schema defines the standardized readiness brief artifact.

## Top-level structure

```yaml
brief_id: string
created_at: datetime
persona:
  role: string
  organization_type: string
scenario: enum
intake_summary:
  employee_count_band: string
  critical_systems: [string]
  concern: string
  safeguards: [string]
  urgency: enum
classification:
  risk_category: string
  severity: enum
  affected_domains: [string]
  likely_controls: [string]
score:
  value: integer   # 0-100
  band: enum       # low | medium | high | critical
  confidence: enum # low | medium | high
executive_summary: string
top_findings:
  - finding: string
    impact: string
immediate_actions:
  - action: string
    owner: string
    due: string
seven_day_plan:
  - day_range: string
    objective: string
    tasks: [string]
long_term_recommendations:
  - recommendation: string
    rationale: string
printable_checklist:
  - item: string
    status: enum # not_started | in_progress | done
follow_up:
  review_date: date
  escalate_if: string
```

## Authoring constraints

- Keep executive summary under 180 words.
- Cap immediate actions to top 5 items.
- Ensure each immediate action is owner- and deadline-bound.
- Include at least one escalation criterion.
