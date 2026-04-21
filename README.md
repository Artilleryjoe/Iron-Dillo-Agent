# Iron Dillo Cybersecurity Buddy

Iron Dillo Cybersecurity Buddy is a **local-first security brief generator** for
**small and rural businesses**. It guides an operator through a focused intake,
classifies the risk, and produces a structured cybersecurity readiness brief
with immediate actions, a 7-day plan, and a printable checklist.

## Who this is for

- Owners and operators of small businesses.
- Rural and underserved organizations that may not have dedicated security teams.
- Advisors helping these organizations triage a current cybersecurity concern.

## What it produces

For a single guided run, Iron Dillo outputs a standardized artifact containing:

- Executive summary.
- Risk score and severity band.
- Top findings and affected domains.
- Immediate actions (first 24 hours).
- 7-day plan.
- Longer-term recommendations.
- Printable checklist.

See:
- `docs/output-schema.md`
- `examples/sample-brief.md`
- `examples/sample-checklist.md`

## Primary use cases (v1)

1. Phishing concern.
2. Weak passwords or missing MFA.
3. Exposed website or remote access issue.
4. Device loss.
5. Vendor/software trust concern.
6. General readiness check.

Details: `docs/use-cases.md`.

## Workflow at a glance

1. **Scenario selection**: choose one of the six v1 scenarios.
2. **Guided intake**: capture business context, current safeguards, and urgency.
3. **Risk triage**: classify category, severity, domains, and likely controls.
4. **Artifact generation**: render a structured readiness brief and checklist.

Details: `docs/workflow.md`.

## Why it is different

- **Product-first flow**: one narrow flagship workflow instead of a generic tool buffet.
- **Local-first execution**: deterministic offline fallback with optional local model support.
- **Action-ready outputs**: standardized artifacts meant to support immediate operational decisions.

## Installation

Iron Dillo targets Python 3.10+. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Run the CLI:

```bash
iron-dillo "We had a suspected phishing email campaign this morning"
```

Repository-local wrapper:

```bash
python agent.py "I lost a laptop with customer data" --audience small_businesses
```

List options:

```bash
python agent.py --help
```

## GUI workflow

Launch the local GUI:

```bash
iron-dillo-gui --host 127.0.0.1 --port 8000 --open-browser
```

The GUI exposes the same flagship readiness-brief flow with separate panes for
intake and generated output.

## Configuration and logging

Pass JSON/TOML config files via `--config`:

```bash
iron-dillo "Brief my board on weak MFA coverage" --config ops.json --config secrets.toml
```

Environment variables, `.env` files, and config files can all be combined for
runtime configuration.

## Product-focused docs for this pivot

- `docs/use-cases.md`
- `docs/workflow.md`
- `docs/output-schema.md`
- `docs/module-layout.md`
- `examples/sample-brief.md`
- `examples/sample-checklist.md`

## Architecture (capability layer)

Source files live under `src/iron_dillo/`:

- `cli.py` – CLI entry point.
- `gui.py` – local GUI app.
- `agent_model.py` – shared Pydantic models.
- `memory.py` – SQLite-backed user preferences.
- `tools/` – security awareness, compliance guidance, risk logic, and RAG helpers.

## Additional sandbox

The repository also includes **Iron Dillo Cybersandbox AI (IDCSA)** under
`iron_dillo_cybersandbox_ai/` for broader experimentation. This remains useful
as supporting infrastructure, but the core product surface is the readiness
brief workflow documented above.

## Running tests

```bash
pytest
```
