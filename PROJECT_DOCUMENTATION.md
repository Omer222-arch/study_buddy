# CRAG Study Buddy - Project Documentation

## Overview

CRAG Study Buddy is a local Retrieval-Augmented Generation (RAG) study assistant that ingests PDF documents, stores embeddings in a Chroma vector database, and answers questions using retrieved chunks plus a lightweight reasoning pipeline.

The repository contains:
- `src/` - Python backend and service implementation
- `config/` - environment and settings loader
- `db/` - Chroma persistence storage
- `frontend/` - React client code and frontend integration
- `netlify/` - Netlify function wrapper for deployment
- `api/` - Vercel-compatible FastAPI wrapper
- `tests/` - unit tests
- `README.md` - quick start and endpoint summary
- `DEPLOYMENT_GUIDE.md` - deployment guidance

---

## Architecture

The application has two main execution surfaces:

1. **Python FastAPI backend** (`src/`) that exposes API endpoints for ingestion and chat.
2. **UI clients**:
   - React frontend in `frontend/`
   - Streamlit UI in `src/streamlit_app.py`

The backend is deployable via:
- Vercel using `api/index.py`
- Netlify using `netlify/functions/api.py`

The service flow is:
1. PDF upload
2. Extract text and chunk it
3. Store chunks into a Chroma vector database
4. Search the vector store for relevant chunks
5. Grade chunks and optionally fallback to external search
6. Generate an answer from relevant content

---

## Backend services and modules

### `src/app.py`

This is the FastAPI application entrypoint.
- Uses `FastAPI` and `CORSMiddleware`.
- Defines endpoint schemas with Pydantic models.
- Builds the `StudyBuddyService` in an async lifespan event.
- Serves:
  - `GET /health`
  - `POST /ingest`
  - `POST /chat`
  - `GET /openapi.json`

It can run locally with `uvicorn` or as a deployed serverless app.

### `src/services.py`

Core service orchestration layer.
- `StudyBuddyService` initializes:
  - `PDFIngestionEngine`
  - `ChromaVectorStore`
  - `CRAGPipeline`
- `ingest_file`:
  - reads an uploaded PDF
  - writes it to a temporary file
  - ingests it into text chunks
  - stores chunks into Chroma with metadata
- `chat`:
  - searches the vector store
  - executes the reasoning pipeline
  - returns answer and retrieved documents
- `reset_store` can recreate the vector store instance.

### `src/vector_store.py`

Chroma-backed vector database wrapper.
- Uses `chromadb.PersistentClient` for local persistence.
- Embeddings are generated with `SentenceTransformerEmbeddingFunction`.
- `add_documents` inserts chunks with generated UUIDs and optional metadata.
- `search` queries by text and returns matched document chunks.

### `src/ingest.py`

PDF ingestion engine.
- Uses `PdfReader` from `pypdf`.
- Extracts raw text from each page.
- Splits text into chunks using `RecursiveCharacterTextSplitter` from `langchain_text_splitters`.
- Default chunk size is 750 characters with 75 characters overlap.

### `src/langgraph_pipeline.py`

The reasoning pipeline.
- Implements a graph-based workflow using `langgraph`.
- Creates nodes:
  - `grade`
  - `fallback_search`
  - `generate`
  - `abort`
- Workflow logic:
  - Grade retrieved chunks.
  - If any chunk is `AMBIGUOUS`, optionally perform fallback search.
  - If enough chunks are `CORRECT`, generate an answer.
  - Otherwise, abort with a reason.
- Produces a `GraphState` object containing:
  - query
  - retrieved documents
  - graded chunks
  - web search context
  - answer or abort reason
  - steps taken.

### `src/graph_state.py`

Defines the state model for the pipeline.
- `ChunkGrade` enum: `CORRECT`, `AMBIGUOUS`, `IRRELEVANT`.
- `GradedChunk` Pydantic model: `chunk_id`, `text`, `grade`, `confidence`, `explanation`.
- `GraphState` Pydantic model: pipeline state container.

### `src/grader.py`

