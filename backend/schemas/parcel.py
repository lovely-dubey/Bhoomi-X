"""Parcel and SourceRecord Pydantic schemas for API request/response."""

from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from uuid import UUID


class SourceRecordOut(BaseModel):
    source_record_id: UUID
    source_type: str
    source_dataset: str
    external_id: Optional[str] = None
    attributes: dict = {}
    area: Optional[float] = None
    land_use: Optional[str] = None
    owner: Optional[str] = None
    original_crs: Optional[str] = None
    is_valid: str = "valid"
    validation_errors: list = []
    created_at: datetime

    model_config = {"from_attributes": True}


class ParcelBase(BaseModel):
    parcel_id: str
    area: Optional[float] = None
    land_use: Optional[str] = None
    owner: Optional[str] = None
    confidence: float = 0.0
    status: str = "pending"


class ParcelOut(ParcelBase):
    """Full parcel response with geometry as GeoJSON."""
    source_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    source_records: list[SourceRecordOut] = []
    geometry_geojson: Optional[dict] = Field(None, alias="geometry_geojson")

    model_config = {"from_attributes": True}


class ParcelSummary(BaseModel):
    """Lightweight parcel for list views."""
    parcel_id: str
    area: Optional[float] = None
    land_use: Optional[str] = None
    confidence: float = 0.0
    status: str = "pending"

    model_config = {"from_attributes": True}


class ParcelGeoJSON(BaseModel):
    """GeoJSON Feature representation of a parcel."""
    type: str = "Feature"
    properties: dict
    geometry: dict


class ParcelStats(BaseModel):
    """Dashboard KPI statistics."""
    total_parcels: int = 0
    harmonized: int = 0
    high_confidence: int = 0
    review_required: int = 0
    conflicts: int = 0
    recent_changes: int = 0
