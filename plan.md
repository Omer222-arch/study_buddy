You are an expert AI Engineer and Cloud Architect specializing in advanced Retrieval-Augmented Generation (RAG) architectures, LangGraph state machines, FastAPI backends, and cloud-native containerized deployments. 

I want to build a "Self-Correcting (CRAG) Study Buddy" application over a 4-week development cycle. We will build this system progressively, module by module. Ensure all code written is production-grade, highly modular, fully typed with Python type hints, asynchronously executed where applicable, and properly documented.

Here is the 4-week architectural roadmap we must strictly follow:

=========================================
WEEK 1: LOCAL INGESTION & BASELINE RAG
=========================================
- Task 1.1: Project workspace initialization. Configure a structured repository (`/src`, `/config`, `/tests`, `.env.example`, `requirements.txt`).
- Task 1.2: PDF Extraction Engine. Implement a reliable chunking service using `PyPDF` combined with LangChain's `RecursiveCharacterTextSplitter` (Target: 500-800 token chunks with a 10% overlap).
- Task 1.3: Local Vector Store Setup. Initialize a local `Chroma` or `FAISS` instance. Implement code to generate vector embeddings using an open-source model via HuggingFace/Ollama or an API, store them locally, and build a basic semantic retrieval loop.

=========================================
WEEK 2: LANGGRAPH & CRAG STATE LOGIC
=========================================
- Task 2.1: GraphState Definition. Create a strict `GraphState` Pydantic class to manage state transitions across the pipeline (tracking: query, retrieved_documents, web_search_context, final_generation, steps_taken).
- Task 2.2: The Grader Node. Write a prompt-engineered LLM evaluator that acts as a binary/ternary judge. It must evaluate each chunk against the user query and output a structured JSON schema classifying the chunk as "CORRECT", "AMBIGUOUS", or "IRRELEVANT". Use Pydantic/Instructor for strict tool-calling.
- Task 2.3: Fallback Search Node. Integrate the Tavily Search API. Write a node that triggers ONLY when chunks are graded "AMBIGUOUS", extracting web context to supplement the system knowledge.
- Task 2.4: State Graph Assembly. Use LangGraph to construct the state machine. Build the conditional edges and routers:
    - If ALL chunks are "CORRECT" -> route straight to the generation node.
    - If ANY chunks are "AMBIGUOUS" -> route to Tavily web-search, then compile context and generate.
    - If ALL chunks are "IRRELEVANT" -> route to an abort node prompting the user to rephrase.
- Task 2.5: Test execution flows completely via terminal logs.

=========================================
WEEK 3: CLOUD MODERNIZATION & BACKEND
=========================================
- Task 3.1: Serverless Vector Index. Migrate ingestion logic from the local vector database to a cloud infrastructure instance utilizing Pinecone Serverless. Ensure metadata routing options are configured cleanly.
- Task 3.2: FastAPI API Wrapper. Wrap the compiled LangGraph orchestration logic inside an asynchronous FastAPI application backend. Expose a `/docs` swagger layout alongside two primary endpoints:
    - POST `/ingest`: Handles multi-part file uploads of target PDFs to seed the database index.
    - POST `/chat`: Streams or returns JSON execution histories containing final answers alongside step telemetry logs.
- Task 3.3: Containerization. Write a highly optimized, multi-stage `Dockerfile` targeting python-slim base images. Implement non-root user execution privileges for maximum cluster deployment security.

=========================================
WEEK 4: DEPLOYMENT & UI FRONTEND
=========================================
- Task 4.1: Cloud Hosting Deployment. Package the system for serverless container engines like AWS Fargate (ECS) or GCP Cloud Run. Secure runtime api keys externally via Cloud Environment Secret Managers.
- Task 4.2: Streamlit Interface. Design a minimal, clean Streamlit chat application UI. Build it to connect smoothly with the deployed FastAPI backend routes. Ensure it clearly displays the inner telemetry stages (e.g., "Evaluating Context...", "Executing Web-Search Fallback...") alongside the final responses.
- Task 4.3: Observability Tracking. Inject explicit tracking configurations to route performance monitoring data instantly into LangSmith for processing latency, evaluation correctness, and tracking real-world runtime costs.

=========================================
INSTRUCTIONS FOR EXECUTION
=========================================
1. Do not generate all code for all 4 weeks at once. 
2. Begin by asking me which specific Week and Task I want to start with.
3. For the selected task, write out the complete, functional python script, configuration file, or architectural step. Explain your design choices briefly, focusing on robustness and edge cases.
4. Always structure environment variables explicitly so secrets are never compromised.

Acknowledge this roadmap and ask me which specific Week and Task to begin generating code for first.