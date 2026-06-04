# Netlify & Vercel Deployment Guide

This project is configured to deploy on both **Netlify** and **Vercel** for the FastAPI backend, with the Streamlit UI deployed separately.

## Architecture

- **Backend (FastAPI)**: Deployed as serverless functions on Netlify or Vercel
- **Frontend (Streamlit UI)**: Deployed to Streamlit Cloud
- **Vector Database (Chroma)**: Local or managed persistence (optional: upgrade to cloud Chroma)

## Vercel Deployment (Recommended)

Vercel has excellent Python support and seamless GitHub integration.

### Prerequisites

- GitHub account with repo access
- Vercel account (https://vercel.com)
- Vercel CLI installed:
  ```powershell
  npm install -g vercel
  ```

### Setup Steps

1. **Push to GitHub** (if not already):
   ```powershell
   git push origin main
   ```

2. **Deploy with Vercel CLI** (from project root):
   ```powershell
   vercel
   ```
   - Select your project name
   - Framework: choose "Other" or "FastAPI"
   - Root directory: `.`

3. **Configure Environment Variables**:
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Select your project
   - Settings → Environment Variables
   - Add:
     ```
     OPENAI_API_KEY=your_key_here
     TAVILY_API_KEY=your_key_here
     ```

4. **Auto-Deploy from GitHub** (optional):
   - Vercel will automatically deploy on push if you connect your GitHub repo
   - In Vercel dashboard → Import Git Repository

### Testing the Deployment

- API health check: `https://your-project.vercel.app/health`
- API docs: `https://your-project.vercel.app/docs`
- API root: `https://your-project.vercel.app/`

---

## Netlify Deployment

Netlify also supports Python and serverless functions through their runtime.

### Prerequisites

- GitHub account
- Netlify account (https://netlify.com)
- Netlify CLI installed:
  ```powershell
  npm install -g netlify-cli
  ```

### Setup Steps

1. **Deploy with Netlify CLI**:
   ```powershell
   netlify deploy --prod
   ```

2. **Link to Git** (optional):
   ```powershell
   netlify link
   ```
   Then connect your GitHub repo for auto-deployments.

3. **Configure Environment Variables**:
   - Site Settings → Build & Deploy → Environment
   - Add:
     ```
     OPENAI_API_KEY=your_key_here
     TAVILY_API_KEY=your_key_here
     ```

### Testing the Deployment

- API check: `https://your-site.netlify.app/`
- Functions: `https://your-site.netlify.app/.netlify/functions/api`

---

## Streamlit Cloud Deployment

Deploy the Streamlit UI separately for the best experience.

### Steps

1. **Ensure repo is on GitHub** with `src/streamlit_app.py`

2. **Go to** [share.streamlit.io](https://share.streamlit.io)

3. **Click "New app"**:
   - GitHub repo
   - Branch: `main`
   - Main file path: `src/streamlit_app.py`

4. **Configure in Streamlit Settings**:
   - Set the API URL environment variable to point to your Vercel/Netlify backend:
     ```
     STUDY_BUDDY_API_URL=https://your-backend.vercel.app
     ```

### Running Locally

```powershell
streamlit run src/streamlit_app.py
```

---

## Troubleshooting

### Cold Start Issues

- Serverless functions may have initial delay (~5-10s)
- Subsequent calls are faster
- For production, consider upgrading to Vercel Pro or Netlify Pro for faster cold starts

### Environment Variables Not Loading

- Ensure variables are set in platform dashboard (not committed to `.env` file)
- Redeploy after adding variables

### Database Persistence

- Current setup uses local Chroma persistence (lost on redeployment)
- For production, migrate to managed Chroma Cloud or PostgreSQL vector store
- Update `src/vector_store.py` to use cloud service

### CORS Errors

- Both platforms have CORS middleware configured in `/netlify/functions/api.py` and `/api/__init__.py`
- Adjust `allow_origins` if needed for production

---

## Comparison

| Feature | Vercel | Netlify |
|---------|--------|---------|
| Python Support | ✅ Excellent | ✅ Good |
| Cold Start | ⚡ Fast | ⚡ Fast |
| Cost (free tier) | ✅ $0 | ✅ $0 |
| GitHub Integration | ✅ Seamless | ✅ Seamless |
| Analytics | ✅ Built-in | ✅ Built-in |

**Recommendation**: Start with **Vercel** for the best Python FastAPI support.

---

## Next Steps

1. Add authentication (JWT tokens, API keys)
2. Migrate to persistent cloud database (Supabase, Planet Scale, etc.)
3. Set up CI/CD for automated testing before deploy
4. Monitor performance and logs in platform dashboard
