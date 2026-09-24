"""
BHOOMI-X Backend Configuration
Loads settings from environment variables / .env file.
All matching weights and thresholds are configurable per Architecture.md §4.
"""

try:
    from pydantic_settings import BaseSettings
except ImportError:
    try:
        from pydantic import BaseModel as BaseSettings
    except ImportError:
        class BaseSettings:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)
from typing import Optional


class Settings(BaseSettings):
    """Application settings with sensible defaults for development."""

    # ─── Database ───
    DATABASE_URL: str = "postgresql+asyncpg://bhoomix:bhoomix_dev_2026@localhost:5432/bhoomix"
    DATABASE_URL_SYNC: str = "postgresql://bhoomix:bhoomix_dev_2026@localhost:5432/bhoomix"

    # ─── Environment ───
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # ─── Matching Pipeline Weights (must sum to 1.0) ───
    SPATIAL_WEIGHT: float = 0.50
    ATTRIBUTE_WEIGHT: float = 0.30
    SOURCE_AGREEMENT_WEIGHT: float = 0.20

    # ─── Confidence Thresholds ───
    CONFIDENCE_AUTO_APPROVE: float = 90.0
    CONFIDENCE_REVIEW: float = 70.0
    CONFIDENCE_ESCALATE: float = 50.0

    # ─── Conflict Detection Thresholds ───
    AREA_MISMATCH_THRESHOLD: float = 0.05       # 5% area discrepancy
    BOUNDARY_MISMATCH_THRESHOLD: float = 2.0    # meters (Hausdorff distance)

    # ─── CRS ───
    PROJECT_CRS: str = "EPSG:4326"              # WGS 84
    LOCAL_UTM_CRS: str = "EPSG:32643"           # UTM Zone 43N (Chandigarh)

    # ─── File Upload ───
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 100

    model_config = {
        "env_file": [".env", "../.env"],
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }


settings = Settings()
