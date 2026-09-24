"""
BHOOMI-X — FastAPI Application Entry Point
AI-Powered Geospatial Reconciliation & Harmonization Platform
SIH 2026 • PS 26013
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

from config import settings
from database import init_db, close_db, async_session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("bhoomix")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # ─── Startup ───
    logger.info("BHOOMI-X API starting up...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Initialize database tables
    await init_db()
    logger.info("Database initialized (PostGIS)")

    # Tables initialized cleanly. Demo data is not seeded on startup.

    # Create upload directory
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    logger.info("BHOOMI-X API ready!")

    yield

    # ─── Shutdown ───
    await close_db()
    logger.info("BHOOMI-X API shut down.")


# ─── Create FastAPI App ───
app = FastAPI(
    title="BHOOMI-X API",
    description=(
        "AI-Powered Geospatial Reconciliation & Harmonization Platform for Urban Land Records. "
        "AI recommends; GIS computes; authorized humans verify."
    ),
    version="1.0.0-prototype",
    lifespan=lifespan,
)

# ─── CORS Middleware ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Mount Routers ───
from routers.parcels import router as parcels_router
from routers.ingestion import router as ingestion_router
from routers.conflicts import router as conflicts_router
from routers.reviews import router as reviews_router
from routers.pipeline import router as pipeline_router
from routers.export import router as export_router

app.include_router(parcels_router)
app.include_router(ingestion_router)
app.include_router(conflicts_router)
app.include_router(reviews_router)
app.include_router(pipeline_router)
app.include_router(export_router)


# ─── Health Check ───
@app.get("/api/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": "BHOOMI-X API",
        "version": "1.0.0-prototype",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "name": "BHOOMI-X",
        "tagline": "AI-Powered Geospatial Reconciliation & Harmonization",
        "docs": "/docs",
        "health": "/api/health",
    }
