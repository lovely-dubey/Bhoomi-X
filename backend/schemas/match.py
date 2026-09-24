"""Match Pydantic schemas."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class MatchOut(BaseModel):
    match_id: UUID
    source_record_id: UUID
    parcel_id: str
    spatial_score: float = 0.0
    attribute_score: float = 0.0
    source_agreement: float = 0.0
    overall_score: float = 0.0
    reasons: dict = {}
    explanation: Optional[str] = None
    status: str = "proposed"
    created_at: datetime

    model_config = {"from_attributes": True}
