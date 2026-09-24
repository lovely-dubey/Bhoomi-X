"""
Matching Service.
Full spatial + attribute matching pipeline per Architecture.md §4.
"""

import geopandas as gpd
from typing import Dict, List, Tuple
import logging

from geo.indexing import SpatialIndex
from geo.spatial_ops import calculate_iou
from ai.spatial_scorer import score_spatial_match
from ai.attribute_matcher import compare_attributes
from ai.confidence import calculate_confidence, calculate_source_agreement
from ai.explanation import generate_explanation
from config import settings

logger = logging.getLogger(__name__)


def match_records(
    parcels_gdf: gpd.GeoDataFrame,
    source_gdf: gpd.GeoDataFrame,
    source_type: str,
) -> List[Dict]:
    """Match source records to parcels using spatial + attribute scoring.

    Pipeline (Architecture.md §4):
    1. Generate spatial candidates via R-tree
    2. Score each pair (spatial + attribute)
    3. Combine into overall score
    4. Apply thresholds
    5. Generate explanations

    Returns list of match records.
    """
    if parcels_gdf.empty or source_gdf.empty:
        return []

    # Build spatial index on parcels
    spatial_idx = SpatialIndex(parcels_gdf)

    # Generate candidates
    candidate_pairs = spatial_idx.candidates_for_matching(source_gdf)

    matches = []
    for src_idx, tgt_idx in candidate_pairs:
        try:
            src_row = source_gdf.iloc[src_idx] if isinstance(src_idx, int) else source_gdf.loc[src_idx]
            tgt_row = parcels_gdf.iloc[tgt_idx]

            src_geom = src_row.geometry
            tgt_geom = tgt_row.geometry

            if src_geom is None or tgt_geom is None:
                continue

            # Spatial score
            spatial_score, spatial_factors = score_spatial_match(src_geom, tgt_geom)

            # Attribute score
            src_attrs = src_row.to_dict() if hasattr(src_row, 'to_dict') else {}
            tgt_attrs = tgt_row.to_dict() if hasattr(tgt_row, 'to_dict') else {}
            attribute_score, attr_breakdown = compare_attributes(src_attrs, tgt_attrs)

            # Source agreement (basic: source present = 1 source agrees)
            source_agreement = 100.0  # Single source always agrees with itself

            # Combined confidence
            confidence, conf_breakdown = calculate_confidence(
                spatial_score, attribute_score, source_agreement
            )

            # Explanation
            explanation = generate_explanation(
                spatial_score, attribute_score, source_agreement, confidence,
            )

            # Determine status
            if confidence >= settings.CONFIDENCE_AUTO_APPROVE:
                status = "confirmed"
            elif confidence >= settings.CONFIDENCE_REVIEW:
                status = "review"
            else:
                status = "proposed"

            parcel_id = tgt_row.get("parcel_id", str(parcels_gdf.index[tgt_idx]))

            match_record = {
                "parcel_id": parcel_id,
                "source_idx": int(src_idx) if isinstance(src_idx, int) else str(src_idx),
                "source_type": source_type,
                "spatial_score": spatial_score,
                "attribute_score": attribute_score,
                "source_agreement": source_agreement,
                "overall_score": confidence,
                "reasons": {
                    "spatial": spatial_factors,
                    "attribute": attr_breakdown,
                    "confidence": conf_breakdown,
                },
                "explanation": explanation,
                "status": status,
            }
            matches.append(match_record)

        except Exception as e:
            logger.error(f"Matching error for pair ({src_idx}, {tgt_idx}): {e}")
            continue

    logger.info(f"Generated {len(matches)} matches from {len(candidate_pairs)} candidates")
    return matches


def aggregate_source_matches(
    all_matches: List[Dict],
    parcel_ids: List[str],
) -> Dict[str, Dict]:
    """Aggregate match results across all sources for each parcel.

    Returns per-parcel summary with multi-source agreement.
    """
    parcel_summaries = {}

    for pid in parcel_ids:
        parcel_matches = [m for m in all_matches if m["parcel_id"] == pid]
        source_types = set(m["source_type"] for m in parcel_matches)

        if not parcel_matches:
            parcel_summaries[pid] = {
                "match_count": 0,
                "sources": {},
                "avg_spatial": 0,
                "avg_attribute": 0,
                "source_agreement": 0,
            }
            continue

        avg_spatial = sum(m["spatial_score"] for m in parcel_matches) / len(parcel_matches)
        avg_attribute = sum(m["attribute_score"] for m in parcel_matches) / len(parcel_matches)

        sources = {
            "cadastral": "cadastral" in source_types,
            "revenue": "revenue" in source_types,
            "municipal": "municipal" in source_types,
            "gnss": "gnss" in source_types,
            "drone": "drone" in source_types,
        }
        source_agreement = calculate_source_agreement(sources)

        parcel_summaries[pid] = {
            "match_count": len(parcel_matches),
            "sources": sources,
            "avg_spatial": round(avg_spatial, 1),
            "avg_attribute": round(avg_attribute, 1),
            "source_agreement": source_agreement,
            "best_overall": max(m["overall_score"] for m in parcel_matches),
        }

    return parcel_summaries
