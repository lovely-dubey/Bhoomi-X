"""
Standard unittest suite for BHOOMI-X core logic.
Phase 6 Testing requirement (Tasks.md §Phase 6).
"""

import unittest
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from ai.confidence import calculate_confidence, determine_routing, calculate_source_agreement
from ai.attribute_matcher import compare_text_fields, compare_numeric_fields, compare_attributes, match_schema
from ai.explanation import generate_explanation, generate_conflict_explanation


class TestBhoomiXCore(unittest.TestCase):

    def test_confidence_calculation_high(self):
        score, breakdown = calculate_confidence(
            spatial_score=95.0,
            attribute_score=90.0,
            source_agreement=100.0,
            anomaly_flags=None,
        )
        self.assertGreaterEqual(score, 90.0)
        self.assertEqual(breakdown["routing"], "auto_approve")
        self.assertEqual(breakdown["total_penalty"], 0.0)

    def test_confidence_calculation_with_penalties(self):
        score, breakdown = calculate_confidence(
            spatial_score=70.0,
            attribute_score=60.0,
            source_agreement=60.0,
            anomaly_flags={
                "area_mismatch": True,
                "area_mismatch_severity": 12.0,
                "missing_source": True,
                "missing_source_count": 2,
            },
        )
        self.assertEqual(breakdown["total_penalty"], 22.0)
        self.assertLess(score, 60.0)
        self.assertIn(breakdown["routing"], ("escalate", "critical_review", "review"))

    def test_source_agreement(self):
        sources = {"cadastral": True, "revenue": True, "municipal": False, "gnss": True, "drone": False}
        agreement = calculate_source_agreement(sources)
        self.assertEqual(agreement, 60.0)

    def test_attribute_matcher(self):
        # Text fields
        self.assertEqual(compare_text_fields("P-101", "P-101"), 1.0)
        self.assertGreater(compare_text_fields("Sector 17 Commercial", "Sector 17 commercial"), 0.9)

        # Numeric fields
        self.assertGreater(compare_numeric_fields(1000.0, 1005.0), 0.95)
        self.assertLess(compare_numeric_fields(1000.0, 1400.0), 0.8)

        # Schema matching
        mapping = match_schema(["plot_no", "area_sqm"], ["parcel_id", "area"])
        self.assertEqual(mapping["plot_no"], "parcel_id")
        self.assertEqual(mapping["area_sqm"], "area")

        # Full record attribute comparison
        rec_a = {"parcel_id": "P-101", "owner": "Municipal Corp.", "area": 850, "land_use": "Commercial"}
        rec_b = {"parcel_id": "P-101", "owner": "Municipal Corp.", "area": 855, "land_use": "Commercial"}
        attr_score, breakdown = compare_attributes(rec_a, rec_b)
        self.assertGreater(attr_score, 90.0)

    def test_explanation_generator(self):
        match_expl = generate_explanation(
            spatial_score=98.0,
            attribute_score=94.0,
            source_agreement=100.0,
            confidence=96.5,
            sources={"cadastral": True, "revenue": True, "municipal": True, "gnss": True, "drone": True}
        )
        self.assertIn("Confidence: 96%", match_expl)

        conflict_expl = generate_conflict_explanation(
            conflict_type="area_mismatch",
            observed_values={"cadastral": 1000, "drone": 1035},
            severity="high"
        )
        self.assertIn("Area measurements differ", conflict_expl)
        self.assertIn("cadastral: 1000", conflict_expl)


if __name__ == "__main__":
    unittest.main()
