"""
Pipeline API Router.
Execute and monitor the harmonization pipeline.
"""

from fastapi import APIRouter
from schemas.pipeline import PipelineStatus
from services.pipeline_service import run_pipeline, get_pipeline_status, reset_pipeline

router = APIRouter(prefix="/api/pipeline", tags=["Pipeline"])


@router.get("/status", response_model=PipelineStatus)
async def pipeline_status():
    """Get current pipeline status and step details."""
    return get_pipeline_status()


@router.post("/run", response_model=PipelineStatus)
async def execute_pipeline():
    """Execute the full harmonization pipeline.

    Steps: Ingestion → CRS → Validation → Matching → Attributes → Conflicts → Confidence → Review Routing
    """
    return run_pipeline()


@router.post("/reset", response_model=PipelineStatus)
async def reset():
    """Reset pipeline state to idle."""
    return reset_pipeline()
