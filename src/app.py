from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config.settings import settings
from src.services import StudyBuddyService


class IngestResponse(BaseModel):
    file_name: str
    ingested_chunks: int
    inserted_ids: list[str]


class ChatRequest(BaseModel):
    query: str
    top_k: int = 4


class ChatResponse(BaseModel):
    query: str
    answer: str
    retrieved_documents: list[str]
    steps_taken: list[str]


@asynccontextmanager
async def lifespan(app: FastAPI):
    global service
    service = StudyBuddyService()
    yield


app = FastAPI(
    title="CRAG Study Buddy API",
    description="A local Study Buddy backend that ingests PDFs, builds a Chroma vector store, and answers queries via a lightweight RAG pipeline.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service: StudyBuddyService | None = None


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "project_root": str(settings.project_root)}


@app.post("/ingest", response_model=IngestResponse)
async def ingest_pdf(file: UploadFile = File(...)) -> Any:
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported.")

    assert service is not None
    return await service.ingest_file(file)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> Any:
    assert service is not None
    return await service.chat(request.query, request.top_k)


@app.get("/openapi.json")
async def openapi_schema() -> Any:
    return app.openapi()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)
