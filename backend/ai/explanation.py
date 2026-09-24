"""
Explainable Recommendation Generator.
AI must be explainable at the decision level (Rules.md §AI.1).
Do not present a recommendation as an authoritative fact (Rules.md §AI.5).
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


# Templates for natural language explanations
TEMPLATES = {
    "high_agreement": (
        "All sources show strong agreement for this parcel. "
        "Spatial overlap is {spatial}%, attribute similarity is {attribute}%, "
        "and {source_count} out of {total_sources} sources agree. "
        "Confidence: {confidence}%."
    ),
    "moderate_discrepancy": (
        "Moderate discrepancy detected. "
        "Spatial match is {spatial}% but attribute similarity drops to {attribute}%. "
        "{discrepancy_detail} "
        "Human review is recommended to verify {focus_area}."
    ),
    "area_mismatch": (
        "Area mismatch detected across sources: {area_details}. "
        "Maximum discrepancy is {max_discrepancy}%. "
        "{action}"
    ),
    "boundary_mismatch": (
        "Boundary discrepancy detected. "
        "Hausdorff distance between boundaries is approximately {distance}m. "
        "{action}"
    ),
    "missing_source": (
        "Missing record from {missing_source}. "
        "Available sources ({available_count}) show {agreement_level} agreement. "
        "{action}"
    ),
    "critical_conflict": (
        "CRITICAL: {conflict_detail}. "
        "Multiple evidence signals indicate significant inconsistency. "
        "Immediate {action_type} recommended."
    ),
    "land_use_change": (
        "Land use change detected: {previous} → {current}. "
        "Revenue records show previous classification as \"{previous}\". "
        "Current imagery confirms {current} structures. "
        "Temporal change documented."
    ),
}


def generate_explanation(
    spatial_score: float,
    attribute_score: float,
    source_agreement: float,
    confidence: float,
    conflict_details: Optional[Dict] = None,
    area_analysis: Optional[Dict] = None,
    sources: Optional[Dict[str, bool]] = None,
) -> str:
    """Generate a human-readable explanation for a match/harmonization result.

    Returns a natural language explanation that covers:
    - What evidence supports the match
    - What inconsistencies were found
    - Why the confidence score is what it is
    - What action is recommended
    """
    total_sources = 5
    source_count = sum(1 for v in (sources or {}).values() if v)
    missing = [k for k, v in (sources or {}).items() if not v]

    explanations = []

    # High confidence path
    if confidence >= 90:
        explanations.append(TEMPLATES["high_agreement"].format(
            spatial=round(spatial_score),
            attribute=round(attribute_score),
            source_count=source_count,
            total_sources=total_sources,
            confidence=round(confidence),
        ))

    # Area mismatch
    if area_analysis and area_analysis.get("is_mismatch"):
        areas = area_analysis.get("areas", {})
        area_str = ", ".join(f"{k}: {v} m²" for k, v in areas.items())
        explanations.append(TEMPLATES["area_mismatch"].format(
            area_details=area_str,
            max_discrepancy=area_analysis.get("range_pct", 0),
            action="Field survey recommended to verify actual boundary." if area_analysis.get("range_pct", 0) > 5 else "Minor variance within acceptable tolerance."
        ))

    # Missing sources
    if missing:
        agreement_level = "strong" if source_agreement > 80 else "moderate" if source_agreement > 60 else "weak"
        explanations.append(TEMPLATES["missing_source"].format(
            missing_source=", ".join(missing),
            available_count=source_count,
            agreement_level=agreement_level,
            action=f"Request {', '.join(missing)} records for complete reconciliation."
        ))

    # Moderate discrepancy
    if 50 <= confidence < 90 and not explanations:
        focus = "boundary alignment" if spatial_score < attribute_score else "attribute consistency"
        detail = ""
        if area_analysis:
            detail = f"Area range across sources is {area_analysis.get('range_pct', 0)}%."
        explanations.append(TEMPLATES["moderate_discrepancy"].format(
            spatial=round(spatial_score),
            attribute=round(attribute_score),
            discrepancy_detail=detail,
            focus_area=focus,
        ))

    # Critical
    if confidence < 50:
        detail = conflict_details.get("explanation", "Multiple sources disagree significantly") if conflict_details else "Low confidence across all matching criteria"
        explanations.append(TEMPLATES["critical_conflict"].format(
            conflict_detail=detail,
            action_type="field verification and legal review",
        ))

    if not explanations:
        explanations.append(
            f"Spatial match: {round(spatial_score)}%, Attribute match: {round(attribute_score)}%, "
            f"Source agreement: {round(source_agreement)}%. Confidence: {round(confidence)}%."
        )

    return " ".join(explanations)


def generate_conflict_explanation(
    conflict_type: str,
    observed_values: Dict,
    severity: str
) -> str:
    """Generate explanation for a specific conflict."""
    explanations = {
        "area_mismatch": f"Area measurements differ across sources. Observed values: {_format_values(observed_values)}. This may indicate boundary errors or outdated records.",
        "boundary_mismatch": f"Parcel boundaries do not align across sources. Vertex positions differ by {observed_values.get('hausdorff_m_approx', 'N/A')}m. Possible causes: different survey epochs, projection errors, or actual boundary changes.",
        "missing_record": f"Record is missing from: {observed_values.get('missing_from', 'unknown')}. This may indicate the record was never registered, was deleted, or uses a different identifier.",
        "duplicate_id": f"Duplicate parcel identifier found: {observed_values.get('duplicate_id', 'N/A')}. Multiple records share the same ID across different sources.",
        "land_use_conflict": f"Land use classification disagrees: {_format_values(observed_values)}. Possible land use change or classification error.",
        "encroachment": f"Building footprint extends beyond recorded parcel boundary. Excess area: {observed_values.get('excess_area', 'N/A')} m². Possible unauthorized construction.",
        "ownership_dispute": f"Owner/holder fields conflict across sources: {_format_values(observed_values)}. Legal review may be required.",
    }

    return explanations.get(conflict_type, f"Conflict detected: {conflict_type}. Details: {_format_values(observed_values)}")


def _format_values(values: Dict) -> str:
    """Format a dict of values into a readable string."""
    return ", ".join(f"{k}: {v}" for k, v in values.items() if v is not None)
