"""
Spatial Operations: Joins, Intersection, Containment, Overlap.
Uses PostGIS-backed operations where possible, Shapely for in-memory.
"""

import geopandas as gpd
import numpy as np
from shapely.geometry import shape
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


def spatial_join(
    gdf_a: gpd.GeoDataFrame,
    gdf_b: gpd.GeoDataFrame,
    how: str = "inner",
    predicate: str = "intersects"
) -> gpd.GeoDataFrame:
    """Perform a spatial join between two GeoDataFrames.

    Args:
        gdf_a: Left GeoDataFrame
        gdf_b: Right GeoDataFrame
        how: Join type ('inner', 'left', 'right')
        predicate: Spatial predicate ('intersects', 'contains', 'within')
    """
    return gpd.sjoin(gdf_a, gdf_b, how=how, predicate=predicate)


def find_intersecting_parcels(gdf: gpd.GeoDataFrame) -> List[Dict]:
    """Find all pairs of intersecting parcels in a single layer.

    Returns list of intersection records with areas.
    """
    intersections = []
    sindex = gdf.sindex

    for idx, row in gdf.iterrows():
        candidates_idx = list(sindex.intersection(row.geometry.bounds))
        for c_idx in candidates_idx:
            if c_idx <= idx:
                continue
            other = gdf.iloc[c_idx]
            if row.geometry.intersects(other.geometry):
                inter = row.geometry.intersection(other.geometry)
                if inter.area > 0:
                    intersections.append({
                        "parcel_a": str(idx),
                        "parcel_b": str(gdf.index[c_idx]),
                        "intersection_area": round(inter.area, 8),
                    })

    return intersections


def containment_check(
    parcels_gdf: gpd.GeoDataFrame,
    buildings_gdf: gpd.GeoDataFrame
) -> List[Dict]:
    """Check which buildings are fully contained within which parcels.

    Flags buildings that extend beyond parcel boundaries.
    """
    results = []
    sindex = parcels_gdf.sindex

    for b_idx, building in buildings_gdf.iterrows():
        candidates = list(sindex.intersection(building.geometry.bounds))
        contained = False

        for p_idx in candidates:
            parcel = parcels_gdf.iloc[p_idx]
            if parcel.geometry.contains(building.geometry):
                results.append({
                    "building_idx": int(b_idx) if isinstance(b_idx, (int, np.integer)) else str(b_idx),
                    "parcel_idx": str(parcels_gdf.index[p_idx]),
                    "status": "contained",
                    "overlap_pct": 100.0,
                })
                contained = True
                break
            elif parcel.geometry.intersects(building.geometry):
                inter = parcel.geometry.intersection(building.geometry)
                overlap_pct = (inter.area / building.geometry.area) * 100 if building.geometry.area > 0 else 0
                results.append({
                    "building_idx": int(b_idx) if isinstance(b_idx, (int, np.integer)) else str(b_idx),
                    "parcel_idx": str(parcels_gdf.index[p_idx]),
                    "status": "partial" if overlap_pct > 10 else "minimal",
                    "overlap_pct": round(overlap_pct, 2),
                })
                contained = True

        if not contained:
            results.append({
                "building_idx": int(b_idx) if isinstance(b_idx, (int, np.integer)) else str(b_idx),
                "parcel_idx": None,
                "status": "unmatched",
                "overlap_pct": 0.0,
            })

    return results


def calculate_iou(geom_a, geom_b) -> float:
    """Calculate Intersection over Union (IoU) between two geometries.

    Returns value 0.0 to 1.0.
    """
    if geom_a is None or geom_b is None:
        return 0.0
    if geom_a.is_empty or geom_b.is_empty:
        return 0.0

    try:
        intersection = geom_a.intersection(geom_b)
        union = geom_a.union(geom_b)
        if union.area == 0:
            return 0.0
        return intersection.area / union.area
    except Exception:
        return 0.0


def find_nearest_candidates(
    geom,
    gdf: gpd.GeoDataFrame,
    max_distance: float = 0.001,  # ~111 meters in degrees
    max_candidates: int = 10
) -> List[int]:
    """Find candidate matches based on proximity using spatial index.

    Uses spatial constraints before expensive matching (Rules.md §Matching.1).
    """
    sindex = gdf.sindex
    # Buffer the geometry to create a search envelope
    buffered = geom.buffer(max_distance)
    candidates = list(sindex.intersection(buffered.bounds))
    return candidates[:max_candidates]
