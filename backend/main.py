"""
TRUVEX Platform — Master Backend Application Entry Point.
Phase 2: Full-Stack Trust Infrastructure, AI Integration, Database Persistence, and Static UI Delivery.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Load environment configuration
load_dotenv()

from backend.database import init_db
from backend.routes import admin, auth, companies, employees, verification

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes SQLite database and seeds default demonstration records."""
    init_db()
    yield


app = FastAPI(
    title="TRUVEX Platform API",
    description="AI-Powered Universal Trust Infrastructure (CMRIT × DetectifAI Hackathon Track 03)",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers under /api
app.include_router(auth.router, prefix="/api")
app.include_router(companies.router, prefix="/api")
app.include_router(employees.router, prefix="/api")
app.include_router(verification.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

# Mount Static Files
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


# Direct Frontend Page Routes for Clean Navigation
@app.get("/", summary="Landing Page", response_class=FileResponse)
async def serve_index():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/login", summary="Login Portal", response_class=FileResponse)
async def serve_login():
    return FileResponse(FRONTEND_DIR / "login.html")


@app.get("/employee", summary="Employee Communication Console", response_class=FileResponse)
async def serve_employee():
    return FileResponse(FRONTEND_DIR / "employee.html")


@app.get("/customer", summary="Customer Verification Portal", response_class=FileResponse)
async def serve_customer():
    return FileResponse(FRONTEND_DIR / "customer.html")


@app.get("/enterprise", summary="Enterprise Administration", response_class=FileResponse)
async def serve_enterprise():
    return FileResponse(FRONTEND_DIR / "enterprise.html")


@app.get("/admin", summary="Platform Superadmin Panel", response_class=FileResponse)
async def serve_admin():
    return FileResponse(FRONTEND_DIR / "admin.html")


@app.get("/api/health", summary="Health Check Endpoint")
async def health_check():
    """Returns the operational health and DetectifAI configuration state."""
    detectif_key = os.getenv("DETECTIF_API_KEY", "")
    has_key = bool(detectif_key and not detectif_key.startswith("dtf_live_your_"))
    mock_fallback = os.getenv("DETECTIF_MOCK_FALLBACK", "True").lower() == "true"

    return {
        "status": "healthy",
        "app": "TRUVEX",
        "version": "0.2.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "database": "sqlite_connected",
        "detectif_configured": has_key,
        "detectif_mock_fallback": mock_fallback,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("TRUVEX_PORT", 8000))
    host = os.getenv("TRUVEX_HOST", "127.0.0.1")
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
