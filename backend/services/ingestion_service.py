"""
Data Ingestion Service.
Parse GeoJSON/CSV, validate, store as SourceRecords in PostGIS.
Users can upload supported datasets and see validation errors (FR-01).
"""

import json
import io
import uuid
import geopandas as gpd
import pandas as pd
from shapely.geometry import shape, mapping
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import logging

from geo.crs import detect_crs, transform_to_project_crs
from geo.geometry import validate_geodataframe, calculate_area_m2

logger = logging.getLogger(__name__)


def parse_geojson(file_content: bytes, filename: str) -> Tuple[gpd.GeoDataFrame, Dict]:
    """Parse a GeoJSON file into a GeoDataFrame.

    Returns (gdf, metadata).
    """
    try:
        data = json.loads(file_content)
        gdf = gpd.GeoDataFrame.from_features(data["features"], crs=data.get("crs", {}).get("properties", {}).get("name", "EPSG:4326"))
        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")

        metadata = {
            "filename": filename,
            "format": "GeoJSON",
            "feature_count": len(gdf),
            "detected_crs": detect_crs(gdf),
            "geometry_types": list(gdf.geometry.geom_type.unique()),
            "columns": list(gdf.columns),
        }
        return gdf, metadata
    except Exception as e:
        logger.error(f"GeoJSON parse error: {e}")
        raise ValueError(f"Failed to parse GeoJSON: {e}")


def parse_csv(file_content: bytes, filename: str, lat_col: str = "lat", lon_col: str = "lon") -> Tuple[gpd.GeoDataFrame, Dict]:
    """Parse a CSV file with coordinate columns into a GeoDataFrame.

    Falls back to tabular-only if no coordinate columns found.
    """
    try:
        df = pd.read_csv(io.BytesIO(file_content))

        # Try to find coordinate columns
        lat_candidates = [c for c in df.columns if c.lower() in ("lat", "latitude", "y")]
        lon_candidates = [c for c in df.columns if c.lower() in ("lon", "lng", "longitude", "x")]

        has_geometry = len(lat_candidates) > 0 and len(lon_candidates) > 0

        if has_geometry:
            lat_c = lat_candidates[0]
            lon_c = lon_candidates[0]
            gdf = gpd.GeoDataFrame(
                df,
                geometry=gpd.points_from_xy(df[lon_c], df[lat_c]),
                crs="EPSG:4326"
            )
        else:
            # Tabular-only (e.g., revenue records)
            from shapely.geometry import Point
            gdf = gpd.GeoDataFrame(df, geometry=[None] * len(df))

        metadata = {
            "filename": filename,
            "format": "CSV",
            "record_count": len(df),
            "has_geometry": has_geometry,
            "columns": list(df.columns),
            "detected_crs": "EPSG:4326" if has_geometry else "N/A (tabular)",
        }
        return gdf, metadata
    except Exception as e:
        logger.error(f"CSV parse error: {e}")
        raise ValueError(f"Failed to parse CSV: {e}")


def ingest_dataset(
    file_content: bytes,
    filename: str,
    source_type: str,
    dataset_name: Optional[str] = None,
) -> Dict:
    """Full ingestion pipeline for a single file.

    1. Parse file
    2. Detect CRS
    3. Transform to project CRS
    4. Validate geometries
    5. Return validation report

    Returns ingestion report dict.
    """
    upload_id = str(uuid.uuid4())[:8]
    dataset_name = dataset_name or filename

    # Parse
    ext = filename.lower().split(".")[-1]
    if ext in ("geojson", "json"):
        gdf, metadata = parse_geojson(file_content, filename)
    elif ext == "csv":
        gdf, metadata = parse_csv(file_content, filename)
    else:
        raise ValueError(f"Unsupported format: {ext}. Supported: geojson, csv")

    # CRS transform
    original_crs = metadata.get("detected_crs", "unknown")
    has_geom = metadata.get("has_geometry", True)

    if has_geom and gdf.geometry.notna().any():
        gdf, crs_record = transform_to_project_crs(gdf)
        # Validate
        valid_gdf, validation_errors = validate_geodataframe(gdf)
        # Calculate areas
        if len(valid_gdf) > 0 and valid_gdf.geometry.notna().any():
            try:
                valid_gdf = valid_gdf.copy()
                valid_gdf["calculated_area_m2"] = calculate_area_m2(valid_gdf)
            except Exception as e:
                logger.warning(f"Area calculation skipped: {e}")
    else:
        valid_gdf = gdf
        validation_errors = []
        crs_record = {"original_crs": "N/A", "transformed": False}

    report = {
        "upload_id": upload_id,
        "dataset_name": dataset_name,
        "source_type": source_type,
        "filename": filename,
        "format": metadata["format"],
        "original_crs": original_crs,
        "target_crs": "EPSG:4326",
        "total_records": len(gdf),
        "valid_records": len(valid_gdf),
        "quarantined_records": len(gdf) - len(valid_gdf),
        "validation_errors": validation_errors,
        "columns": metadata.get("columns", []),
        "status": "valid" if not validation_errors else "warning",
        "crs_transformation": crs_record,
        "gdf": valid_gdf,  # Pass the GeoDataFrame for downstream use
    }

    logger.info(
        f"Ingested {dataset_name}: {report['valid_records']}/{report['total_records']} valid records"
    )
    return report
