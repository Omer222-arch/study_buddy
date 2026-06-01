import asyncio

from src.grader import GraderNode, MockLLMClient
from src.langgraph_pipeline import CRAGPipeline
from src.tavily_search import MockTavilySearchClient


def test_graph_state_pipeline_generates_with_correct_chunks() -> None:
    grader = GraderNode(MockLLMClient())
    search_client = MockTavilySearchClient()
    pipeline = CRAGPipeline(grader_node=grader, search_client=search_client)

    query = "What is retrieval-augmented generation?"
    chunks = [
        "Retrieval-augmented generation (RAG) is a design pattern that combines retrieval and generation.",
        "This text is not relevant to the user's query.",
    ]

    result = asyncio.run(pipeline.execute(query, chunks))

    assert result.final_generation is not None
    assert "retrieval-augmented generation" in result.final_generation.lower()
    assert "final_generation" in result.steps_taken
