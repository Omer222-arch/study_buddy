from __future__ import annotations

import asyncio
import json
from typing import Protocol, Sequence

from pydantic import BaseModel, Field, ValidationError

from .graph_state import ChunkGrade, GradedChunk


class LLMClientProtocol(Protocol):
    async def generate(self, prompt: str) -> str:
        ...


class MockLLMClient:
    async def generate(self, prompt: str) -> str:
        await asyncio.sleep(0)
        # A lightweight placeholder that mimics a structured JSON response.
        return prompt


class GradeResponse(BaseModel):
    graded_chunks: list[GradedChunk]
    reasoning: str


class GraderNode:
    def __init__(self, llm_client: LLMClientProtocol | None = None) -> None:
        self.llm_client = llm_client or MockLLMClient()

    async def grade_chunks(self, query: str, chunks: Sequence[str]) -> list[GradedChunk]:
        prompt = self._build_prompt(query, chunks)
        raw_response = await self.llm_client.generate(prompt)

        try:
            response = GradeResponse.model_validate_json(raw_response)
            return response.graded_chunks
        except (ValidationError, ValueError):
            return self._heuristic_grade(query, chunks)

    def _build_prompt(self, query: str, chunks: Sequence[str]) -> str:
        return json.dumps(
            {
                "instruction": (
                    "Evaluate each chunk for the user query. "
                    "Return a JSON payload with `graded_chunks` and `reasoning`. "
                    "Each graded chunk must include `chunk_id`, `text`, `grade`, "
                    "`confidence`, and `explanation`."
                ),
                "query": query,
                "chunks": [
                    {"chunk_id": idx + 1, "text": text}
                    for idx, text in enumerate(chunks)
                ],
                "schema": {
                    "graded_chunks": [
                        {
                            "chunk_id": "integer",
                            "text": "string",
                            "grade": "CORRECT|AMBIGUOUS|IRRELEVANT",
                            "confidence": "number",
                            "explanation": "string",
                        }
                    ],
                    "reasoning": "string",
                },
            },
            indent=2,
        )

    def _heuristic_grade(self, query: str, chunks: Sequence[str]) -> list[GradedChunk]:
        query_terms = {token.strip().lower() for token in query.split() if token.strip()}
        graded_chunks: list[GradedChunk] = []

        for idx, chunk in enumerate(chunks, start=1):
            text_lower = chunk.lower()
            match_count = sum(1 for term in query_terms if term and term in text_lower)
            grade = (
                ChunkGrade.CORRECT
                if match_count >= max(1, len(query_terms) // 2)
                else ChunkGrade.AMBIGUOUS
                if match_count >= 1
                else ChunkGrade.IRRELEVANT
            )

            confidence = min(1.0, 0.25 + 0.25 * match_count)
            explanation = (
                "The chunk contains many query keywords and appears relevant."
                if grade == ChunkGrade.CORRECT
                else (
                    "The chunk contains some query keywords but lacks enough detail."
                    if grade == ChunkGrade.AMBIGUOUS
                    else "The chunk appears unrelated to the query."
                )
            )

            graded_chunks.append(
                GradedChunk(
                    chunk_id=idx,
                    text=chunk,
                    grade=grade,
                    confidence=confidence,
                    explanation=explanation,
                )
            )

        return graded_chunks