Chunk grading logic.
- `MockLLMClient` returns the prompt text immediately; it is a placeholder.
- `GraderNode` attempts to parse a structured JSON response from the client.
- If parsing fails, it falls back to a heuristic grader.
- Heuristic grading:
  - counts query token matches in each chunk
  - assigns `CORRECT`, `AMBIGUOUS`, or `IRRELEVANT`
  - computes a confidence score
  - returns human-readable explanations.

### `src/tavily_search.py`

External search fallback client.
- `MockTavilySearchClient` returns static mock text.
- `TavilySearchClient` sends a POST request to `https://api.tavily.ai/search`.
- Uses `TAVILY_API_KEY` from settings.
- Extracts `context` or `results` from the API response.

### `config/settings.py`

Application settings loader.
- Loads environment variables from `.env`.
- Settings include:
  - `project_root`
  - `chroma_persist_directory`
  - `chroma_collection_name`
  - `embedding_model_name`
  - `embedding_device`
  - `openai_api_key`
  - `tavily_api_key`
  - `pinecone_api_key`
  - `pinecone_environment`

Defaults are set to local paths and CPU embedding.

---

## API endpoints

### `GET /health`

- Purpose: basic readiness and health check.
- Response:
  - `status`: `ok`
  - `project_root`: configured project root path

### `POST /ingest`

- Purpose: ingest a PDF into the vector database.
- Request: multipart form-data with `file` set to a PDF.
- Validation: only accepts files ending in `.pdf`.
- Response model: `IngestResponse`
  - `file_name`: uploaded file name
  - `ingested_chunks`: number of text chunks created
  - `inserted_ids`: list of persisted vector IDs
- Backend flow:
  - temporary file creation
  - text extraction and chunking
  - indexing into Chroma

### `POST /chat`

- Purpose: answer a text query using ingested content.
- Request JSON:
  - `query`: string
  - `top_k` (optional): number of returned chunks, default `4`
- Response model: `ChatResponse`
  - `query`
  - `answer`
  - `retrieved_documents`
  - `steps_taken`
- Backend flow:
  - semantic search in Chroma
  - grade retrieved chunks
  - optionally perform fallback web search when ambiguous
  - generate an answer or abort reason

### `GET /openapi.json`

- Serves the OpenAPI schema for documentation and client generation.

---

## Deployment wrappers

### `api/index.py`

Used for Vercel deployment.
- Imports `src.app.app`.
- Adds permissive CORS headers for serverless usage.
- Exports `app` for Vercel Python functions.

### `netlify/functions/api.py`

Used for Netlify deployment.
- Imports `Mangum` to wrap the FastAPI app.
- Exports `handler` for Netlify Functions.

### `netlify.toml`

Netlify config details:
- installs requirements with `pip install -r requirements.txt`
- serves functions from `netlify/functions`
- rewrites `/api/*` to the Netlify function wrapper
- publishes the repository root

### `vercel.json`

Vercel config details:
- installs requirements
- uses Python 3.12 runtime for API functions
- rewrites `/api/(.*)` to the same destination
- excludes build artifacts, database files, and markdown from the function bundle

---

## Frontend and UI clients

### `frontend/src/api.ts`

Browser API helper.
- `apiBaseUrl` uses `VITE_API_BASE_URL` if set; otherwise defaults to `/api`.
- `ingestPdf(file)` sends a `POST /ingest` request with multipart form data.
- `askChat(query, top_k)` sends a `POST /chat` JSON request.
- Exposes TypeScript interfaces for API responses.

### `frontend/src/App.tsx`

React application UI.
- Provides file upload and ingestion controls.
- Provides query input and top-K selection.
- Displays ingestion results and chat answers.
- Uses state hooks for loading, error, file selection, and backend results.
- Shows status, retrieved chunks, and pipeline steps.
- Designed as a single-page interface.

### `src/streamlit_app.py`

Streamlit application.
- Uses `requests` to call the backend API.
- Reads `STUDY_BUDDY_API_URL` from environment or defaults to local `http://127.0.0.1:8000`.
- Allows PDF upload and ingestion.
- Displays ingestion results and returned chat answers in Streamlit widgets.
- Mirrors the same `/ingest` and `/chat` API contract.

---

## Supporting files

### `requirements.txt`

