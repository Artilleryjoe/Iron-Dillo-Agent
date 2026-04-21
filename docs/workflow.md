# v1 Workflow Specification

## Flagship workflow

**Name:** Rural Small Business Security Brief Generator

**Outcome:** A standardized cybersecurity readiness brief suitable for owner,
operator, or advisor review in one sitting.

## Step 1: Scenario selection

User selects one scenario:
- phishing concern
- weak passwords / MFA
- exposed website or remote access
- device loss
- vendor/software trust concern
- general readiness check

## Step 2: Guided intake

Collect the minimum viable context:
- business type
- employee count band
- critical systems/data
- primary concern description
- existing safeguards
- urgency level

### Intake guardrails
- Prefer structured choices over long free text.
- Keep questionnaire short enough to finish in under 10 minutes.
- Mark unknown answers explicitly rather than guessing.

## Step 3: Internal classification and scoring

### Classification outputs
- risk category
- severity band (low / medium / high / critical)
- affected domains (identity, endpoint, network, vendor, data)
- likely next controls

### Scoring outputs
- single normalized risk score (0-100)
- confidence indicator (high/medium/low) based on intake completeness

## Step 4: Artifact generation

Render a standardized output package:
1. executive summary
2. score and severity
3. top findings
4. immediate actions (first 24h)
5. 7-day action plan
6. longer-term recommendations
7. printable checklist

## Step 5: Next-action handoff

The generated brief should always end with:
- one owner-assigned action list
- one review date
- one escalation criterion for when to involve specialist support
