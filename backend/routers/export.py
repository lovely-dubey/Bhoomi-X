"""
Export API Router.
Export harmonized records and review reports (FR-10).
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
import json

from database import get_db
from models.parcel import Parcel
from models.conflict import Conflict
from models.review import Review, AuditLog

router = APIRouter(prefix="/api/export", tags=["Export"])


@router.get("/geojson")
async def export_geojson(db: AsyncSession = Depends(get_db)):
    """Export all harmonized parcels as a GeoJSON FeatureCollection."""
    result = await db.execute(select(Parcel))
    parcels = result.scalars().all()

    features = []
    for p in parcels:
        geom_result = await db.execute(
            text("SELECT ST_AsGeoJSON(geometry) FROM parcels WHERE parcel_id = :pid"),
            {"pid": p.parcel_id}
        )
        geom_json = geom_result.scalar()

        features.append({
            "type": "Feature",
            "properties": {
                "parcel_id": p.parcel_id,
                "area": p.area,
                "land_use": p.land_use,
                "owner": p.owner,
                "confidence": p.confidence,
                "status": p.status,
                "source_id": p.source_id,
            },
            "geometry": json.loads(geom_json) if geom_json else None,
        })

    geojson = {
        "type": "FeatureCollection",
        "name": "BHOOMI-X Harmonized Parcels",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::4326"}},
        "features": features,
    }

    return JSONResponse(
        content=geojson,
        headers={"Content-Disposition": "attachment; filename=bhoomix_harmonized_parcels.geojson"}
    )


@router.get("/csv")
async def export_csv(db: AsyncSession = Depends(get_db)):
    """Export harmonized parcels as CSV."""
    result = await db.execute(select(Parcel))
    parcels = result.scalars().all()

    import io, csv
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["parcel_id", "source_id", "area", "land_use", "owner", "confidence", "status"])
    for p in parcels:
        writer.writerow([p.parcel_id, p.source_id, p.area, p.land_use, p.owner, p.confidence, p.status])

    from fastapi.responses import StreamingResponse
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=bhoomix_harmonized_parcels.csv"}
    )


@router.get("/report")
async def export_report(db: AsyncSession = Depends(get_db)):
    """Export full reconciliation report with parcels, conflicts, reviews, and audit trail."""
    parcels = (await db.execute(select(Parcel))).scalars().all()
    conflicts = (await db.execute(select(Conflict))).scalars().all()
    reviews = (await db.execute(select(Review))).scalars().all()
    audit = (await db.execute(select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100))).scalars().all()

    report = {
        "title": "BHOOMI-X Reconciliation Report",
        "generated_at": __import__("datetime").datetime.utcnow().isoformat(),
        "summary": {
            "total_parcels": len(parcels),
            "validated": sum(1 for p in parcels if p.status == "validated"),
            "review": sum(1 for p in parcels if p.status == "review"),
            "conflict": sum(1 for p in parcels if p.status == "conflict"),
            "changed": sum(1 for p in parcels if p.status == "changed"),
            "total_conflicts": len(conflicts),
            "pending_conflicts": sum(1 for c in conflicts if c.status == "pending"),
            "total_reviews": len(reviews),
        },
        "conflicts": [
            {
                "parcel_id": c.parcel_id,
                "type": c.conflict_type,
                "severity": c.severity,
                "status": c.status,
                "action": c.recommended_action,
            }
            for c in conflicts
        ],
        "audit_trail": [
            {
                "entity": f"{a.entity_type}:{a.entity_id}",
                "action": a.action,
                "user": a.user,
                "timestamp": a.timestamp.isoformat() if a.timestamp else None,
            }
            for a in audit
        ],
        "disclaimer": "This report is generated from prototype/synthetic data and does not represent authoritative government land records.",
    }

    return JSONResponse(
        content=report,
        headers={"Content-Disposition": "attachment; filename=bhoomix_reconciliation_report.json"}
    )
