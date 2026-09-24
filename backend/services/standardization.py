"""
Standardization Service.
Normalizes field names, data types and coordinate reference systems (FR-02).
"""

import geopandas as gpd
import pandas as pd
from typing import Dict, List, Tuple
import logging

from ai.attribute_matcher import match_schema, FIELD_ALIASES
from geo.crs import transform_to_project_crs, transform_to_utm
from geo.geometry import calculate_area_m2

logger = logging.getLogger(__name__)

# Canonical parcel schema
CANONICAL_SCHEMA = {
    "parcel_id": str,
    "owner": str,
    "area": float,
    "land_use": str,
    "address": str,
}


def normalize_field_names(gdf: gpd.GeoDataFrame) -> Tuple[gpd.GeoDataFrame, Dict]:
    """Map source field names to canonical schema.

    Returns (renamed_gdf, field_mapping).
    """
    source_cols = [c for c in gdf.columns if c != "geometry"]
    canonical_cols = list(CANONICAL_SCHEMA.keys())

    # Try to map source columns to canonical names
    mapping = match_schema(source_cols, canonical_cols)

    # Build rename dict (source → canonical)
    rename_map = {}
    for src_col, matched_canonical in mapping.items():
        if matched_canonical:
            rename_map[src_col] = matched_canonical

    if rename_map:
        gdf = gdf.rename(columns=rename_map)
        logger.info(f"Renamed fields: {rename_map}")

    return gdf, {
        "original_to_canonical": rename_map,
        "unmapped_fields": [c for c in source_cols if c not in rename_map],
    }


def standardize_dataset(
    gdf: gpd.GeoDataFrame,
    source_type: str,
) -> Tuple[gpd.GeoDataFrame, Dict]:
    """Full standardization pipeline for a dataset.

    1. Normalize field names
    2. Ensure CRS is EPSG:4326
    3. Compute areas in UTM
    4. Record provenance

    Returns (standardized_gdf, standardization_report).
    """
    report = {"source_type": source_type, "steps": []}

    # Field normalization
    gdf, field_report = normalize_field_names(gdf)
    report["field_mapping"] = field_report
    report["steps"].append("field_normalization")

    # CRS standardization
    has_geom = gdf.geometry.notna().any() if "geometry" in gdf.columns else False
    if has_geom:
        gdf, crs_report = transform_to_project_crs(gdf)
        report["crs_transformation"] = crs_report
        report["steps"].append("crs_transformation")

        # Area calculation in metric units
        try:
            gdf = gdf.copy()
            gdf["area_m2"] = calculate_area_m2(gdf)
            report["steps"].append("area_calculation")
        except Exception as e:
            logger.warning(f"Area calc skipped: {e}")

    report["record_count"] = len(gdf)
    report["columns"] = list(gdf.columns)

    return gdf, report
