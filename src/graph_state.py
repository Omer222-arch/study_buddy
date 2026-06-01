from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class ChunkGrade(str, Enum):
    CORRECT = "CORRECT"
    AMBIGUOUS = "AMBIGUOUS"
    IRRELEVANT = "IRRELEVANT"


class GradedChunk(BaseModel):
    chunk_id: int
    text: str
    grade: ChunkGrade
    confidence: float = Field(..., ge=0.0, le=1.0)
    explanation: str


class GraphState(BaseModel):
    query: str
    retrieved_documents: List[str] = Field(default_factory=list)
    graded_chunks: List[GradedChunk] = Field(default_factory=list)
    web_search_context: str | None = None
    final_generation: str | None = None
    steps_taken: List[str] = Field(default_factory=list)
    abort_reason: str | None = None

    model_config = ConfigDict(extra="forbid", validate_assignment=True)
