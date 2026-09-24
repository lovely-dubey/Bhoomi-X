"""Review and AuditLog Pydantic schemas."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class ReviewCreate(BaseModel):
    parcel_id: str
    reviewer: str = "admin"
    decision: str  # accepted | rejected | escalated
    comment: Optional[str] = None


class ReviewOut(BaseModel):
    review_id: UUID
    parcel_id: str
    reviewer: str
    decision: str
    comment: Optional[str] = None
    timestamp: datetime

    model_config = {"from_attributes": True}


class AuditLogOut(BaseModel):
    log_id: UUID
    entity_type: str
    entity_id: str
    action: str
    details: dict = {}
    user: str
    timestamp: datetime

    model_config = {"from_attributes": True}
