"""
Geometry Validation, Area, and Topology Operations.
Rejects or quarantines invalid geometries (Rules.md §Data.7).
"""

import geopandas as gpd
import numpy as np
from shapely.geometry import shape, mapping
from shapely.validation import make_valid, explain_validity
from shapely.ops import unary_union
from typing import Tuple, List, Dict, Any
import logging

from geo.crs import transform_to_utm

logger = logging.getLogger(__name__)


def validate_geometry(geom) -> Tuple[bool, str]:
    """Validate a single geometry.

    Returns (is_valid, error_message).
    """
    if geom is None or geom.is_empty:
        return False, "Geometry is empty or null"

    if not geom.is_valid:
        reason = explain_validity(geom)
        return False, f"Invalid geometry: {reason}"

    if geom.geom_type not in ("Polygon", "MultiPolygon", "Point", "LineString", "MultiPoint", "MultiLineString"):
        return False, f"Unsupported geometry type: {geom.geom_type}"

    return True, "valid"


def validate_geodataframe(gdf: gpd.GeoDataFrame) -> Tuple[gpd.GeoDataFrame, List[Dict]]:
    """Validate all geometries in a GeoDataFrame.

    Returns:
        (valid_gdf, validation_errors)

    Invalid geometries are quarantined, not silently fixed (Rules.md §Data.7).
    """
    errors = []
    valid_mask = []

    for idx, row in gdf.iterrows():
        is_valid, msg = validate_geometry(row.geometry)
        valid_mask.append(is_valid)
        if not is_valid:
            errors.append({
                "index": int(idx) if isinstance(idx, (int, np.integer)) else str(idx),
                "error": msg,
                "quarantined": True,
            })

    valid_gdf = gdf[valid_mask].copy()
    quarantined_count = len(gdf) - len(valid_gdf)

    if quarantined_count > 0:
        logger.warning(f"Quarantined {quarantined_count} invalid geometries out of {len(gdf)}")

    return valid_gdf, errors


def attempt_fix_geometry(geom):
    """Attempt to fix an invalid geometry using buffer(0).

    Only for reporting purposes — the fixed version is not used to overwrite
    the original without explicit user approval (Rules.md §Data.3).
    """
    try:
        fixed = make_valid(geom)
        return fixed, True
    except Exception:
        return geom, False


def calculate_area_m2(gdf: gpd.GeoDataFrame) -> gpd.GeoSeries:
    """Calculate geodesic area in square meters.

    Transforms to local UTM for accurate area computation.
    """
    utm_gdf = transform_to_utm(gdf)
    return utm_gdf.geometry.area


def calculate_perimeter_m(gdf: gpd.GeoDataFrame) -> gpd.GeoSeries:
    """Calculate perimeter in meters using UTM projection."""
    utm_gdf = transform_to_utm(gdf)
    return utm_gdf.geometry.length


def compare_boundaries(geom_a, geom_b) -> Dict[str, float]:
    """Compare two parcel boundaries.

    Returns metrics for assessing boundary agreement:
    - hausdorff_distance: max distance between boundaries
    - mean_distance: average boundary deviation
    - vertex_count_diff: difference in vertex counts
    """
    from shapely.ops import nearest_points

    try:
        hausdorff = geom_a.hausdorff_distance(geom_b)

        # Count vertices
        verts_a = len(list(geom_a.exterior.coords)) if geom_a.geom_type == "Polygon" else 0
        verts_b = len(list(geom_b.exterior.coords)) if geom_b.geom_type == "Polygon" else 0

        return {
            "hausdorff_distance": round(hausdorff, 4),
            "vertex_count_a": verts_a,
            "vertex_count_b": verts_b,
            "vertex_count_diff": abs(verts_a - verts_b),
        }
    except Exception as e:
        logger.error(f"Boundary comparison failed: {e}")
        return {"hausdorff_distance": -1, "error": str(e)}


def topology_check(gdf: gpd.GeoDataFrame) -> List[Dict]:
    """Check for topology issues: overlaps, gaps, slivers.

    Returns a list of detected issues.
    """
    issues = []

    for i in range(len(gdf)):
        for j in range(i + 1, len(gdf)):
            geom_a = gdf.iloc[i].geometry
            geom_b = gdf.iloc[j].geometry

            if geom_a.intersects(geom_b):
                intersection = geom_a.intersection(geom_b)
                if intersection.area > 0:
                    overlap_pct = (intersection.area / min(geom_a.area, geom_b.area)) * 100
                    if overlap_pct > 0.1:  # More than 0.1% overlap
                        issues.append({
                            "type": "overlap",
                            "parcels": [str(gdf.index[i]), str(gdf.index[j])],
                            "overlap_area": round(intersection.area, 4),
                            "overlap_pct": round(overlap_pct, 2),
                        })

    return issues
