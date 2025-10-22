"""Lazy dependency helpers for the Cybersandbox API."""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import List, Sequence

from .settings import Settings, get_settings


@dataclass
class OllamaResponse:
    """Structured result returned by the Ollama helper."""

    response: str


class OllamaClient:
    """Thin wrapper around the optional ``ollama`` Python package."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._module = None

    def _load_module(self):
        if self._module is None:
            module = importlib.util.find_spec("ollama")
            if module is None:
                raise RuntimeError(
                    "The ollama Python package is not installed. Install it to enable LLM calls."
                )
            self._module = importlib.import_module("ollama")
        return self._module

    def generate(self, prompt: str, *, system_prompt: str | None = None) -> OllamaResponse:
        """Generate a completion using the configured local model."""

        module = self._load_module()
        kwargs = {"model": self.settings.model, "prompt": prompt}
        if system_prompt:
            kwargs["system"] = system_prompt
        result = module.generate(**kwargs)
        if isinstance(result, dict) and "response" in result:
            content = result["response"]
        else:
            content = str(result)
        return OllamaResponse(response=content)


class EmbeddingClient:
    """Wrapper that lazily loads a sentence-transformer model."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._model = None

    def _ensure_model(self):
        if self._model is None:
            package_spec = importlib.util.find_spec("sentence_transformers")
            if package_spec is None:
                raise RuntimeError(
                    "sentence-transformers is not installed. Install it to compute embeddings."
                )
            sentence_transformers = importlib.import_module("sentence_transformers")
            self._model = sentence_transformers.SentenceTransformer(self.model_name)
        return self._model

    def embed(self, texts: Sequence[str]) -> List[List[float]]:
        model = self._ensure_model()
        vectors = model.encode(list(texts), convert_to_numpy=False, normalize_embeddings=True)
        return [list(map(float, vector)) for vector in vectors]


def get_ollama_client(settings: Settings | None = None) -> OllamaClient:
    """Return an Ollama client bound to the provided settings."""

    settings = settings or get_settings()
    return OllamaClient(settings)


def get_embedding_client(settings: Settings | None = None) -> EmbeddingClient:
    """Return an embedding client configured by settings."""

    settings = settings or get_settings()
    return EmbeddingClient(settings.embedding_model)


__all__ = [
    "EmbeddingClient",
    "OllamaClient",
    "OllamaResponse",
    "get_embedding_client",
    "get_ollama_client",
]
