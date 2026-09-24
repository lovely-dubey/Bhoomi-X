"""
Parcel and SourceRecord ORM models.
Parcel is the canonical harmonized land record.
SourceRecord stores raw ingested data from each source dataset.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, DateTime, Text, Enum as SAEnum, ForeignKey, Integer
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship
from database import Base


class Parcel(Base):
    """Canonical harmonized parcel record."""

    __tablename__ = "parcels"

    parcel_id = Column(String(50), primary_key=True, default=lambda: f"P-{uuid.uuid4().hex[:6].upper()}")
    source_id = Column(String(100), nullable=True, comment="Original identifier from primary source")
    geometry = Column(Geometry("POLYGON", srid=4326), nullable=False)
    area = Column(Float, nullable=True, comment="Area in square meters")
    land_use = Column(String(100), nullable=True)
    owner = Column(String(200), nullable=True)
    confidence = Column(Float, default=0.0, comment="Harmonization confidence score 0-100")
    status = Column(
        String(20),
        default="pending",
        comment="validated | review | conflict | changed | pending"
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    source_records = relationship("SourceRecord", back_populates="parcel", lazy="selectin")
    matches = relationship("Match", back_populates="parcel", lazy="selectin")
    conflicts = relationship("Conflict", back_populates="parcel", lazy="selectin")
    reviews = relationship("Review", back_populates="parcel", lazy="selectin")

    def __repr__(self):
        return f"<Parcel {self.parcel_id} status={self.status} confidence={self.confidence}>"


class SourceRecord(Base):
    """Raw record from an ingested source dataset.
    Every record retains its source dataset and source identifier (Rules.md §Data.2).
    """

    __tablename__ = "source_records"

    source_record_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type = Column(
        String(50),
        nullable=False,
        comment="cadastral | revenue | municipal | gnss | drone"
    )
    source_dataset = Column(String(200), nullable=False, comment="Name/path of the uploaded dataset")
    external_id = Column(String(100), nullable=True, comment="ID from the source system")
    attributes = Column(JSONB, default=dict, comment="All original attributes preserved")
    geometry = Column(Geometry("GEOMETRY", srid=4326), nullable=True)
    original_crs = Column(String(50), nullable=True, comment="CRS before transformation")
    area = Column(Float, nullable=True)
    land_use = Column(String(100), nullable=True)
    owner = Column(String(200), nullable=True)
    upload_id = Column(String(100), nullable=True, comment="Upload batch identifier")
    is_valid = Column(String(20), default="valid", comment="valid | warning | error | quarantined")
    validation_errors = Column(JSONB, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    # FK to parcel (set after matching)
    parcel_id = Column(String(50), ForeignKey("parcels.parcel_id"), nullable=True)
    parcel = relationship("Parcel", back_populates="source_records")

    def __repr__(self):
        return f"<SourceRecord {self.source_type}:{self.external_id}>"
