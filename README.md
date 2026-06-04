# Self-Correcting (CRAG) Study Buddy

A local Retrieval-Augmented Generation (RAG) study assistant with PDF ingestion, Chroma-backed vector search, and a lightweight FastAPI backend.

## What this repo contains

- `src/` - application source code
- `config/` - settings and environment loader
- `db/` - local Chroma persistence directory
- `tests/` - unit tests
- `.env.example` - configuration template
- `requirements.txt` - Python dependencies

## Getting Started

### Run locally

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

The UI will be available at `http://localhost:8501`.

5. Start the React frontend in a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

## Deploy React Frontend to Netlify

This project is configured for Netlify deployment using `netlify.toml`.

1. In the Netlify dashboard, connect your repository.
2. Use the following build settings if needed:
   - Build command: `cd frontend && npm install && npm run build`
   - Publish directory: `frontend/dist`
3. If you want to use Netlify Functions for API routing, keep the `netlify/functions` folder.
4. Deploy the site.

Netlify will build the Vite React app and publish the static site from `frontend/dist`.

## Configuring Gemini 2.5 Flash LLM

This project now supports Google's Gemini 2.5 Flash model for intelligent chunk grading.

### Setup

1. **Get a Gemini API Key:**
   - Visit [Google AI Studio](https://aistudio.google.com/apikey)
   - Create an API key for your project

2. **Configure your environment:**
   - Copy `.env.example` to `.env`:
     ```powershell
     cp .env.example .env
     ```
   - Add your Gemini API key:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```

3. **Install/Update dependencies:**
   ```powershell
   python -m pip install -r requirements.txt
   ```

### How it Works

- **Gemini 2.5 Flash** is used for intelligent chunk grading in the CRAG pipeline
- When a query is received, Gemini evaluates retrieved documents and grades them as `CORRECT`, `AMBIGUOUS`, or `IRRELEVANT`
- If all chunks are relevant, the pipeline generates an answer directly
- If chunks are ambiguous or irrelevant, it falls back to web search before generating
- If no Gemini API key is configured, the system gracefully falls back to a heuristic grading method

### Model Details

- **Model:** `gemini-2.5-flash`
- **Temperature:** 0.7 (balanced creativity and consistency)
- **Use Case:** Chunk relevance grading in RAG pipeline

The React app will be available at `http://localhost:5173`.

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

## Deployment

### Vercel (Recommended for API Backend)

1. Install Vercel CLI:
```powershell
npm install -g vercel
```

2. Deploy from the project root:
```powershell
vercel
```

3. Configure environment variables in the Vercel dashboard:
   - `OPENAI_API_KEY`
   - `TAVILY_API_KEY`
   - `CHROMA_PERSIST_DIRECTORY` (optional)
   - `STUDY_BUDDY_API_URL` if you want Streamlit to call the deployed API directly

4. The backend API will be available at `https://<your-project>.vercel.app/api`
   - `GET /api/health`
   - `POST /api/ingest`
   - `POST /api/chat`

### Netlify (Alternative for API Backend)

1. Install Netlify CLI:
```powershell
npm install -g netlify-cli
```

2. Deploy from the project root:
```powershell
netlify deploy --prod
```

3. Configure environment variables in the Netlify dashboard under **Site settings > Build & deploy > Environment**:
   - `OPENAI_API_KEY`
   - `TAVILY_API_KEY`
   - `CHROMA_PERSIST_DIRECTORY` (optional)

4. The Netlify function is configured at `netlify/functions/api.py` and will serve your FastAPI app via `/api/*`.

### Streamlit UI Deployment

Deploy the Streamlit UI separately to [Streamlit Cloud](https://streamlit.io/cloud):

1. Push your repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io).
3. Click "New app" and connect your GitHub repo.
4. Select your branch and `src/streamlit_app.py` as the main file.
5. Set `STUDY_BUDDY_API_URL` in Streamlit Cloud to your deployed API base URL, for example:
   - `https://<your-project>.vercel.app/api`
   - or `https://<your-netlify-site>.netlify.app/api`

## Notes

- The local Chroma store persists embeddings to `db/chroma`.
- The Streamlit UI submits PDF uploads and chat queries to the API.
- For Vercel/Netlify, configure the API URL in Streamlit settings to point to your deployed backend.
