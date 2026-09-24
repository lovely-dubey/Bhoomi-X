"""
Seed Database with Chandigarh Demo Data.
Loads synthetic parcels, buildings, conflicts, and source records into PostGIS.
Data is clearly labelled as synthetic (Rules.md §Data.1, Memory.md §Prototype Data Strategy).
"""

import json
import os
from pathlib import Path
from shapely.geometry import shape, Polygon
from geoalchemy2.shape import from_shape
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
import logging

from models.parcel import Parcel, SourceRecord
from models.conflict import Conflict
from models.review import AuditLog

logger = logging.getLogger(__name__)

SEED_DIR = Path(__file__).parent

# ─── Chandigarh Sector 17 Parcels ───
PARCELS_DATA = [
    {"id":"P-101","status":"validated","confidence":97,"area":850,"land_use":"Commercial","owner":"Municipal Corp.","coords":[[76.7760,30.7440],[76.7775,30.7440],[76.7775,30.7430],[76.7760,30.7430],[76.7760,30.7440]]},
    {"id":"P-102","status":"validated","confidence":95,"area":1200,"land_use":"Commercial","owner":"State Govt.","coords":[[76.7780,30.7440],[76.7798,30.7440],[76.7798,30.7430],[76.7780,30.7430],[76.7780,30.7440]]},
    {"id":"P-103","status":"review","confidence":74,"area":960,"land_use":"Mixed Use","owner":"Private","coords":[[76.7802,30.7440],[76.7818,30.7440],[76.7818,30.7430],[76.7802,30.7430],[76.7802,30.7440]]},
    {"id":"P-104","status":"conflict","confidence":58,"area":1000,"land_use":"Residential","owner":"Private","coords":[[76.7760,30.7425],[76.7780,30.7425],[76.7780,30.7415],[76.7760,30.7415],[76.7760,30.7425]]},
    {"id":"P-105","status":"validated","confidence":99,"area":700,"land_use":"Commercial","owner":"Municipal Corp.","coords":[[76.7785,30.7425],[76.7800,30.7425],[76.7800,30.7415],[76.7785,30.7415],[76.7785,30.7425]]},
    {"id":"P-106","status":"validated","confidence":93,"area":1100,"land_use":"Commercial","owner":"Private","coords":[[76.7805,30.7425],[76.7822,30.7425],[76.7822,30.7415],[76.7805,30.7415],[76.7805,30.7425]]},
    {"id":"P-107","status":"conflict","confidence":45,"area":1400,"land_use":"Institutional","owner":"State Govt.","coords":[[76.7760,30.7413],[76.7782,30.7413],[76.7782,30.7403],[76.7760,30.7403],[76.7760,30.7413]]},
    {"id":"P-108","status":"review","confidence":72,"area":550,"land_use":"Residential","owner":"Private","coords":[[76.7788,30.7413],[76.7800,30.7413],[76.7800,30.7403],[76.7788,30.7403],[76.7788,30.7413]]},
    {"id":"P-109","status":"validated","confidence":91,"area":800,"land_use":"Commercial","owner":"Private","coords":[[76.7805,30.7413],[76.7820,30.7413],[76.7820,30.7403],[76.7805,30.7403],[76.7805,30.7413]]},
    {"id":"P-110","status":"changed","confidence":88,"area":650,"land_use":"Commercial","owner":"Municipal Corp.","coords":[[76.7768,30.7400],[76.7782,30.7400],[76.7782,30.7392],[76.7768,30.7392],[76.7768,30.7400]]},
    {"id":"P-111","status":"validated","confidence":96,"area":900,"land_use":"Residential","owner":"Private","coords":[[76.7786,30.7400],[76.7800,30.7400],[76.7800,30.7392],[76.7786,30.7392],[76.7786,30.7400]]},
    {"id":"P-112","status":"conflict","confidence":52,"area":1300,"land_use":"Residential","owner":"Private","coords":[[76.7804,30.7400],[76.7822,30.7400],[76.7822,30.7392],[76.7804,30.7392],[76.7804,30.7400]]},
    {"id":"P-113","status":"review","confidence":69,"area":780,"land_use":"Mixed Use","owner":"Private","coords":[[76.7762,30.7390],[76.7776,30.7390],[76.7776,30.7382],[76.7762,30.7382],[76.7762,30.7390]]},
    {"id":"P-114","status":"validated","confidence":94,"area":1050,"land_use":"Commercial","owner":"Municipal Corp.","coords":[[76.7780,30.7390],[76.7798,30.7390],[76.7798,30.7382],[76.7780,30.7382],[76.7780,30.7390]]},
    {"id":"P-115","status":"changed","confidence":85,"area":500,"land_use":"Residential","owner":"Private","coords":[[76.7802,30.7390],[76.7812,30.7390],[76.7812,30.7382],[76.7802,30.7382],[76.7802,30.7390]]},
    {"id":"P-116","status":"validated","confidence":98,"area":1500,"land_use":"Institutional","owner":"State Govt.","coords":[[76.7815,30.7390],[76.7838,30.7390],[76.7838,30.7380],[76.7815,30.7380],[76.7815,30.7390]]},
    {"id":"P-117","status":"review","confidence":68,"area":620,"land_use":"Residential","owner":"Private","coords":[[76.7765,30.7448],[76.7778,30.7448],[76.7778,30.7442],[76.7765,30.7442],[76.7765,30.7448]]},
    {"id":"P-118","status":"validated","confidence":92,"area":880,"land_use":"Commercial","owner":"Private","coords":[[76.7782,30.7448],[76.7798,30.7448],[76.7798,30.7442],[76.7782,30.7442],[76.7782,30.7448]]},
    {"id":"P-119","status":"conflict","confidence":50,"area":1150,"land_use":"Commercial","owner":"Disputed","coords":[[76.7802,30.7448],[76.7820,30.7448],[76.7820,30.7442],[76.7802,30.7442],[76.7802,30.7448]]},
    {"id":"P-120","status":"validated","confidence":90,"area":750,"land_use":"Residential","owner":"Private","coords":[[76.7768,30.7378],[76.7782,30.7378],[76.7782,30.7370],[76.7768,30.7370],[76.7768,30.7378]]},
    {"id":"P-121","status":"changed","confidence":86,"area":950,"land_use":"Commercial","owner":"Private","coords":[[76.7786,30.7378],[76.7802,30.7378],[76.7802,30.7370],[76.7786,30.7370],[76.7786,30.7378]]},
    {"id":"P-122","status":"review","confidence":71,"area":680,"land_use":"Residential","owner":"Private","coords":[[76.7806,30.7378],[76.7818,30.7378],[76.7818,30.7370],[76.7806,30.7370],[76.7806,30.7378]]},
    {"id":"P-123","status":"validated","confidence":96,"area":1100,"land_use":"Institutional","owner":"Municipal Corp.","coords":[[76.7822,30.7378],[76.7840,30.7378],[76.7840,30.7370],[76.7822,30.7370],[76.7822,30.7378]]},
    {"id":"P-124","status":"conflict","confidence":47,"area":820,"land_use":"Residential","owner":"Private","coords":[[76.7775,30.7368],[76.7790,30.7368],[76.7790,30.7360],[76.7775,30.7360],[76.7775,30.7368]]},
    {"id":"P-125","status":"validated","confidence":94,"area":600,"land_use":"Commercial","owner":"Private","coords":[[76.7795,30.7368],[76.7808,30.7368],[76.7808,30.7360],[76.7795,30.7360],[76.7795,30.7368]]},
]

