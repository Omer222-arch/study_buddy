import sys
import os
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import app as fastapi_app

# Add CORS for Vercel
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Export FastAPI app for ASGI middleware
app = fastapi_app
handler = fastapi_app
