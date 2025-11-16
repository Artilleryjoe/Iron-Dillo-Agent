"""Lightweight helpers for modern LLM interactions."""

from __future__ import annotations

import importlib
import importlib.util
from dataclasses import dataclass

from .cli import build_security_brief

__all__ = ["LLMError", "LLMResult", "ModernLLMInterface"]


class LLMError(RuntimeError):
    """Raised when the local LLM bridge cannot produce a response."""


@dataclass
class LLMResult:
    """Structured payload describing an LLM response."""

    response: str
    provider: str


class ModernLLMInterface:
    """Provide a modern local-first LLM experience with graceful fallbacks."""

    def __init__(self, model: str = "llama3", system_prompt: str | None = None) -> None:
        self.model = model
        self.system_prompt = system_prompt
        self._ollama_module = None
        self._module_checked = False

    def _load_module(self):
        if not self._module_checked:
            spec = importlib.util.find_spec("ollama")
            if spec is not None:
                self._ollama_module = importlib.import_module("ollama")
            self._module_checked = True
        return self._ollama_module

    def generate(self, prompt: str, *, system_prompt: str | None = None) -> LLMResult:
        """Generate content either via Ollama or a deterministic fallback."""

        cleaned_prompt = prompt.strip()
        if not cleaned_prompt:
            raise LLMError("Prompt must not be empty.")

        module = self._load_module()
        combined_prompt = system_prompt or self.system_prompt
        if module is None:
            return LLMResult(
                response=self._fallback_response(cleaned_prompt),
                provider="heuristic-brief",
            )

        kwargs = {"model": self.model, "prompt": cleaned_prompt}
        if combined_prompt:
            kwargs["system"] = combined_prompt

        try:
            result = module.generate(**kwargs)
        except Exception as exc:  # pragma: no cover - exercised in real deployments
            raise LLMError(f"Failed to invoke Ollama: {exc}") from exc

        if isinstance(result, dict):
            response_text = (
                result.get("response")
                or result.get("message")
                or result.get("content")
                or str(result)
            )
        else:
            response_text = str(result)
        return LLMResult(response=response_text, provider=f"ollama:{self.model}")

    @staticmethod
    def _fallback_response(prompt: str) -> str:
        """Return a structured briefing when no LLM backend is available."""

        briefing = build_security_brief(
            prompt=prompt,
            audience="small_businesses",
            topic="identity",
            include_fact=False,
        )
        return (
            "Local LLM backend unavailable. Provided structured response instead.\n\n"
            f"{briefing.message}"
        )
