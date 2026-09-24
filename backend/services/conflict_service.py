"""
Conflict Detection Service.
Flags area mismatch, boundary mismatch, missing records, duplicates, land use conflicts (FR-06).
Conflicting authoritative-looking records must be flagged, not silently resolved (Rules.md §Matching.4).
"""

from typing import Dict, List
import logging

from ai.anomaly_detector import detect_area_mismatch, detect_boundary_mismatch
from ai.explanation import generate_conflict_explanation
from config import settings

logger = logging.getLogger(__name__)


def detect_conflicts(parcel_data: List[Dict]) -> List[Dict]:
    """Run all conflict detection rules on a list of parcel records.

    Each parcel_data entry should contain:
    - parcel_id
    - areas: {source: area_value}
    - sources: {source: bool}
    - boundary_metrics: {hausdorff_distance, ...}  (optional)
    - land_use_by_source: {source: land_use}  (optional)
    - owner_by_source: {source: owner}  (optional)

    Returns list of Conflict dicts.
    """
    conflicts = []

    for parcel in parcel_data:
        pid = parcel.get("parcel_id", "unknown")

        # 1. Area mismatch detection
        areas = parcel.get("areas", {})
        if areas:
            is_mismatch, area_details = detect_area_mismatch(areas)
            if is_mismatch:
                severity = _area_severity(area_details.get("range_pct", 0))
                conflicts.append({
                    "parcel_id": pid,
                    "conflict_type": "area_mismatch",
                    "severity": severity,
                    "observed_values": area_details,
                    "sources_involved": ", ".join(f"{k}" for k in areas.keys()),
                    "recommended_action": _area_action(severity),
                    "explanation": generate_conflict_explanation("area_mismatch", area_details, severity),
                })

        # 2. Missing source detection
        sources = parcel.get("sources", {})
        missing = [k for k, v in sources.items() if not v]
        if missing:
            conflicts.append({
                "parcel_id": pid,
                "conflict_type": "missing_record",
                "severity": "high" if len(missing) >= 2 else "medium",
                "observed_values": {"missing_from": missing, "present_in": [k for k, v in sources.items() if v]},
                "sources_involved": ", ".join(f"{m} (absent)" for m in missing),
                "recommended_action": f"Request records from: {', '.join(missing)}",
                "explanation": generate_conflict_explanation("missing_record", {"missing_from": ", ".join(missing)}, "high"),
            })

        # 3. Land use conflict
        land_uses = parcel.get("land_use_by_source", {})
        unique_uses = set(v.lower().strip() for v in land_uses.values() if v)
        if len(unique_uses) > 1:
            conflicts.append({
                "parcel_id": pid,
                "conflict_type": "land_use_conflict",
                "severity": "medium",
                "observed_values": land_uses,
                "sources_involved": ", ".join(land_uses.keys()),
                "recommended_action": "Verify current land use classification via field inspection",
                "explanation": generate_conflict_explanation("land_use_conflict", land_uses, "medium"),
            })

        # 4. Ownership dispute
        owners = parcel.get("owner_by_source", {})
        unique_owners = set(v.lower().strip() for v in owners.values() if v)
        if len(unique_owners) > 1:
            conflicts.append({
                "parcel_id": pid,
                "conflict_type": "ownership_dispute",
                "severity": "high",
                "observed_values": owners,
                "sources_involved": ", ".join(owners.keys()),
                "recommended_action": "Legal review and title verification required",
                "explanation": generate_conflict_explanation("ownership_dispute", owners, "high"),
            })

        # 5. Boundary mismatch
        boundary = parcel.get("boundary_metrics", {})
        hausdorff = boundary.get("hausdorff_distance", 0)
        if hausdorff > 0:
            is_mismatch, boundary_details = detect_boundary_mismatch(hausdorff)
            if is_mismatch:
                severity = "high" if boundary_details.get("hausdorff_m_approx", 0) > 5 else "medium"
                conflicts.append({
                    "parcel_id": pid,
                    "conflict_type": "boundary_mismatch",
                    "severity": severity,
                    "observed_values": boundary_details,
                    "sources_involved": boundary.get("sources", "Multiple"),
                    "recommended_action": "Resurvey with DGPS for accurate boundary determination",
                    "explanation": generate_conflict_explanation("boundary_mismatch", boundary_details, severity),
                })

    logger.info(f"Detected {len(conflicts)} conflicts across {len(parcel_data)} parcels")
    return conflicts


def _area_severity(range_pct: float) -> str:
    """Determine severity based on area discrepancy percentage."""
    if range_pct > 10:
        return "critical"
    elif range_pct > 7:
        return "high"
    elif range_pct > 5:
        return "medium"
    return "low"


def _area_action(severity: str) -> str:
    """Recommended action based on severity."""
    actions = {
        "critical": "Immediate field survey and legal review required",
        "high": "Field survey to verify boundary",
        "medium": "Cross-reference with recent survey data",
        "low": "Review measurements for rounding/precision differences",
    }
    return actions.get(severity, "Review area measurements")
