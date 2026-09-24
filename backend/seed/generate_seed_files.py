import json
import csv
from pathlib import Path

seed_dir = Path(__file__).parent

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
    {"id":"P-120","status":"validated","confidence":90,"area":750,"land_use":"Residential","owner":"Private","coords":[[76.7768,30.7378],[76.7782,30.7378],[76.7802,30.7370],[76.7768,30.7370],[76.7768,30.7378]]},
    {"id":"P-121","status":"changed","confidence":86,"area":950,"land_use":"Commercial","owner":"Private","coords":[[76.7786,30.7378],[76.7802,30.7378],[76.7802,30.7370],[76.7786,30.7370],[76.7786,30.7378]]},
    {"id":"P-122","status":"review","confidence":71,"area":680,"land_use":"Residential","owner":"Private","coords":[[76.7806,30.7378],[76.7818,30.7378],[76.7818,30.7370],[76.7806,30.7370],[76.7806,30.7378]]},
    {"id":"P-123","status":"validated","confidence":96,"area":1100,"land_use":"Institutional","owner":"Municipal Corp.","coords":[[76.7822,30.7378],[76.7840,30.7378],[76.7840,30.7370],[76.7822,30.7370],[76.7822,30.7378]]},
    {"id":"P-124","status":"conflict","confidence":47,"area":820,"land_use":"Residential","owner":"Private","coords":[[76.7775,30.7368],[76.7790,30.7368],[76.7790,30.7360],[76.7775,30.7360],[76.7775,30.7368]]},
    {"id":"P-125","status":"validated","confidence":94,"area":600,"land_use":"Commercial","owner":"Private","coords":[[76.7795,30.7368],[76.7808,30.7368],[76.7808,30.7360],[76.7795,30.7360],[76.7795,30.7368]]}
]

# 1. chandigarh_parcels.geojson
parcels_features = []
for p in PARCELS_DATA:
    parcels_features.append({
        "type": "Feature",
        "id": p["id"],
        "properties": {
            "parcel_id": p["id"],
            "status": p["status"],
            "confidence": p["confidence"],
            "area": p["area"],
            "land_use": p["land_use"],
            "owner": p["owner"],
            "source": "Chandigarh Cadastral Survey 2024"
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [p["coords"]]
        }
    })

geojson_data = {
    "type": "FeatureCollection",
    "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
    "features": parcels_features
}
(seed_dir / "chandigarh_parcels.geojson").write_text(json.dumps(geojson_data, indent=2))

# 2. municipal_gis.geojson
(seed_dir / "municipal_gis.geojson").write_text(json.dumps(geojson_data, indent=2))

# 3. gnss_survey.geojson (point survey coordinates)
gnss_features = []
for p in PARCELS_DATA:
    c = p["coords"][0]
    gnss_features.append({
        "type": "Feature",
        "properties": {
            "point_id": f"GNSS-{p['id']}",
            "parcel_id": p["id"],
            "accuracy_cm": 1.5,
            "surveyor": "Survey of India / DGPS Team A"
        },
        "geometry": {
            "type": "Point",
            "coordinates": [c[0] + 0.00005, c[1] + 0.00005]
        }
    })

(seed_dir / "gnss_survey.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": gnss_features}, indent=2))

# 4. buildings.geojson
bld_features = []
for p in PARCELS_DATA[:15]:
    c = p["coords"]
    inset = [
        [c[0][0] + 0.0002, c[0][1] - 0.0001],
        [c[1][0] - 0.0002, c[1][1] - 0.0001],
        [c[2][0] - 0.0002, c[2][1] + 0.0001],
        [c[3][0] + 0.0002, c[3][1] + 0.0001],
        [c[0][0] + 0.0002, c[0][1] - 0.0001],
    ]
    bld_features.append({
        "type": "Feature",
        "properties": {
            "building_id": f"BLD-{p['id']}",
            "parcel_id": p["id"],
            "floors": 3,
            "structure": "RCC Commercial"
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [inset]
        }
    })

(seed_dir / "buildings.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": bld_features}, indent=2))

# 5. revenue_records.csv
with open(seed_dir / "revenue_records.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["khasra_no", "owner_name", "area_sqm", "land_use", "mutation_status", "dispute_flag"])
    for p in PARCELS_DATA:
        dispute = "YES" if p["status"] == "conflict" else "NO"
        writer.writerow([p["id"], p["owner"], p["area"], p["land_use"], "MUTATED", dispute])

print("All seed files created successfully!")
