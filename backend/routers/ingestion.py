"""
Data Ingestion API Router.
File upload, validation, and dataset management.
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import json

from database import get_db
from schemas.pipeline import DatasetInfo

router = APIRouter(prefix="/api/ingest", tags=["Data Ingestion"])

# In-memory dataset registry — starts empty so ONLY user-uploaded datasets appear
_datasets: list[DatasetInfo] = []


def _ensure_datasets_initialized():
    """No-op: do not preload demo data automatically."""
    pass


@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    source_type: str = Form("cadastral"),
    dataset_name: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """Upload a geospatial dataset (GeoJSON, CSV, GeoTIFF).

    Validates format, detects CRS, and stores source records.
    """
    _ensure_datasets_initialized()
    content = await file.read()
    name = dataset_name or file.filename

    try:
        from services.ingestion_service import ingest_dataset
        report = ingest_dataset(content, file.filename, source_type, name)

        # Register dataset
        dataset_info = DatasetInfo(
            name=name,
            source_type=source_type,
            file_format=report["format"],
            crs=report.get("original_crs"),
            record_count=report["valid_records"],
            file_size=f"{len(content) / 1024:.0f} KB",
            status=report["status"],
            upload_id=report["upload_id"],
            validation_errors=[e["error"] for e in report.get("validation_errors", [])],
        )
        _datasets.append(dataset_info)

        # Persist source records into PostgreSQL
        try:
            from models.parcel import SourceRecord
            from geoalchemy2.shape import from_shape
            import uuid

            gdf = report.get("gdf")
            if gdf is not None and len(gdf) > 0:
                for idx, row in gdf.iterrows():
                    geom = row.geometry if (hasattr(row, "geometry") and row.geometry is not None and not row.geometry.is_empty) else None
                    geom_wkb = from_shape(geom, srid=4326) if geom is not None else None
                    
                    # Extract attributes dictionary
                    attrs = {k: str(v) for k, v in row.items() if k not in ("geometry",)}
                    ext_id = str(row.get("id") or row.get("parcel_id") or row.get("objectid") or f"REC-{idx+1}")
                    area_val = float(row.get("calculated_area_m2") or row.get("area") or 0.0) if ("calculated_area_m2" in row or "area" in row) else None
                    
                    record = SourceRecord(
                        source_type=source_type,
                        source_dataset=name,
                        external_id=ext_id,
                        attributes=attrs,
                        geometry=geom_wkb,
                        original_crs=report.get("original_crs"),
                        area=area_val,
                        land_use=str(row.get("land_use") or row.get("use") or ""),
                        owner=str(row.get("owner") or ""),
                        upload_id=report["upload_id"],
                        is_valid=report["status"],
                    )
                    db.add(record)
                await db.commit()
        except Exception as db_err:
            # Continue even if DB writing hits an issue so user gets report
            print(f"Warning: Failed saving source records to DB: {db_err}")

        return {
            "message": f"Dataset '{name}' uploaded and processed successfully",
            "upload_id": report["upload_id"],
            "records": report["valid_records"],
            "quarantined": report["quarantined_records"],
            "status": report["status"],
            "crs": report.get("original_crs"),
            "validation_errors": report.get("validation_errors", []),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.get("/datasets", response_model=list[DatasetInfo])
async def list_datasets(db: AsyncSession = Depends(get_db)):
    """List all uploaded datasets from database and memory registry."""
    from sqlalchemy import select, func
    from models.parcel import SourceRecord

    # First collect datasets stored in memory
    results_map: dict[str, DatasetInfo] = {d.name: d for d in _datasets}

    # Also query PostgreSQL source_records to ensure uploaded datasets persist forever
    try:
        stmt = (
            select(
                SourceRecord.source_dataset,
                SourceRecord.source_type,
                SourceRecord.original_crs,
                func.count(SourceRecord.source_record_id).label("record_count"),
            )
            .group_by(
                SourceRecord.source_dataset,
                SourceRecord.source_type,
                SourceRecord.original_crs,
            )
        )
        db_rows = (await db.execute(stmt)).all()
        for row in db_rows:
            dataset_name = row.source_dataset
            if dataset_name and dataset_name not in results_map:
                results_map[dataset_name] = DatasetInfo(
                    name=dataset_name,
                    source_type=row.source_type or "cadastral",
                    file_format="GeoJSON" if "json" in dataset_name.lower() else "CSV" if "csv" in dataset_name.lower() else "Spatial",
                    crs=row.original_crs or "EPSG:4326",
                    record_count=row.record_count or 0,
                    file_size="Persisted DB",
                    status="valid",
                    validation_errors=[],
                )
    except Exception as e:
        print(f"Error querying source_records: {e}")

    return list(results_map.values())


@router.post("/sample")
async def load_sample_data(db: AsyncSession = Depends(get_db)):
    """Load built-in sample datasets for demo."""
    global _datasets

    from seed.seed_data import seed_database
    await seed_database(db)

    _datasets = _get_sample_datasets()
    return {
        "message": "Sample datasets loaded successfully",
        "datasets": len(_datasets),
    }


@router.get("/validate/{upload_id}")
async def get_validation_results(upload_id: str):
    """Get validation results for a specific upload."""
    dataset = next((d for d in _datasets if d.upload_id == upload_id), None)
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Upload {upload_id} not found")
    return dataset


def _get_sample_datasets() -> list[DatasetInfo]:
    """Return metadata for the built-in sample datasets."""
    return [
        DatasetInfo(name="Cadastral Map", source_type="cadastral", file_format="GeoJSON", crs="EPSG:32643", record_count=125, file_size="2.4 MB", status="valid"),
        DatasetInfo(name="Revenue Records", source_type="revenue", file_format="CSV", crs="N/A (tabular)", record_count=118, file_size="340 KB", status="valid"),
        DatasetInfo(name="Municipal GIS", source_type="municipal", file_format="GeoJSON", crs="EPSG:4326", record_count=122, file_size="3.1 MB", status="valid"),
        DatasetInfo(name="GNSS Survey", source_type="gnss", file_format="CSV + GeoJSON", crs="EPSG:4326", record_count=89, file_size="1.8 MB", status="valid"),
        DatasetInfo(name="Drone / ORI", source_type="drone", file_format="GeoTIFF + GeoJSON", crs="EPSG:32643", record_count=95, file_size="45 MB", status="valid"),
    ]
