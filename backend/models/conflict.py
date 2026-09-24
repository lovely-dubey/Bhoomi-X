"""
Conflict ORM model.
Flags detected inconsistencies between data sources for a parcel.
100% of flagged conflicts must have an explanation (PRD §9).
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from database import Base


class Conflict(Base):
    """A detected conflict/inconsistency for a parcel."""

    __tablename__ = "conflicts"

    conflict_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # FK to parcel
    parcel_id = Column(String(50), ForeignKey("parcels.parcel_id"), nullable=False)

    # Conflict details
    conflict_type = Column(
        String(50),
        nullable=False,
        comment="area_mismatch | boundary_mismatch | missing_record | duplicate_id | land_use_conflict | encroachment | ownership_dispute"
    )
    severity = Column(
        String(20),
        default="medium",
        comment="low | medium | high | critical"
    )
    observed_values = Column(JSONB, default=dict, comment="Values from each conflicting source")
    recommended_action = Column(String(500), nullable=True)
    explanation = Column(String(1000), nullable=True, comment="Why this conflict was flagged")

    # Status
    status = Column(
        String(20),
        default="pending",
        comment="pending | accepted | rejected | escalated"
    )

    sources_involved = Column(String(200), nullable=True, comment="Which sources are in conflict")
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(100), nullable=True)

    # Relationships
    parcel = relationship("Parcel", back_populates="conflicts")

    def __repr__(self):
        return f"<Conflict {self.conflict_type} parcel={self.parcel_id} severity={self.severity}>"
