"""
Attribute Schema Matching and Record Similarity.
Compares parcel identifiers, owner/holder fields, area, land use (FR-05).
AI must not invent missing attributes (Rules.md §AI.4).
"""

from difflib import SequenceMatcher
import re
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Common field name aliases in land records
FIELD_ALIASES = {
    "parcel_id": ["parcel_id", "plot_no", "survey_no", "khasra_no", "gat_no", "plot_id", "id", "parcel_number"],
    "owner": ["owner", "holder", "pattadar", "khatedar", "owner_name", "proprietor", "occupant"],
    "area": ["area", "area_sqm", "area_m2", "plot_area", "extent", "area_sqft", "area_acres"],
    "land_use": ["land_use", "landuse", "use_type", "classification", "category", "zone", "type"],
    "address": ["address", "location", "village", "ward", "mohalla", "sector"],
}


def match_schema(columns_a: List[str], columns_b: List[str]) -> Dict[str, Optional[str]]:
    """Match field names between two schemas using fuzzy matching and known aliases.

    Returns a mapping: {field_a: best_matching_field_b_or_None}
    """
    mapping = {}

    for col_a in columns_a:
        best_match = None
        best_score = 0.0
        col_a_lower = col_a.lower().strip()

        for col_b in columns_b:
            col_b_lower = col_b.lower().strip()

            # Direct match
            if col_a_lower == col_b_lower:
                best_match = col_b
                best_score = 1.0
                break

            # Alias match
            for canonical, aliases in FIELD_ALIASES.items():
                if col_a_lower in aliases and col_b_lower in aliases:
                    best_match = col_b
                    best_score = 0.95
                    break

            if best_score >= 0.95:
                break

            # Fuzzy match
            score = SequenceMatcher(None, col_a_lower, col_b_lower).ratio()
            if score > best_score and score > 0.6:
                best_match = col_b
                best_score = score

        mapping[col_a] = best_match

    return mapping


def normalize_text(text: str) -> str:
    """Normalize text for comparison — lowercase, remove extra spaces, basic transliteration."""
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text


def compare_text_fields(val_a: str, val_b: str) -> float:
    """Compare two text values and return a similarity score (0-1)."""
    if not val_a or not val_b:
        return 0.0

    norm_a = normalize_text(val_a)
    norm_b = normalize_text(val_b)

    if norm_a == norm_b:
        return 1.0

    # Check if one contains the other
    if norm_a in norm_b or norm_b in norm_a:
        return 0.85

    return SequenceMatcher(None, norm_a, norm_b).ratio()


def compare_numeric_fields(val_a: float, val_b: float, tolerance: float = 0.05) -> float:
    """Compare two numeric values within a tolerance.

    Returns 1.0 for exact match, scaled down based on discrepancy.
    """
    if val_a is None or val_b is None:
        return 0.0
    if val_a == 0 and val_b == 0:
        return 1.0

    max_val = max(abs(val_a), abs(val_b))
    if max_val == 0:
        return 1.0

    diff_pct = abs(val_a - val_b) / max_val

    if diff_pct <= tolerance:
        return 1.0 - (diff_pct / tolerance) * 0.2  # 0.8-1.0 range within tolerance
    else:
        return max(0.0, 1.0 - diff_pct)  # Linear falloff beyond tolerance


def compare_attributes(
    record_a: Dict,
    record_b: Dict,
    field_mapping: Optional[Dict[str, str]] = None
) -> Tuple[float, Dict]:
    """Compare all comparable attributes between two records.

    Returns:
        (attribute_score 0-100, per_field_breakdown)

    Uses multiple evidence signals (Rules.md §Matching.2).
    """
    scores = {}
    weights = {}

    # ID comparison (weight: 30%)
    id_a = record_a.get("external_id") or record_a.get("parcel_id") or ""
    id_b = record_b.get("external_id") or record_b.get("parcel_id") or ""
    if id_a and id_b:
        scores["id"] = compare_text_fields(str(id_a), str(id_b))
        weights["id"] = 0.30

    # Owner comparison (weight: 25%)
    owner_a = record_a.get("owner", "")
    owner_b = record_b.get("owner", "")
    if owner_a and owner_b:
        scores["owner"] = compare_text_fields(owner_a, owner_b)
        weights["owner"] = 0.25

    # Area comparison (weight: 25%)
    area_a = record_a.get("area")
    area_b = record_b.get("area")
    if area_a is not None and area_b is not None:
        scores["area"] = compare_numeric_fields(float(area_a), float(area_b))
        weights["area"] = 0.25

    # Land use comparison (weight: 20%)
    lu_a = record_a.get("land_use", "")
    lu_b = record_b.get("land_use", "")
    if lu_a and lu_b:
        scores["land_use"] = compare_text_fields(lu_a, lu_b)
        weights["land_use"] = 0.20

    # Weighted average
    if not scores:
        return 0.0, {"note": "No comparable attributes found"}

    total_weight = sum(weights.values())
    if total_weight == 0:
        return 0.0, scores

    weighted_sum = sum(scores[k] * weights[k] for k in scores)
    attribute_score = (weighted_sum / total_weight) * 100

    breakdown = {k: round(v * 100, 1) for k, v in scores.items()}
    breakdown["weighted_score"] = round(attribute_score, 1)

    return round(attribute_score, 1), breakdown
