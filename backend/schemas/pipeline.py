"""Pipeline Pydantic schemas."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PipelineStep(BaseModel):
    step_number: int
    name: str
    description: str
    status: str = "pending"  # pending | running | complete | error
    records_processed: Optional[str] = None
    duration_seconds: Optional[float] = None
    errors: list[str] = []


class PipelineStatus(BaseModel):
    pipeline_id: str
    status: str = "idle"  # idle | running | complete | error
    current_step: int = 0
    total_steps: int = 8
    steps: list[PipelineStep] = []
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    summary: Optional[str] = None


class DatasetInfo(BaseModel):
    """Metadata for an uploaded/loaded dataset."""
    name: str
    source_type: str
    file_format: str
    crs: Optional[str] = None
    record_count: int = 0
    file_size: Optional[str] = None
    status: str = "valid"  # valid | warning | error
    upload_id: Optional[str] = None
    validation_errors: list[str] = []
