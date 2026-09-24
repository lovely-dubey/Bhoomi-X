"""
Review and AuditLog ORM models.
Reviewer decisions are auditable (Rules.md §Review.1).
Rejected recommendations remain in the audit trail (Rules.md §Review.3).
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from database import Base


class Review(Base):
    """Human review decision for a parcel."""

    __tablename__ = "reviews"

    review_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # FK to parcel
    parcel_id = Column(String(50), ForeignKey("parcels.parcel_id"), nullable=False)

    # Review details
    reviewer = Column(String(100), nullable=False, default="system")
    decision = Column(
        String(20),
        nullable=False,
        comment="accepted | rejected | escalated | pending"
    )
    comment = Column(Text, nullable=True)
    evidence_snapshot = Column(JSONB, default=dict, comment="Snapshot of evidence at time of review")

    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    parcel = relationship("Parcel", back_populates="reviews")

    def __repr__(self):
        return f"<Review {self.review_id} parcel={self.parcel_id} decision={self.decision}>"


class AuditLog(Base):
    """Immutable audit trail for all system and user actions.
    Records source datasets, processing steps, match reasons, and reviewer actions (FR-09).
    """

    __tablename__ = "audit_log"

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(50), nullable=False, comment="parcel | match | conflict | review | pipeline | dataset")
    entity_id = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False, comment="created | updated | reviewed | exported | ingested | matched")
    details = Column(JSONB, default=dict)
    user = Column(String(100), default="system")
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog {self.action} {self.entity_type}:{self.entity_id}>"
