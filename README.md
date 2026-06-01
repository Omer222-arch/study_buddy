# Self-Correcting (CRAG) Study Buddy

A local Retrieval-Augmented Generation (RAG) study assistant with PDF ingestion, Chroma-backed vector search, and a lightweight FastAPI backend.

## What this repo contains

- `src/` - application source code
- `config/` - settings and environment loader
- `db/` - local Chroma persistence directory
- `tests/` - unit tests
- `.env.example` - configuration template
- `requirements.txt` - Python dependencies

## Week 3.3 / Week 4 Delivery

This branch adds containerization and a Streamlit UI for local deployment:

- `Dockerfile` - API container definition
- `docker-compose.yml` - API + Streamlit UI orchestration
- `src/streamlit_app.py` - browser-based frontend for ingestion and chat
- `.dockerignore` - excluded files for Docker builds

## Run locally without Docker

1. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

2. Start the API service:

```powershell
python -m src.app
```

3. Browse the API docs:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

4. Start the Streamlit UI:

```powershell
streamlit run src/streamlit_app.py
```

## Run with Docker

### Build the image

```powershell
docker build -t studybuddy:latest .
```

### Run the API container only

```powershell
docker run --rm -p 8000:8000 -v "%cd%/db:/app/db" studybuddy:latest
```

### Run API + UI together

```powershell
docker compose up --build
```

Then open:

- API: `http://localhost:8000`
- Streamlit UI: `http://localhost:8501`

## Cloud Deployment

A cloud deployment workflow is included at `.github/workflows/docker-publish.yml`.
It builds the Docker image and publishes it to GitHub Container Registry (GHCR):

- `ghcr.io/<owner>/studybuddy:latest`
- `ghcr.io/<owner>/studybuddy:<commit-sha>`

For GCP Cloud Run, there is also a dedicated workflow at `.github/workflows/gcp-cloud-run.yml`.
It builds the container image, pushes it to Google Container Registry, and deploys directly to Cloud Run.

See `CLOUD_DEPLOYMENT.md` for the next step, required GCP secrets, and provider-specific guidance.

## Environment

Copy `.env.example` to `.env` to customize settings such as:

- `CHROMA_PERSIST_DIRECTORY`
- `CHROMA_COLLECTION_NAME`
- `EMBEDDING_MODEL_NAME`
- `EMBEDDING_DEVICE`
- `OPENAI_API_KEY`
- `TAVILY_API_KEY`

## API Endpoints

- `GET /health` - readiness check
- `POST /ingest` - upload a PDF file for ingestion
- `POST /chat` - query the ingested documents

## Continuous Integration

A GitHub Actions workflow can be added to validate the Python package and run tests on push or pull request. The workflow should install dependencies, execute the test suite, and build the Docker image to ensure both the service and container artifacts are valid.

## Notes

- The local Chroma store persists embeddings to `db/chroma`.
- The Streamlit UI submits PDF uploads and chat queries to the API.
- Docker Compose launches the API and UI together with shared volume persistence.
