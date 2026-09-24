"""
Anomaly Detection using Isolation Forest.
Detects unusual parcels, area mismatches, and boundary inconsistencies.
All model thresholds must be configurable and testable (Rules.md §AI.7).
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Dict, List, Tuple
import logging

from config import settings

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Isolation Forest based anomaly detector for parcel data."""

    def __init__(self, contamination: float = 0.1):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100,
        )
        self.is_fitted = False

    def fit(self, features: np.ndarray):
        """Fit the model on parcel features."""
        if len(features) < 5:
            logger.warning("Not enough data to fit anomaly detector (need >= 5)")
            return
        self.model.fit(features)
        self.is_fitted = True
        logger.info(f"Anomaly detector fitted on {len(features)} samples")

    def predict(self, features: np.ndarray) -> np.ndarray:
        """Predict anomaly labels. -1 = anomaly, 1 = normal."""
        if not self.is_fitted:
            return np.ones(len(features))
        return self.model.predict(features)

    def score_samples(self, features: np.ndarray) -> np.ndarray:
        """Get anomaly scores. Lower = more anomalous."""
        if not self.is_fitted:
            return np.zeros(len(features))
        return self.model.score_samples(features)


def extract_parcel_features(parcel_data: List[Dict]) -> np.ndarray:
    """Extract feature vectors from parcel data for anomaly detection.

    Features: [area, perimeter_proxy, aspect_ratio, vertex_count, area_discrepancy]
    """
    features = []
    for p in parcel_data:
        area = p.get("area", 0) or 0
        # Use area as proxy for perimeter (sqrt relationship)
        perimeter_proxy = np.sqrt(area) * 4 if area > 0 else 0
        vertex_count = p.get("vertex_count", 4)
        area_discrepancy = p.get("area_discrepancy", 0) or 0
        confidence = p.get("confidence", 50)

        features.append([
            area,
            perimeter_proxy,
            vertex_count,
            area_discrepancy,
            confidence,
        ])

    return np.array(features) if features else np.empty((0, 5))


def detect_area_mismatch(
    areas: Dict[str, float],
    threshold: float = None
) -> Tuple[bool, Dict]:
    """Detect area mismatch across multiple source measurements.

    Args:
        areas: Dict of {source_name: area_value}
        threshold: Max allowed fractional discrepancy (default from config)

    Returns:
        (is_mismatch, details)
    """
    threshold = threshold or settings.AREA_MISMATCH_THRESHOLD
    valid_areas = {k: v for k, v in areas.items() if v is not None and v > 0}

    if len(valid_areas) < 2:
        return False, {"note": "Insufficient sources for comparison"}

    values = list(valid_areas.values())
    mean_area = np.mean(values)
    max_area = max(values)
    min_area = min(values)
    range_pct = (max_area - min_area) / mean_area if mean_area > 0 else 0
    std_pct = np.std(values) / mean_area if mean_area > 0 else 0

    is_mismatch = range_pct > threshold

    return is_mismatch, {
        "areas": valid_areas,
        "mean_area": round(mean_area, 2),
        "max_area": round(max_area, 2),
        "min_area": round(min_area, 2),
        "range_pct": round(range_pct * 100, 2),
        "std_pct": round(std_pct * 100, 2),
        "threshold_pct": round(threshold * 100, 2),
        "is_mismatch": is_mismatch,
    }


def detect_boundary_mismatch(
    hausdorff_distance: float,
    threshold_m: float = None
) -> Tuple[bool, Dict]:
    """Detect boundary mismatch based on Hausdorff distance.

    Args:
        hausdorff_distance: Max distance between boundaries (in CRS units)
        threshold_m: Max allowed distance in meters

    Returns:
        (is_mismatch, details)
    """
    threshold_m = threshold_m or settings.BOUNDARY_MISMATCH_THRESHOLD
    # Approximate conversion: 1 degree ≈ 111,000 meters at equator
    distance_approx_m = hausdorff_distance * 111000

    is_mismatch = distance_approx_m > threshold_m

    return is_mismatch, {
        "hausdorff_deg": round(hausdorff_distance, 6),
        "hausdorff_m_approx": round(distance_approx_m, 2),
        "threshold_m": threshold_m,
        "is_mismatch": is_mismatch,
    }
