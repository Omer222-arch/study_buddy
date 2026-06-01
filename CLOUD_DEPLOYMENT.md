# Cloud Deployment Guide

This repository is container-ready, so the first cloud deployment step is to publish a Docker image and then deploy it to a container hosting service.

## 1. Publish the Docker image

A GitHub Actions workflow is included in `.github/workflows/docker-publish.yml`.
It builds the app image and pushes it to GitHub Container Registry (GHCR):

- `ghcr.io/<owner>/studybuddy:latest`
- `ghcr.io/<owner>/studybuddy:<commit-sha>`

Make sure your repository has GitHub Actions enabled.

## 2. Cloud hosting options

You can deploy the published container image to any container platform:

- AWS App Runner
- AWS ECS / Fargate
- Google Cloud Run
- Azure App Service / Azure Container Instances
- Railway, Fly.io, or Cloudflare Pages for Containers

### Recommended first target

For a fast start, deploy the image to **GCP Cloud Run**, because it supports container images directly, manages HTTPS, and is easy to automate from GitHub Actions.

## 3. GCP Cloud Run deployment

A GitHub Actions workflow is included at `.github/workflows/gcp-cloud-run.yml`.
It builds the Docker image, pushes it to Google Container Registry, and deploys to Cloud Run.

### Required GitHub secrets

- `GCP_PROJECT_ID`
- `GCP_REGION`
- `CLOUD_RUN_SERVICE_NAME`
- `GCP_SA_KEY` (JSON service account key)

### Service account IAM roles

The service account used by `GCP_SA_KEY` should have at least these roles:

- `roles/run.admin`
- `roles/storage.admin` or `roles/storage.objectAdmin`
- `roles/iam.serviceAccountUser`

### Environment variables for Cloud Run

Set the following variables in Cloud Run or via GitHub Actions deployment:

- `CHROMA_PERSIST_DIRECTORY=/tmp/chroma`
- `CHROMA_COLLECTION_NAME=studybuddy`
- `EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2`
- `EMBEDDING_DEVICE=cpu`

> Note: Cloud Run containers use ephemeral filesystem storage. The local Chroma persistence directory is suitable for prototyping, but not for durable long-term storage. For production, migrate embeddings to a managed cloud vector store or external database.

## 4. Manual Cloud Run deployment

If you prefer to deploy manually from your workstation, install the Google Cloud SDK and run:

```bash
gcloud auth login

gcloud config set project YOUR_PROJECT_ID

gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/studybuddy:latest .
gcloud run deploy YOUR_SERVICE_NAME \
  --image gcr.io/YOUR_PROJECT_ID/studybuddy:latest \
  --region YOUR_REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars CHROMA_PERSIST_DIRECTORY=/tmp/chroma,CHROMA_COLLECTION_NAME=studybuddy,EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2,EMBEDDING_DEVICE=cpu
```

## 5. Next step

Create the GCP service account and add the `GCP_SA_KEY` secret, then push to `main` to trigger deployment.

Store runtime secrets in cloud provider secrets/configuration:

- `CHROMA_PERSIST_DIRECTORY` -> use a writable path inside the container, e.g. `/app/db/chroma`
- `CHROMA_COLLECTION_NAME`
- `EMBEDDING_MODEL_NAME`
- `EMBEDDING_DEVICE`
- `OPENAI_API_KEY`
- `TAVILY_API_KEY`

If you deploy only the API service, the UI can be hosted separately or run locally and point at the API URL.

## 4. Next step

Choose a target cloud provider and I will generate the exact deployment manifest and provider-specific instructions.