CONFLICTS_DATA = [
    {"parcel_id":"P-104","conflict_type":"area_mismatch","severity":"high","sources_involved":"Cadastral vs Drone","recommended_action":"Field survey to verify boundary","observed_values":{"cadastral":1000,"revenue":1000,"gnss":1008,"drone":1035,"range_pct":3.5},"explanation":"Area measurements differ across sources. Drone estimate is 3.5% larger than cadastral records."},
    {"parcel_id":"P-107","conflict_type":"missing_record","severity":"high","sources_involved":"Revenue (absent)","recommended_action":"Request revenue dept. records","observed_values":{"missing_from":["revenue"],"present_in":["cadastral","municipal","gnss","drone"]},"explanation":"Revenue records missing for this institutional parcel. Drone estimate 8.6% larger than cadastral."},
    {"parcel_id":"P-112","conflict_type":"boundary_mismatch","severity":"high","sources_involved":"Cadastral vs GNSS vs Drone","recommended_action":"Resurvey with DGPS","observed_values":{"cadastral":1300,"revenue":1250,"gnss":1340,"drone":1360,"range_pct":8.5},"explanation":"Parcel boundaries do not align across sources. Possible subdivision not recorded."},
    {"parcel_id":"P-119","conflict_type":"ownership_dispute","severity":"high","sources_involved":"All sources","recommended_action":"Legal review and title verification","observed_values":{"cadastral":"Private","revenue":"Disputed","municipal":"Private"},"explanation":"Owner field shows 'Disputed' in revenue records. Duplicate parcel IDs found in municipal records."},
    {"parcel_id":"P-124","conflict_type":"encroachment","severity":"high","sources_involved":"GNSS + Drone vs Cadastral","recommended_action":"Site inspection and NOC verification","observed_values":{"cadastral":820,"gnss":860,"drone":870,"excess_area":"50 m²"},"explanation":"Building footprint extends beyond recorded parcel. Possible unauthorized construction."},
]


async def seed_database(db: AsyncSession):
    """Seed the database with Chandigarh demo data."""
    # Check if already seeded
    existing = await db.scalar(select(Parcel.parcel_id).limit(1))
    if existing:
        logger.info("Database already seeded, skipping")
        return

    logger.info("Seeding database with Chandigarh demo data...")

    # Insert parcels
    for p in PARCELS_DATA:
        polygon = Polygon(p["coords"])
        parcel = Parcel(
            parcel_id=p["id"],
            source_id=p["id"],
            geometry=from_shape(polygon, srid=4326),
            area=p["area"],
            land_use=p["land_use"],
            owner=p["owner"],
            confidence=p["confidence"],
            status=p["status"],
        )
        db.add(parcel)

    # Insert conflicts
    for c in CONFLICTS_DATA:
        conflict = Conflict(
            parcel_id=c["parcel_id"],
            conflict_type=c["conflict_type"],
            severity=c["severity"],
            sources_involved=c["sources_involved"],
            recommended_action=c["recommended_action"],
            observed_values=c["observed_values"],
            explanation=c["explanation"],
        )
        db.add(conflict)

    # Audit entry for seeding
    audit = AuditLog(
        entity_type="dataset",
        entity_id="seed",
        action="seed_database",
        details={"parcels": len(PARCELS_DATA), "conflicts": len(CONFLICTS_DATA), "area": "Chandigarh Sector 17"},
        user="system",
    )
    db.add(audit)

    await db.commit()
    logger.info(f"Seeded {len(PARCELS_DATA)} parcels and {len(CONFLICTS_DATA)} conflicts")
