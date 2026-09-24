"""
Review Service.
Routes uncertain cases to human review per FR-08.
Records reviewer actions for auditability per FR-09.
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def create_review_decision(
    parcel_id: str,
    reviewer: str,
    decision: str,
    comment: Optional[str] = None,
    evidence_snapshot: Optional[Dict] = None,
) -> Dict:
    """Create a review decision record.

    Reviewer decisions are auditable (Rules.md §Review.1).
    Rejected recommendations remain in the audit trail (Rules.md §Review.3).
    """
    valid_decisions = {"accepted", "rejected", "escalated"}
    if decision not in valid_decisions:
        raise ValueError(f"Invalid decision: {decision}. Must be one of: {valid_decisions}")

    review = {
        "parcel_id": parcel_id,
        "reviewer": reviewer,
        "decision": decision,
        "comment": comment,
        "evidence_snapshot": evidence_snapshot or {},
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Determine new parcel status based on decision
    status_map = {
        "accepted": "validated",
        "rejected": "review",
        "escalated": "conflict",
    }
    review["new_parcel_status"] = status_map.get(decision, "review")

    logger.info(f"Review recorded: parcel={parcel_id}, decision={decision}, reviewer={reviewer}")
    return review


def create_audit_entry(
    entity_type: str,
    entity_id: str,
    action: str,
    details: Dict = None,
    user: str = "system",
) -> Dict:
    """Create an audit log entry."""
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "action": action,
        "details": details or {},
        "user": user,
        "timestamp": datetime.utcnow().isoformat(),
    }
