from __future__ import annotations

from typing import Any

from langgraph.graph import StateGraph, START
from langgraph.types import Command

from .graph_state import ChunkGrade, GradedChunk, GraphState
from .grader import GraderNode, MockLLMClient
from .tavily_search import MockTavilySearchClient, SearchClientProtocol, TavilySearchClient


class CRAGPipeline:
    def __init__(
        self,
        grader_node: GraderNode | None = None,
        search_client: SearchClientProtocol | None = None,
    ) -> None:
        self.grader_node = grader_node or GraderNode(MockLLMClient())
        self.search_client = search_client or MockTavilySearchClient()
        self.compiled = self._build_graph()

    def _build_graph(self) -> Any:
        graph = StateGraph(state_schema=GraphState)
        graph.add_node("grade", self._grade_node)
        graph.add_node("fallback_search", self._fallback_search_node)
        graph.add_node("generate", self._generate_node)
        graph.add_node("abort", self._abort_node)

        graph.add_edge(START, "grade")
        graph.set_finish_point("generate")
        graph.set_finish_point("abort")

        return graph.compile()

    async def execute(self, query: str, chunks: list[str]) -> GraphState:
        state = GraphState(query=query, retrieved_documents=chunks)
        result = await self.compiled.ainvoke(state.model_dump())

        if isinstance(result, dict):
            return GraphState(**result)

        return result

    async def _grade_node(self, state: GraphState, runtime: Any) -> Command:
        graded_chunks = await self.grader_node.grade_chunks(state.query, state.retrieved_documents)
        step_label = "graded_chunks"
        next_node = self._get_next_node(graded_chunks)

        return Command(
            goto=next_node,
            update={
                "graded_chunks": [chunk.model_dump() for chunk in graded_chunks],
                "steps_taken": [*state.steps_taken, step_label],
            },
        )

    async def _fallback_search_node(self, state: GraphState, runtime: Any) -> Command:
        if not any(chunk.grade == ChunkGrade.AMBIGUOUS for chunk in state.graded_chunks):
            return Command(goto="abort", update={"steps_taken": [*state.steps_taken, "fallback_skipped"]})

        search_context = await self.search_client.search(state.query)
        step_label = "tavily_web_search"

        return Command(
            goto="generate",
            update={
                "web_search_context": search_context,
                "steps_taken": [*state.steps_taken, step_label],
            },
        )

    async def _generate_node(self, state: GraphState, runtime: Any) -> dict[str, Any]:
        answer = self._compose_answer(state)
        return {
            "final_generation": answer,
            "steps_taken": [*state.steps_taken, "final_generation"],
        }

    async def _abort_node(self, state: GraphState, runtime: Any) -> dict[str, Any]:
        return {
            "abort_reason": (
                "The available content is insufficient or irrelevant. "
                "Please rephrase your question with more specific details."
            ),
            "steps_taken": [*state.steps_taken, "abort"],
        }

    @staticmethod
    def _get_next_node(graded_chunks: list[ChunkGrade | GradedChunk]) -> str:
        grades = [chunk.grade if isinstance(chunk, GradedChunk) else chunk for chunk in graded_chunks]
        if all(grade == ChunkGrade.CORRECT for grade in grades) and grades:
            return "generate"
        if any(grade == ChunkGrade.AMBIGUOUS for grade in grades):
            return "fallback_search"
        return "abort"

    @staticmethod
    def _compose_answer(state: GraphState) -> str:
        if state.final_generation:
            return state.final_generation

        relevant = [chunk.text for chunk in state.graded_chunks if chunk.grade == ChunkGrade.CORRECT]
        if not relevant and state.web_search_context:
            return (
                "I could not confirm a reliable answer from the local chunks, "
                "but I found this external context: "
                + state.web_search_context
            )
        if not relevant:
            return (
                "I could not reliably answer the query from the available content. "
                "Please provide a clearer question or different source material."
            )

        details = "\n\n".join(relevant[:3])
        return (
            "Based on the verified chunks, this is the best answer I can provide:\n\n"
            f"{details}\n\n"
            "If you want more detail, refine the query and run the pipeline again."
        )
