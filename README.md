# Iron Dillo Cybersecurity Buddy

Iron Dillo is a watsonx-powered cybersecurity buddy that helps small businesses and
rural or underserved communities make sense of security guidance. The project now
ships as a standard Python package with a simple command line interface for quick
briefings.

## Features

- Tool calling for security awareness tips, compliance reminders, and rapid risk
  triage.
- Retrieval Augmented Generation (RAG) primitives to experiment with bespoke
  content libraries.
- Rotating armadillo and pangolin facts to keep learning light-hearted.
- SQLite-backed preference store for persisting lightweight user settings.

## Installation

Iron Dillo targets Python 3.10+. Create a virtual environment and install the
package in editable mode along with developer tooling:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The editable install pulls in the package dependencies declared in `pyproject.toml`
while keeping the source tree editable for development.

## Usage

Run the CLI via the console script installed by the package:

```bash
iron-dillo "How do I brief a co-op about securing irrigation controllers?"
```

For direct execution inside the repository you can also call the wrapper script:

```bash
python agent.py "How should I protect payroll systems?" --audience small_businesses
```

Available options can be listed with `python agent.py --help`. The CLI stitches
together security tips, compliance checklists, and a qualitative risk assessment.

## Running tests

The repository includes a lightweight pytest suite:

```bash
pytest
```

## Project layout

Source files live under `src/iron_dillo/` and are exposed through the
`iron_dillo` package namespace:

- `cli.py` – command line interface entry point.
- `agent_model.py` – shared Pydantic models.
- `buddy_facts.py` – rotating fact helper utilities.
- `memory.py` – SQLite-backed preference store.
- `tools/` – composable domain helpers for awareness, compliance, risk, and RAG.

## Additional sandbox

The repository also ships with **Iron Dillo Cybersandbox AI (IDCSA)** under
`iron_dillo_cybersandbox_ai/`. The sandbox provides a FastAPI backend, Tailwind
inspired frontend, and helper scripts for running a completely offline
Ollama-powered workflow featuring prompt vector exploration, document RAG, and
security mini-apps. See `iron_dillo_cybersandbox_ai/README.md` for usage
details.

## Development notes

- Do not commit API keys or tokens. Use environment variables instead.
- Keep large vector indexes and other generated data out of version control; the
  `data/` directory remains gitignored for this purpose.
- A sample GitHub Actions workflow is available in `.github/workflows/ci.yml`
  for running the test suite on every push.
