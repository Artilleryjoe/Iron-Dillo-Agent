"""Data models shared across the Iron Dillo Cybersecurity Buddy."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class ToolCall(BaseModel):
    """Representation of a tool invocation request."""

    name: str = Field(..., min_length=1, description="Name of the tool to execute")
    arguments: Dict[str, Any] = Field(default_factory=dict)

    @validator("name")
    def _normalize_name(cls, value: str) -> str:
        return value.strip()


class AgentTurn(BaseModel):
    """Single turn of interaction between the operator and the assistant."""

    prompt: str = Field(..., description="User supplied question or instruction")
    audience: str = Field(
        "small_businesses",
        description="Persona targeted by the response; used for routing to tools.",
    )
    include_fact: bool = Field(
        True,
        description="Whether to append an armadillo fact to lighten the briefing.",
    )


class AgentResponse(BaseModel):
    """Final agent output including optional tool calls."""

    message: str
    fact: Optional[str] = None
    tool_calls: List[ToolCall] = Field(default_factory=list)


__all__ = ["ToolCall", "AgentTurn", "AgentResponse"]
