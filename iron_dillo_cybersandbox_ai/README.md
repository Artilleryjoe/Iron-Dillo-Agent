# Iron Dillo Cybersandbox AI (IDCSA)

Iron Dillo Cybersandbox AI is a local-first playground for experimenting with prompt engineering, retrieval-augmented generation, and security automations without sending data to the cloud.

## Features

- **Prompt vector playground** – explore sanitised prompt embeddings and run local chat sessions with Ollama.
- **Document RAG** – ingest PDFs, Markdown, and text files into a local Chroma vector store backed by sentence-transformer embeddings.
- **Threat-intel aware retrieval** – modular vector, hybrid, and intel retrieval modes with MITRE-style tactic tagging, threat keyword enrichment, and scoped filtering by document or threat family.
- **Security mini-apps** – run IOC extraction, email header parsing, and log summarisation utilities without needing outbound connectivity.
- **Privacy guardrails** – optional egress blocking, metadata sanitisation, and append-only audit logging.

## Project layout

```
iron_dillo_cybersandbox_ai/
├─ backend/                # FastAPI app, RAG helpers, security utilities
├─ frontend/               # Tailwind-inspired static UI
├─ models/                 # Ollama Modelfile persona
├─ scripts/                # CLI helpers (demo seeding, ingestion)
├─ vault/                  # Your local documents (not committed)
└─ data/                   # Persistent Chroma storage & audit logs
```

## Getting started

1. Install [Ollama](https://ollama.com) and pull a compatible model such as `llama3`.
2. Create a Python environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install fastapi uvicorn chromadb sentence-transformers umap-learn numpy pydantic[dotenv] python-multipart
   ```

3. Copy `.env.example` to `.env` and adjust paths or model names as needed.
4. Seed the vault with demo content (optional):

   ```bash
   python -m iron_dillo_cybersandbox_ai.scripts.demo_seed
   ```

5. Start the API:

   ```bash
   uvicorn iron_dillo_cybersandbox_ai.backend.main:app --reload
   ```

6. Open `frontend/index.html` in a browser, or serve the `frontend/` directory via a static file server of your choice.


## Advanced modular RAG

IDCSA now supports a richer RAG workflow for cybersecurity intelligence use-cases:

- **Modular ingestion** with selectable chunking modes (`fixed` or `paragraph`) via `POST /rag/ingest?chunk_mode=...`.
- **Threat profiling on ingest** that tags chunks for common modern threat families (e.g. ransomware, zero-day, supply-chain, cloud abuse), extracts CVE/T-technique indicators, and stores tactic metadata for later filtering.
- **Retrieval modes** exposed through `POST /rag/query`:
  - `vector` for pure semantic retrieval
  - `hybrid` for semantic + keyword + threat-tag scoring
  - `intel` for threat-intel focused ranking using the same hybrid scoring with additional analyst-facing metadata
- **Scoped querying** with optional `doc_ids` and `required_threat_tags` fields to constrain results to specific intelligence sources or threat categories.

Example query payload:

```json
{
  "query": "Summarize ransomware initial access patterns tied to CVE-2024-3400",
  "top_k": 6,
  "retrieval_mode": "intel",
  "doc_ids": ["weekly_intel.md"],
  "required_threat_tags": ["ransomware", "vulnerability"]
}
```

## Environment variables

| Variable | Default | Description |
| --- | --- | --- |
| `ALLOW_EGRESS` | `false` | Block outbound network calls when `false`. |
| `DOCS_PATH` | `iron_dillo_cybersandbox_ai/vault` | Directory for ingested source documents. |
| `CHROMA_PATH` | `iron_dillo_cybersandbox_ai/data/chroma` | Persistence directory for Chroma. |
| `AUDIT_LOG_PATH` | `iron_dillo_cybersandbox_ai/data/audit.log` | Append-only audit log file. |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model used for vectorisation. |
| `OLLAMA_MODEL` | `llama3` | Ollama model invoked for chat completions. |

## Security defaults

- **Fail-closed egress**: API endpoints raise an error if outbound networking is disallowed by policy.
- **Sanitised analytics**: Vectors and plots exclude raw text, exposing only hashed identifiers and previews.
- **Auditability**: Each route appends JSON entries to the local audit log for traceability.

## License

This scaffold is provided under the Apache 2.0 License. See the root repository for details.
