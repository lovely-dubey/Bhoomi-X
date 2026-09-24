"""
Confidence Score Calculator.
Weighted composite: overall = 0.50*spatial + 0.30*attribute + 0.20*source_agreement (Architecture.md §4).
Weights are configurable and must be validated on labelled test data.
"""

from typing import Dict, Tuple
from config import settings
import logging

logger = logging.getLogger(__name__)


def calculate_confidence(
    spatial_score: float,
    attribute_score: float,
    source_agreement: float,
    anomaly_flags: Dict = None,
) -> Tuple[float, Dict]:
    """Calculate composite confidence score with configurable weights.

    Args:
        spatial_score: 0-100
        attribute_score: 0-100
        source_agreement: 0-100
        anomaly_flags: Dict of anomaly indicators that apply penalties

    Returns:
        (confidence_score 0-100, breakdown)
    """
    w_spatial = settings.SPATIAL_WEIGHT
    w_attribute = settings.ATTRIBUTE_WEIGHT
    w_source = settings.SOURCE_AGREEMENT_WEIGHT

    # Base weighted score
    base_score = (
        w_spatial * spatial_score +
        w_attribute * attribute_score +
        w_source * source_agreement
    )

    # Apply anomaly penalties
    penalty = 0.0
    penalties = {}
    if anomaly_flags:
        if anomaly_flags.get("area_mismatch"):
            p = min(15.0, anomaly_flags.get("area_mismatch_severity", 10))
            penalty += p
            penalties["area_mismatch"] = -p

        if anomaly_flags.get("boundary_mismatch"):
            p = min(15.0, anomaly_flags.get("boundary_mismatch_severity", 10))
            penalty += p
            penalties["boundary_mismatch"] = -p

        if anomaly_flags.get("missing_source"):
            count = anomaly_flags.get("missing_source_count", 1)
            p = count * 5.0
            penalty += p
            penalties["missing_sources"] = -p

        if anomaly_flags.get("isolation_forest_anomaly"):
            penalty += 8.0
            penalties["statistical_anomaly"] = -8.0

    final_score = max(0.0, min(100.0, base_score - penalty))

    # Determine routing decision
    routing = determine_routing(final_score)

    breakdown = {
        "spatial_contribution": round(w_spatial * spatial_score, 1),
        "attribute_contribution": round(w_attribute * attribute_score, 1),
        "source_contribution": round(w_source * source_agreement, 1),
        "base_score": round(base_score, 1),
        "penalties": penalties,
        "total_penalty": round(penalty, 1),
        "final_score": round(final_score, 1),
        "routing": routing,
        "weights": {
            "spatial": w_spatial,
            "attribute": w_attribute,
            "source_agreement": w_source,
        },
    }

    return round(final_score, 1), breakdown


def determine_routing(confidence: float) -> str:
    """Determine where to route based on confidence score.

    Low-confidence matches require human review (Rules.md §AI.3).
    """
    if confidence >= settings.CONFIDENCE_AUTO_APPROVE:
        return "auto_approve"
    elif confidence >= settings.CONFIDENCE_REVIEW:
        return "review"
    elif confidence >= settings.CONFIDENCE_ESCALATE:
        return "escalate"
    else:
        return "critical_review"


def calculate_source_agreement(sources: Dict[str, bool]) -> float:
    """Calculate source agreement percentage.

    Returns: 0-100 based on how many expected sources have data.
    """
    total = len(sources)
    if total == 0:
        return 0.0
    present = sum(1 for v in sources.values() if v)
    return round((present / total) * 100, 1)
