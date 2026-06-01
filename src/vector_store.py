from __future__ import annotations

from pathlib import Path
from typing import Optional
from uuid import uuid4

import chromadb
from chromadb.api.types import EmbeddingFunction
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


class ChromaVectorStore:
    """A local Chroma-backed vector store using SentenceTransformers."""

    def __init__(
        self,
        collection_name: str = "studybuddy",
        persist_directory: Path | str | None = None,
        model_name: str = "all-MiniLM-L6-v2",
        device: str = "cpu",
        embedding_function: Optional[EmbeddingFunction] = None,
    ) -> None:
        self.persist_directory = Path(persist_directory or Path("./db/chroma")).expanduser().resolve()
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=str(self.persist_directory))
        self.embedding_function = embedding_function or SentenceTransformerEmbeddingFunction(
            model_name=model_name,
            device=device,
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
        )

    def add_documents(
        self,
        documents: list[str],
        metadatas: list[dict[str, str]] | None = None,
    ) -> list[str]:
        ids = [str(uuid4()) for _ in documents]
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )
        return ids

    def search(self, query: str, n_results: int = 4) -> list[str]:
        query_result = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "metadatas"],
        )

        if not query_result or not query_result.get("documents"):
            return []

        return [doc for doc in query_result["documents"][0] if doc is not None]