Contains Python dependency declarations for:
- FastAPI
- uvicorn
- chromadb
- pydantic-settings
- pypdf
- langchain-text-splitters
- httpx
- streamlit
- mangum
- any other packages required by the backend and deployment wrappers

### `README.md`

Contains quick start instructions, environment notes, API endpoint summary, and deployment hints.

### `DEPLOYMENT_GUIDE.md`

Presumably contains more detailed deployment guidance for Vercel/Netlify/Streamlit Cloud.

### `plan.md`

Project planning notes and roadmap items.

---

## File-by-file summary

### Root and top-level files
- `README.md`: quick start and high-level project description.
- `DEPLOYMENT_GUIDE.md`: deployment instructions and notes.
- `requirements.txt`: Python dependencies.
- `netlify.toml`: Netlify dev/build configuration and redirects.
- `vercel.json`: Vercel build and function configuration.
- `plan.md`: project planning notes.

### Backend entrypoints
- `src/app.py`: FastAPI app, endpoint definitions, service initialization.
- `api/index.py`: Vercel wrapper for `src.app`.
- `netlify/functions/api.py`: Netlify wrapper with `Mangum`.

### Backend services
- `src/services.py`: orchestrates ingestion, vector storage, and pipeline.
- `src/vector_store.py`: manages Chroma persistence and search.
- `src/ingest.py`: extracts and chunks PDF text.
- `src/langgraph_pipeline.py`: controls the state graph and answer generation.
- `src/graph_state.py`: defines state and graded chunk schema.
- `src/grader.py`: grades chunk relevance with a mock LLM and heuristics.
- `src/tavily_search.py`: optional fallback external search provider.
- `config/settings.py`: configuration loader from environment.

### Frontend
- `frontend/package.json`: React project dependencies and scripts.
- `frontend/tsconfig.json`: TypeScript configuration.
- `frontend/vite.config.ts`: Vite build config.
- `frontend/src/api.ts`: frontend API client.
- `frontend/src/App.tsx`: React UI application.
- `frontend/src/main.tsx`: React app bootstrap.
- `frontend/src/styles.css`: frontend styling.
- `frontend/index.html`: main HTML entry.

### Tests
- `tests/test_api.py`: tests the API behavior.
- `tests/test_ingestion.py`: tests PDF ingestion behavior.
- `tests/test_vector_store.py`: tests vector store insertion/search.
- `tests/test_week2_pipeline.py`: tests the pipeline logic.

---

## How to run locally

1. Install Python dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
2. Start the backend:
   ```powershell
   python -m src.app
   ```
3. Open FastAPI docs at:
   - `http://127.0.0.1:8000/docs`
   - `http://127.0.0.1:8000/redoc`
4. Start Streamlit UI:
   ```powershell
   streamlit run src/streamlit_app.py
   ```
5. Start the React frontend:
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

---

## Environment variables

Key environment variables:
- `CHROMA_PERSIST_DIRECTORY`: directory where Chroma stores vectors.
- `CHROMA_COLLECTION_NAME`: Chroma collection name.
- `EMBEDDING_MODEL_NAME`: embedding model name for SentenceTransformers.
- `EMBEDDING_DEVICE`: embedding device, such as `cpu`.
- `OPENAI_API_KEY`: optional LLM API key if extended functionality is added.
- `TAVILY_API_KEY`: required for `TavilySearchClient` fallback search.
- `STUDY_BUDDY_API_URL`: used by Streamlit UI to point to the backend.

---

## Notes and behavior

- The project currently uses a mock LLM client in `src/grader.py`, so chunk grading is deterministic and local.
- The external fallback search is also mocked unless `TAVILY_API_KEY` is provided and `TavilySearchClient` is used.
- Search results from the vector store are returned as raw text chunks.
- The `CRAGPipeline` only generates an answer if there are at least some chunks graded as `CORRECT` or if fallback search provides external context.
- The React frontend expects the backend API to be reachable at `/api` by default.

---

## Recommended next steps

- Add real LLM integration for chunk grading and answer generation.
- Add authentication if public deployment is needed.
- Add PDF metadata extraction and chunk source references.
- Add a dedicated admin endpoint to clear or inspect the Chroma store.
