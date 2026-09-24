"""
Spatial Candidate Scoring.
Calculates composite spatial similarity using overlap, distance, area ratio, geometry similarity.
A high spatial score alone must not guarantee a final match (Rules.md §Matching.3).
"""

from shapely.geometry import shape
from geo.spatial_ops import calculate_iou
from typing import Dict, Tuple
import math
import logging

logger = logging.getLogger(__name__)


def score_spatial_match(geom_a, geom_b) -> Tuple[float, Dict]:
    """Calculate a composite spatial similarity score (0-100).

    Components:
    - IoU (Intersection over Union): 40%
    - Centroid distance: 20%
    - Area ratio: 20%
    - Shape similarity (compactness): 20%

    Returns:
        (spatial_score, contributing_factors)
    """
    if geom_a is None or geom_b is None or geom_a.is_empty or geom_b.is_empty:
        return 0.0, {"error": "One or both geometries are empty"}

    factors = {}

    # 1. IoU (40% weight)
    iou = calculate_iou(geom_a, geom_b)
    factors["iou"] = round(iou * 100, 1)

    # 2. Centroid distance (20% weight)
    centroid_dist = geom_a.centroid.distance(geom_b.centroid)
    # Normalize: 0 distance = 100%, >0.001 deg (~111m) = 0%
    max_dist = 0.001
    centroid_score = max(0, 1 - (centroid_dist / max_dist)) if centroid_dist < max_dist else 0
    factors["centroid_distance_deg"] = round(centroid_dist, 6)
    factors["centroid_score"] = round(centroid_score * 100, 1)

    # 3. Area ratio (20% weight)
    area_a = geom_a.area
    area_b = geom_b.area
    if max(area_a, area_b) > 0:
        area_ratio = min(area_a, area_b) / max(area_a, area_b)
    else:
        area_ratio = 0
    factors["area_ratio"] = round(area_ratio * 100, 1)
    factors["area_a"] = round(area_a, 8)
    factors["area_b"] = round(area_b, 8)

    # 4. Shape similarity via compactness (Polsby-Popper) (20% weight)
    def compactness(geom):
        if geom.area == 0 or geom.length == 0:
            return 0
        return (4 * math.pi * geom.area) / (geom.length ** 2)

    comp_a = compactness(geom_a)
    comp_b = compactness(geom_b)
    if max(comp_a, comp_b) > 0:
        shape_sim = 1 - abs(comp_a - comp_b) / max(comp_a, comp_b)
    else:
        shape_sim = 0
    shape_sim = max(0, shape_sim)
    factors["shape_similarity"] = round(shape_sim * 100, 1)

    # Weighted composite
    spatial_score = (
        0.40 * (iou * 100) +
        0.20 * (centroid_score * 100) +
        0.20 * (area_ratio * 100) +
        0.20 * (shape_sim * 100)
    )

    factors["composite_score"] = round(spatial_score, 1)

    return round(spatial_score, 1), factors


def score_overlap_only(geom_a, geom_b) -> float:
    """Quick overlap percentage between two geometries."""
    if geom_a is None or geom_b is None:
        return 0.0
    try:
        intersection = geom_a.intersection(geom_b)
        if geom_a.area == 0:
            return 0.0
        return round((intersection.area / geom_a.area) * 100, 1)
    except Exception:
        return 0.0
