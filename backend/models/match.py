"""
Match ORM model.
Stores candidate and confirmed matches between source records and parcels.
Every match exposes its evidence (Rules.md §Matching.5).
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from database import Base


class Match(Base):
    """A proposed or confirmed match between a SourceRecord and a Parcel."""

    __tablename__ = "matches"

    match_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    source_record_id = Column(UUID(as_uuid=True), ForeignKey("source_records.source_record_id"), nullable=False)
    parcel_id = Column(String(50), ForeignKey("parcels.parcel_id"), nullable=False)

    # Scores (0-100)
    spatial_score = Column(Float, default=0.0, comment="Spatial overlap/distance score")
    attribute_score = Column(Float, default=0.0, comment="Attribute similarity score")
    source_agreement = Column(Float, default=0.0, comment="Cross-source agreement score")
    overall_score = Column(Float, default=0.0, comment="Weighted composite score")

    # Evidence & explanation
    reasons = Column(JSONB, default=dict, comment="Detailed evidence factors")
    explanation = Column(String(1000), nullable=True, comment="Human-readable explanation")

    # Status
    status = Column(
        String(20),
        default="proposed",
        comment="proposed | confirmed | rejected | review"
    )

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    parcel = relationship("Parcel", back_populates="matches")

    def __repr__(self):
        return f"<Match {self.match_id} parcel={self.parcel_id} score={self.overall_score}>"
