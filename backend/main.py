"""
TRUVEX Platform — Master Backend Application Entry Point.
Phase 1: Minimal FastAPI setup, CORS, static mounting, and health checks.
"""

from datetime import datetime, timezone
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Resolve base directories
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="TRUVEX Platform API",
    description="AI-Powered Universal Trust Infrastructure (B2B2C)",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend static directory if exists
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/", summary="TRUVEX Landing Page", response_class=FileResponse)
async def serve_landing_page():
    """Serves the TRUVEX landing page."""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return JSONResponse(
        content={
            "app": "TRUVEX",
            "message": "Welcome to TRUVEX. Frontend assets are initializing.",
        }
    )


@app.get("/api/health", summary="Health Check Endpoint")
async def health_check():
    """Returns the current operational health of the TRUVEX backend."""
    return {
        "status": "healthy",
        "app": "TRUVEX",
        "version": "0.1.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("TRUVEX_PORT", 8000))
    host = os.getenv("TRUVEX_HOST", "127.0.0.1")
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
