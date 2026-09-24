"""
Confidence Service.
Orchestrates AI confidence scoring for all matched parcels.
Routes low-confidence to review queue, updates parcel status.
"""

from typing import Dict, List
import logging

from ai.confidence import calculate_confidence, calculate_source_agreement, determine_routing
from config import settings

logger = logging.getLogger(__name__)


def score_all_parcels(
    parcel_summaries: Dict[str, Dict],
    anomaly_results: Dict[str, Dict] = None,
) -> Dict[str, Dict]:
    """Score confidence for all parcels and determine routing.

    Args:
        parcel_summaries: {parcel_id: {avg_spatial, avg_attribute, sources, ...}}
        anomaly_results: {parcel_id: {anomaly_flags}}

    Returns: {parcel_id: {confidence, routing, breakdown}}
    """
    anomaly_results = anomaly_results or {}
    results = {}

    for pid, summary in parcel_summaries.items():
        spatial = summary.get("avg_spatial", 0)
        attribute = summary.get("avg_attribute", 0)
        source_agreement = summary.get("source_agreement", 0)
        anomaly_flags = anomaly_results.get(pid, {})

        confidence, breakdown = calculate_confidence(
            spatial, attribute, source_agreement, anomaly_flags
        )

        routing = breakdown.get("routing", determine_routing(confidence))

        # Map routing to parcel status
        status_map = {
            "auto_approve": "validated",
            "review": "review",
            "escalate": "conflict",
            "critical_review": "conflict",
        }

        results[pid] = {
            "confidence": confidence,
            "routing": routing,
            "status": status_map.get(routing, "review"),
            "breakdown": breakdown,
        }

    # Log summary
    statuses = {}
    for r in results.values():
        s = r["status"]
        statuses[s] = statuses.get(s, 0) + 1
    logger.info(f"Confidence scoring complete: {statuses}")

    return results
