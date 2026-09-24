"""
CRS Detection and Transformation.
Handles coordinate reference system operations per Architecture.md §4.
Stores CRS metadata and transformation history (Rules.md §Data.5).
"""

import geopandas as gpd
import pyproj
from shapely.geometry import shape
from typing import Optional, Tuple
import logging

from config import settings

logger = logging.getLogger(__name__)


def detect_crs(gdf: gpd.GeoDataFrame) -> Optional[str]:
    """Detect the CRS of a GeoDataFrame.

    Returns EPSG code string (e.g. 'EPSG:4326') or None if undetectable.
    """
    if gdf.crs is not None:
        try:
            epsg = gdf.crs.to_epsg()
            if epsg:
                return f"EPSG:{epsg}"
            # Fallback to WKT representation
            return gdf.crs.to_string()
        except Exception as e:
            logger.warning(f"CRS detection fallback: {e}")
            return gdf.crs.to_string() if gdf.crs else None
    return None


def detect_crs_from_file(filepath: str) -> Optional[str]:
    """Detect CRS directly from a file without loading all data."""
    try:
        import fiona
        with fiona.open(filepath) as src:
            if src.crs:
                crs = pyproj.CRS(src.crs)
                epsg = crs.to_epsg()
                return f"EPSG:{epsg}" if epsg else crs.to_string()
    except Exception as e:
        logger.warning(f"CRS detection from file failed: {e}")
    return None


def transform_to_project_crs(
    gdf: gpd.GeoDataFrame,
    target_crs: str = None
) -> Tuple[gpd.GeoDataFrame, dict]:
    """Transform a GeoDataFrame to the project CRS (default: EPSG:4326).

    Returns:
        (transformed_gdf, transformation_record)

    Preserves original geometry before transformation (Rules.md §Data.4).
    """
    target_crs = target_crs or settings.PROJECT_CRS
    original_crs = detect_crs(gdf) or "unknown"

    transformation_record = {
        "original_crs": original_crs,
        "target_crs": target_crs,
        "transformed": False,
        "records_count": len(gdf),
    }

    if gdf.crs is None:
        # Assume WGS84 if no CRS (common for CSV imports)
        logger.warning("No CRS detected, assuming EPSG:4326")
        gdf = gdf.set_crs("EPSG:4326")
        transformation_record["assumed_crs"] = "EPSG:4326"

    if gdf.crs.to_epsg() != pyproj.CRS(target_crs).to_epsg():
        gdf = gdf.to_crs(target_crs)
        transformation_record["transformed"] = True
        logger.info(f"Transformed CRS: {original_crs} → {target_crs}")
    else:
        logger.info(f"CRS already {target_crs}, no transformation needed")

    return gdf, transformation_record


def transform_to_utm(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Transform to local UTM CRS for accurate metric calculations (area, distance).

    Uses the UTM zone configured for the pilot area.
    """
    return gdf.to_crs(settings.LOCAL_UTM_CRS)


def get_utm_zone(lon: float, lat: float) -> str:
    """Auto-detect UTM zone from longitude/latitude."""
    zone_number = int((lon + 180) / 6) + 1
    hemisphere = "north" if lat >= 0 else "south"
    epsg = 32600 + zone_number if hemisphere == "north" else 32700 + zone_number
    return f"EPSG:{epsg}"
