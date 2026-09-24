"""
Reviews API Router.
Human review actions and audit trail.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime

from database import get_db
from models.parcel import Parcel
from models.review import Review, AuditLog
from schemas.review import ReviewCreate, ReviewOut, AuditLogOut

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


@router.get("/", response_model=list[ReviewOut])
async def list_reviews(db: AsyncSession = Depends(get_db)):
    """List all review decisions."""
    result = await db.execute(select(Review).order_by(Review.timestamp.desc()))
    return result.scalars().all()


@router.post("/", response_model=ReviewOut)
async def create_review(
    body: ReviewCreate,
    db: AsyncSession = Depends(get_db),
):
    """Submit a review decision for a parcel.

    Updates parcel status based on decision.
    Records action in audit trail.
    """
    # Verify parcel exists
    parcel = await db.scalar(select(Parcel).where(Parcel.parcel_id == body.parcel_id))
    if not parcel:
        raise HTTPException(status_code=404, detail=f"Parcel {body.parcel_id} not found")

    # Create review
    review = Review(
        parcel_id=body.parcel_id,
        reviewer=body.reviewer,
        decision=body.decision,
        comment=body.comment,
    )
    db.add(review)

    # Update parcel status
    status_map = {"accepted": "validated", "rejected": "review", "escalated": "conflict"}
    new_status = status_map.get(body.decision, "review")
    parcel.status = new_status

    # Audit log
    audit = AuditLog(
        entity_type="parcel",
        entity_id=body.parcel_id,
        action=f"review_{body.decision}",
        details={
            "reviewer": body.reviewer,
            "decision": body.decision,
            "comment": body.comment,
            "new_status": new_status,
        },
        user=body.reviewer,
    )
    db.add(audit)

    await db.flush()
    return review


@router.get("/audit", response_model=list[AuditLogOut])
async def get_audit_trail(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Get the audit trail."""
    result = await db.execute(
        select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit)
    )
    return result.scalars().all()
