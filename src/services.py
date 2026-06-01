from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from fastapi import UploadFile

from config.settings import settings
from src.graph_state import GraphState
from src.ingest import PDFIngestionEngine
from src.langgraph_pipeline import CRAGPipeline
from src.vector_store import ChromaVectorStore


class StudyBuddyService:
    def __init__(self) -> None:
        self.ingester = PDFIngestionEngine()
        self.vector_store = ChromaVectorStore(
            collection_name=settings.chroma_collection_name,
            persist_directory=settings.chroma_persist_directory,
            model_name=settings.embedding_model_name,
            device=settings.embedding_device,
        )
        self.pipeline = CRAGPipeline()

    async def ingest_file(self, file: UploadFile) -> dict[str, Any]:
        content = await file.read()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / file.filename
            temp_path.write_bytes(content)
            chunks = self.ingester.ingest_pdf(temp_path)

        metadatas = [
            {"source": file.filename, "chunk_index": str(idx + 1)}
            for idx in range(len(chunks))
        ]
        ids = self.vector_store.add_documents(chunks, metadatas=metadatas)

        return {
            "file_name": file.filename,
            "ingested_chunks": len(chunks),
            "inserted_ids": ids,
        }

    async def chat(self, query: str, top_k: int = 4) -> dict[str, Any]:
        retrieved = self.vector_store.search(query, n_results=top_k)
        if not retrieved:
            return {
                "query": query,
                "answer": "No relevant documents were found for your query.",
                "retrieved_documents": [],
                "steps_taken": ["no_documents_found"],
            }

        state = await self.pipeline.execute(query, retrieved)

        answer = state.final_generation or state.abort_reason or "Unable to generate an answer."
        return {
            "query": query,
            "answer": answer,
            "retrieved_documents": retrieved,
            "steps_taken": state.steps_taken,
        }

    def reset_store(self) -> None:
        self.vector_store = ChromaVectorStore(
            collection_name=settings.chroma_collection_name,
            persist_directory=settings.chroma_persist_directory,
            model_name=settings.embedding_model_name,
            device=settings.embedding_device,
        )
