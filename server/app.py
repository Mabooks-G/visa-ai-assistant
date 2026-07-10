"""
Visa AI Assistant — FastAPI Backend
Main application entry point.

Designed to run on AMD Cloud with GPU acceleration for
AI-powered document classification and visa readiness assessment.
"""

import os
import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from server.routes.users import router as users_router
from server.routes.analysis import router as analysis_router

# ── Logging ────────────────────────────────────────────────────

log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── App Initialization ─────────────────────────────────────────

app = FastAPI(
    title="Visa AI Assistant API",
    description="Backend API for AI-powered visa document classification and readiness assessment. Designed for AMD Cloud GPU acceleration.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ───────────────────────────────────────────────────────

cors_origins = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000,https://*.nativelyai.app",
)
allowed_origins = [o.strip() for o in cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ───────────────────────────────────────────

app.include_router(users_router)
app.include_router(analysis_router)


# ── Health Endpoints ──────────────────────────────────────────

@app.get("/health")
def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "Visa AI Assistant API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health/gpu")
def gpu_health():
    """Check GPU availability (for AMD ROCm)."""
    gpu_info = {"available": False, "devices": []}

    try:
        import subprocess
        result = subprocess.run(
            ["rocm-smi", "--showallinfo"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            gpu_info["available"] = True
            gpu_info["devices"] = [line.strip() for line in result.stdout.split("\n") if line.strip()[:5].isdigit()]
            gpu_info["raw_output"] = result.stdout[:1000]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        try:
            import torch
            gpu_info["available"] = torch.cuda.is_available()
            if gpu_info["available"]:
                gpu_info["devices"] = [
                    f"CUDA Device {i}: {torch.cuda.get_device_name(i)}"
                    for i in range(torch.cuda.device_count())
                ]
        except ImportError:
            gpu_info["note"] = "No GPU detection libraries available"

    return gpu_info


@app.get("/health/db")
def db_health():
    """Check Supabase database connectivity."""
    try:
        from server.database.db import get_db
        client = get_db()
        result = client.table("visa_applications").select("count", count="exact").limit(1).execute()
        return {
            "status": "connected",
            "tables": ["visa_applications", "documents", "document_classifications", "users"],
        }
    except Exception as e:
        return {
            "status": "error",
            "detail": str(e),
        }


# ── Error Handlers ─────────────────────────────────────────────

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500},
    )


# ── Startup / Shutdown ─────────────────────────────────────────

@app.on_event("startup")
async def startup():
    logger.info("Visa AI Assistant API starting up...")
    logger.info(f"CORS origins: {allowed_origins}")

    # Check database
    try:
        db_health_result = db_health()
        logger.info(f"Database health: {db_health_result['status']}")
    except Exception as e:
        logger.warning(f"Database not available at startup: {e}")


@app.on_event("shutdown")
async def shutdown():
    logger.info("Visa AI Assistant API shutting down...")


# ── Main Entry ─────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level=log_level.lower(),
    )