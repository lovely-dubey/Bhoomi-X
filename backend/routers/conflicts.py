"""
Conflicts API Router.
CRUD operations for detected conflicts + review actions.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from datetime import datetime
from typing import Optional

from database import get_db
from models.conflict import Conflict
from models.review import AuditLog
from schemas.conflict import ConflictOut, ConflictUpdate, ConflictStats

router = APIRouter(prefix="/api/conflicts", tags=["Conflicts"])


@router.get("/", response_model=list[ConflictOut])
async def list_conflicts(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    parcel_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all conflicts with optional filters."""
    query = select(Conflict)
    if status:
        query = query.where(Conflict.status == status)
    if severity:
        query = query.where(Conflict.severity == severity)
    if parcel_id:
        query = query.where(Conflict.parcel_id == parcel_id)

    query = query.order_by(Conflict.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/stats", response_model=ConflictStats)
async def get_conflict_stats(db: AsyncSession = Depends(get_db)):
    """Get conflict summary statistics."""
    total = await db.scalar(select(func.count(Conflict.conflict_id)))
    pending = await db.scalar(select(func.count(Conflict.conflict_id)).where(Conflict.status == "pending"))
    accepted = await db.scalar(select(func.count(Conflict.conflict_id)).where(Conflict.status == "accepted"))
    rejected = await db.scalar(select(func.count(Conflict.conflict_id)).where(Conflict.status == "rejected"))
    escalated = await db.scalar(select(func.count(Conflict.conflict_id)).where(Conflict.status == "escalated"))

    return ConflictStats(
        total=total or 0,
        pending=pending or 0,
        accepted=accepted or 0,
        rejected=rejected or 0,
        escalated=escalated or 0,
    )


@router.get("/{conflict_id}", response_model=ConflictOut)
async def get_conflict(conflict_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific conflict's details."""
    result = await db.execute(select(Conflict).where(Conflict.conflict_id == conflict_id))
    conflict = result.scalar_one_or_none()
    if not conflict:
        raise HTTPException(status_code=404, detail="Conflict not found")
    return conflict


@router.put("/{conflict_id}")
async def resolve_conflict(
    conflict_id: str,
    body: ConflictUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Resolve a conflict: accept, reject, or escalate."""
    result = await db.execute(select(Conflict).where(Conflict.conflict_id == conflict_id))
    conflict = result.scalar_one_or_none()
    if not conflict:
        raise HTTPException(status_code=404, detail="Conflict not found")

    conflict.status = body.status
    conflict.resolved_at = datetime.utcnow()
    conflict.resolved_by = body.reviewer

    # Create audit entry
    audit = AuditLog(
        entity_type="conflict",
        entity_id=str(conflict_id),
        action=f"conflict_{body.status}",
        details={
            "reviewer": body.reviewer,
            "comment": body.comment,
            "previous_status": "pending",
        },
        user=body.reviewer,
    )
    db.add(audit)

    return {
        "message": f"Conflict {body.status}",
        "conflict_id": str(conflict_id),
        "parcel_id": conflict.parcel_id,
        "reviewer": body.reviewer,
    }
