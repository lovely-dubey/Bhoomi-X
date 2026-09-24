"""
Parcels API Router.
CRUD operations + spatial queries + GeoJSON export.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from sqlalchemy.orm import selectinload
from typing import Optional, List
import json

from database import get_db
from models.parcel import Parcel, SourceRecord
from models.conflict import Conflict
from schemas.parcel import ParcelOut, ParcelSummary, ParcelStats, ParcelGeoJSON

router = APIRouter(prefix="/api/parcels", tags=["Parcels"])


@router.get("/", response_model=list[ParcelSummary])
async def list_parcels(
    status: Optional[str] = Query(None, description="Filter by status"),
    min_confidence: Optional[float] = Query(None, description="Minimum confidence score"),
    land_use: Optional[str] = Query(None, description="Filter by land use"),
    limit: int = Query(200, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List parcels with optional filters."""
    query = select(Parcel)
    if status:
        query = query.where(Parcel.status == status)
    if min_confidence is not None:
        query = query.where(Parcel.confidence >= min_confidence)
    if land_use:
        query = query.where(Parcel.land_use == land_use)

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/stats", response_model=ParcelStats)
async def get_parcel_stats(db: AsyncSession = Depends(get_db)):
    """Get dashboard KPI statistics."""
    total = await db.scalar(select(func.count(Parcel.parcel_id)))
    harmonized = await db.scalar(
        select(func.count(Parcel.parcel_id)).where(Parcel.status == "validated")
    )
    high_conf = await db.scalar(
        select(func.count(Parcel.parcel_id)).where(Parcel.confidence >= 90)
    )
    review = await db.scalar(
        select(func.count(Parcel.parcel_id)).where(Parcel.status == "review")
    )
    conflicts = await db.scalar(
        select(func.count(Conflict.conflict_id)).where(Conflict.status == "pending")
    )
    changed = await db.scalar(
        select(func.count(Parcel.parcel_id)).where(Parcel.status == "changed")
    )

    return ParcelStats(
        total_parcels=total or 0,
        harmonized=harmonized or 0,
        high_confidence=high_conf or 0,
        review_required=review or 0,
        conflicts=conflicts or 0,
        recent_changes=changed or 0,
    )


@router.get("/geojson")
async def get_parcels_geojson(
    status: Optional[str] = None,
    min_confidence: Optional[float] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get all parcels as a GeoJSON FeatureCollection."""
    query = select(Parcel)
    if status:
        query = query.where(Parcel.status == status)
    if min_confidence is not None:
        query = query.where(Parcel.confidence >= min_confidence)

    result = await db.execute(query)
    parcels = result.scalars().all()

    features = []
    for p in parcels:
        # Convert WKB geometry to GeoJSON
        if p.geometry is not None:
            geojson_result = await db.execute(
                text(f"SELECT ST_AsGeoJSON(geometry) FROM parcels WHERE parcel_id = :pid"),
                {"pid": p.parcel_id}
            )
            geom_json = geojson_result.scalar()
            geometry = json.loads(geom_json) if geom_json else None
        else:
            geometry = None

        features.append({
            "type": "Feature",
            "properties": {
                "parcel_id": p.parcel_id,
                "area": p.area,
                "land_use": p.land_use,
                "owner": p.owner,
                "confidence": p.confidence,
                "status": p.status,
            },
            "geometry": geometry,
        })

    return {
        "type": "FeatureCollection",
        "features": features,
    }


@router.get("/{parcel_id}")
async def get_parcel_detail(parcel_id: str, db: AsyncSession = Depends(get_db)):
    """Get full parcel detail with source records, matches, and conflicts."""
    result = await db.execute(
        select(Parcel)
        .options(selectinload(Parcel.source_records))
        .options(selectinload(Parcel.matches))
        .options(selectinload(Parcel.conflicts))
        .options(selectinload(Parcel.reviews))
        .where(Parcel.parcel_id == parcel_id)
    )
    parcel = result.scalar_one_or_none()
    if not parcel:
        raise HTTPException(status_code=404, detail=f"Parcel {parcel_id} not found")

    # Get geometry as GeoJSON
    geom_result = await db.execute(
        text("SELECT ST_AsGeoJSON(geometry) FROM parcels WHERE parcel_id = :pid"),
        {"pid": parcel_id}
    )
    geom_json = geom_result.scalar()

    return {
        "parcel_id": parcel.parcel_id,
        "source_id": parcel.source_id,
        "area": parcel.area,
        "land_use": parcel.land_use,
        "owner": parcel.owner,
        "confidence": parcel.confidence,
        "status": parcel.status,
        "geometry": json.loads(geom_json) if geom_json else None,
        "source_records": [
            {
                "source_type": sr.source_type,
                "source_dataset": sr.source_dataset,
                "external_id": sr.external_id,
                "area": sr.area,
                "land_use": sr.land_use,
                "owner": sr.owner,
                "is_valid": sr.is_valid,
            }
            for sr in parcel.source_records
        ],
        "matches": [
            {
                "match_id": str(m.match_id),
                "spatial_score": m.spatial_score,
                "attribute_score": m.attribute_score,
                "overall_score": m.overall_score,
                "explanation": m.explanation,
                "status": m.status,
            }
            for m in parcel.matches
        ],
        "conflicts": [
            {
                "conflict_id": str(c.conflict_id),
                "conflict_type": c.conflict_type,
                "severity": c.severity,
                "status": c.status,
                "recommended_action": c.recommended_action,
            }
            for c in parcel.conflicts
        ],
        "reviews": [
            {
                "review_id": str(r.review_id),
                "reviewer": r.reviewer,
                "decision": r.decision,
                "comment": r.comment,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            }
            for r in parcel.reviews
        ],
    }
