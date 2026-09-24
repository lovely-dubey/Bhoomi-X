"""
Spatial Indexing with R-tree (STRtree) for fast candidate generation.
Candidate generation must use spatial constraints before expensive matching (Rules.md §Matching.1).
"""

import geopandas as gpd
from shapely import STRtree
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class SpatialIndex:
    """R-tree spatial index for efficient candidate generation."""

    def __init__(self, gdf: gpd.GeoDataFrame):
        """Build an STRtree index from a GeoDataFrame."""
        self.gdf = gdf
        self.geometries = list(gdf.geometry)
        self.tree = STRtree(self.geometries)
        self.index_to_id = {i: idx for i, idx in enumerate(gdf.index)}
        logger.info(f"Built spatial index with {len(self.geometries)} geometries")

    def query(self, geom, predicate: str = "intersects") -> List[int]:
        """Query the index for geometries matching the predicate.

        Args:
            geom: Query geometry
            predicate: 'intersects', 'contains', 'within', 'touches', 'overlaps'

        Returns:
            List of indices into the original GeoDataFrame
        """
        result_indices = self.tree.query(geom, predicate=predicate)
        return result_indices.tolist() if hasattr(result_indices, 'tolist') else list(result_indices)

    def nearest(self, geom, k: int = 5) -> List[int]:
        """Find k nearest geometries to the query geometry."""
        result_indices = self.tree.nearest(geom, k)
        if hasattr(result_indices, 'tolist'):
            return result_indices.tolist()
        return [result_indices] if isinstance(result_indices, int) else list(result_indices)

    def candidates_for_matching(
        self,
        source_gdf: gpd.GeoDataFrame,
        max_per_record: int = 10
    ) -> List[Tuple[int, int]]:
        """Generate candidate match pairs between source records and indexed parcels.

        Returns list of (source_idx, target_idx) pairs for further scoring.
        """
        pairs = []
        for src_idx, src_row in source_gdf.iterrows():
            candidates = self.query(src_row.geometry, predicate="intersects")
            if not candidates:
                # Fall back to nearest neighbors
                candidates = self.nearest(src_row.geometry, k=3)

            for tgt_idx in candidates[:max_per_record]:
                pairs.append((src_idx, tgt_idx))

        logger.info(f"Generated {len(pairs)} candidate pairs from {len(source_gdf)} source records")
        return pairs
