# Iron Dillo Cybersecurity Buddy

A watsonx-powered cybersecurity assistant for small businesses and rural/underserved communities.

## Capabilities
- Tool-calling for tips, compliance hints, quick risk triage
- Python snippets execution for demos and calculations
- Retrieval Augmented Generation (RAG) over a master handbook and industry standards (NIST, ISO, HIPAA, PCI-DSS)
- Rotates fun armadillo/pangolin facts to keep learning engaging

## Quick start
```bash
pip install -r requirements.txt
python agent.py
```

## Notes

- Do not commit API keys or tokens. Use environment variables.
- Keep large vector indexes and data out of the repo (`data/` is gitignored).

## Optional: Continuous integration

A sample GitHub Actions workflow is available in `.github/workflows/ci.yml` for running the test suite on every push.
