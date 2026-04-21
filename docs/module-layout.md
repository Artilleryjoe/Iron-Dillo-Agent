# Proposed Module Layout for Product Pivot

This is a product-oriented layout proposal that preserves current capabilities
while enforcing a clear workflow boundary.

## New/expanded modules

- `src/iron_dillo/product/scenario_selector.py`
  - maps user-selected scenario to intake profile + triage policy
- `src/iron_dillo/product/intake_normalizer.py`
  - validates and normalizes guided intake inputs
- `src/iron_dillo/product/score_calculator.py`
  - calculates normalized risk score and confidence
- `src/iron_dillo/product/triage_engine.py`
  - derives category, severity, affected domains, likely controls
- `src/iron_dillo/product/artifact_renderer.py`
  - renders brief/checklist markdown and machine-readable payloads

## Existing modules retained as capability layer

- `src/iron_dillo/tools/security_awareness.py`
- `src/iron_dillo/tools/compliance_guides.py`
- `src/iron_dillo/tools/risk_assessor.py`
- `src/iron_dillo/tools/rag_store.py`

These continue to support enrichment but are no longer presented as the primary
product identity.

## Data contracts

- `src/iron_dillo/product/schemas/intake.py`
- `src/iron_dillo/product/schemas/output.py`
- `src/iron_dillo/product/schemas/scenarios.py`

## Suggested docs/examples alignment

- `docs/use-cases.md`
- `docs/workflow.md`
- `docs/output-schema.md`
- `examples/sample-brief.md`
- `examples/sample-checklist.md`
