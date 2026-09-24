"""Conflict Pydantic schemas."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class ConflictOut(BaseModel):
    conflict_id: UUID
    parcel_id: str
    conflict_type: str
    severity: str = "medium"
    observed_values: dict = {}
    recommended_action: Optional[str] = None
    explanation: Optional[str] = None
    status: str = "pending"
    sources_involved: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None

    model_config = {"from_attributes": True}


class ConflictUpdate(BaseModel):
    """Request body for resolving a conflict."""
    status: str  # accepted | rejected | escalated
    reviewer: str = "admin"
    comment: Optional[str] = None


class ConflictStats(BaseModel):
    total: int = 0
    pending: int = 0
    accepted: int = 0
    rejected: int = 0
    escalated: int = 0
    by_severity: dict = {}
    by_type: dict = {}
