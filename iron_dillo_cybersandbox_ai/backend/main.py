"""FastAPI entrypoint for the Iron Dillo Cybersandbox."""

from __future__ import annotations

from typing import List

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .deps import get_embedding_client, get_ollama_client
from .rag import ingest_upload, query_rag
from .security import EgressBlockedError, build_audit_logger
from .settings import Settings, get_settings
from .utils import extract_iocs, parse_email_headers, summarize_logs
from .vectors import project_vectors

app = FastAPI(title="Iron Dillo Cybersandbox AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


def get_logger(settings: Settings = Depends(get_settings)):
    return build_audit_logger(settings)


class ChatRequest(BaseModel):
    message: str
    system_prompt: str | None = Field(
        default="You are Iron Dillo, a pragmatic cybersecurity copilot.",
        description="Optional system prompt overriding the Modelfile persona.",
    )


class ChatResponse(BaseModel):
    response: str


class EmbedRequest(BaseModel):
    texts: List[str]


class RagQueryRequest(BaseModel):
    query: str
    top_k: int = Field(5, ge=1, le=20)
    retrieval_mode: str = Field("vector", pattern="^(vector|hybrid|intel)$")
    doc_ids: List[str] = Field(default_factory=list)
    required_threat_tags: List[str] = Field(default_factory=list)


class IOCRequest(BaseModel):
    text: str


class HeaderRequest(BaseModel):
    headers: str


class LogSummaryRequest(BaseModel):
    text: str


@app.on_event("startup")
def _prepare_directories():
    settings = get_settings()
    settings.sanitized_docs_path
    settings.chroma_storage_path
    settings.audit_log_file


@app.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    settings: Settings = Depends(get_settings),
    logger=Depends(get_logger),
) -> ChatResponse:
    client = get_ollama_client(settings)
    try:
        result = await _run_in_threadpool(client.generate, payload.message, payload.system_prompt)
    except EgressBlockedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    logger.log(route="/chat", payload={"hash": hash(payload.message)})
    return ChatResponse(response=result.response)


async def _run_in_threadpool(func, *args, **kwargs):
    from fastapi.concurrency import run_in_threadpool

    return await run_in_threadpool(func, *args, **kwargs)


@app.post("/embed")
async def embed(
    payload: EmbedRequest,
    settings: Settings = Depends(get_settings),
    logger=Depends(get_logger),
):
    if not payload.texts:
        raise HTTPException(status_code=400, detail="No texts provided")
    client = get_embedding_client(settings)
    try:
        embeddings = await _run_in_threadpool(client.embed, payload.texts)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    logger.log(route="/embed", payload={"count": len(payload.texts)})
    return {"embeddings": embeddings}


@app.post("/rag/ingest")
async def rag_ingest(
    file: UploadFile = File(...),
    chunk_mode: str = Query("fixed", pattern="^(fixed|paragraph)$"),
    settings: Settings = Depends(get_settings),
    logger=Depends(get_logger),
):
    summary = await _run_in_threadpool(ingest_upload, file, settings=settings, chunk_mode=chunk_mode)
    logger.log(
        route="/rag/ingest",
        payload={"doc_id": summary["doc_id"], "chunks": summary["chunks"], "chunk_mode": chunk_mode},
    )
    return summary


@app.post("/rag/query")
async def rag_query(
    payload: RagQueryRequest,
    settings: Settings = Depends(get_settings),
    logger=Depends(get_logger),
):
    try:
        results = await _run_in_threadpool(
            query_rag,
            payload.query,
            top_k=payload.top_k,
            settings=settings,
            retrieval_mode=payload.retrieval_mode,
            doc_ids=payload.doc_ids,
            required_threat_tags=payload.required_threat_tags,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    logger.log(
        route="/rag/query",
        payload={
            "query_hash": hash(payload.query),
            "results": len(results["results"]),
            "retrieval_mode": payload.retrieval_mode,
        },
    )
    return results


@app.get("/vectors/umap")
async def vectors_umap(settings: Settings = Depends(get_settings), logger=Depends(get_logger)):
    projection = await _run_in_threadpool(project_vectors, settings=settings)
    logger.log(route="/vectors/umap", payload={"points": len(projection["points"])})
    return projection


@app.post("/utils/ioc_extract")
async def utils_ioc(payload: IOCRequest, logger=Depends(get_logger)):
    indicators = extract_iocs(payload.text)
    logger.log(route="/utils/ioc_extract", payload={"count": len(indicators)})
    return {"iocs": indicators}


@app.post("/utils/headers")
async def utils_headers(payload: HeaderRequest, logger=Depends(get_logger)):
    entries = parse_email_headers(payload.headers)
    logger.log(route="/utils/headers", payload={"count": len(entries)})
    return {"headers": entries}


@app.post("/utils/log_summary")
async def utils_log_summary(payload: LogSummaryRequest, logger=Depends(get_logger)):
    summary = summarize_logs(payload.text)
    logger.log(route="/utils/log_summary", payload={"lines": summary["lines"]})
    return summary


__all__ = ["app"]
