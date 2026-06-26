from typing import Any

from pydantic import BaseModel, Field


class AgentAskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class AgentSource(BaseModel):
    label: str
    endpoint: str


class AgentResponse(BaseModel):
    question: str
    intent: str
    answer: str
    sources: list[AgentSource]
    data: list[dict[str, Any]] | dict[str, Any] | None = None
    suggestions: list[str] = []
