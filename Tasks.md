# BHOOMI-X — Task Plan

## Phase 0 — Setup
- [x] Create monorepo
- [x] Docker Compose (`docker-compose.yml`, `.env`, `nginx/nginx.conf`)
- [x] PostgreSQL + PostGIS (PostGIS 16-3.4 container service)
- [x] FastAPI service (`backend/main.py`, config, database)
- [x] React frontend (`frontend/` Vite + TypeScript + Leaflet)
- [x] Seed demo dataset (`backend/seed/seed_data.py` & synthetic GeoJSONs/CSVs)

## Phase 1 — Data Foundation
- [x] Define canonical parcel schema (`backend/models/parcel.py`, `backend/schemas/parcel.py`)
- [x] Build GeoJSON/CSV ingestion (`backend/services/ingestion_service.py`)
- [x] CRS detection (`backend/geo/crs.py`)
- [x] CRS transformation (`backend/geo/crs.py` with EPSG:4326 canonical target)
- [x] Geometry validation (`backend/geo/geometry.py` with quarantine rules)
- [x] Store source provenance (`models.parcel.SourceRecord`)

## Phase 2 — GIS Core
- [x] Parcel layer (`backend/models/parcel.py`, `backend/geo/spatial_ops.py`)
- [x] Building layer (`backend/seed/buildings.geojson`)
- [x] Spatial join (`backend/geo/spatial_ops.py`)
- [x] Intersection/containment (`backend/geo/spatial_ops.py`)
- [x] Area calculations (`backend/geo/spatial_ops.py`)
- [x] Topology checks (`backend/geo/geometry.py`)

## Phase 3 — AI/Intelligence
- [x] Attribute schema matcher (`backend/ai/attribute_matcher.py`)
- [x] Record similarity baseline (`backend/ai/attribute_matcher.py`)
- [x] Spatial candidate scorer (`backend/ai/spatial_scorer.py`)
- [x] Combined match score (`backend/ai/confidence.py`)
- [x] Anomaly detector (`backend/ai/anomaly_detector.py`)
- [x] Explanation generator (`backend/ai/explanation.py`)
- [x] Confidence scoring (`backend/ai/confidence.py`)

## Phase 4 — Change & Conflict
- [x] Area mismatch detection (`backend/services/conflict_service.py`)
- [x] Boundary mismatch detection (`backend/services/conflict_service.py`)
- [x] Missing/duplicate record detection (`backend/services/conflict_service.py`)
- [x] Building-parcel inconsistency (`backend/services/conflict_service.py`)
- [x] Historical comparison (`backend/services/conflict_service.py`)
- [x] Conflict review queue (`backend/routers/conflicts.py`, `backend/routers/reviews.py`)

## Phase 5 — Frontend
- [x] Dashboard (`frontend/src/pages/Dashboard.tsx`)
- [x] Interactive map (`frontend/src/pages/MapWorkspace.tsx`)
- [x] Upload flow (`frontend/src/pages/DataIngestion.tsx`)
- [x] Parcel detail drawer (`frontend/src/pages/MapWorkspace.tsx`)
- [x] Conflict review (`frontend/src/pages/Conflicts.tsx`)
- [x] Confidence visualization (`frontend/src/pages/MapWorkspace.tsx`, gauge/bars)
- [x] Export (`backend/routers/export.py`)

## Phase 6 — Testing
- [x] Create labelled test cases (`backend/seed/seed_data.py`, `backend/seed/chandigarh_parcels.geojson`)
- [x] Measure precision/recall of matching (`backend/ai/spatial_scorer.py`, `backend/ai/attribute_matcher.py`)
- [x] Test CRS transformations (`backend/geo/crs.py`)
- [x] Test invalid geometry (`backend/geo/geometry.py`)
- [x] Test low-confidence routing (`backend/tests/test_core.py`)
- [x] Test reviewer actions (`backend/tests/test_core.py`, `backend/routers/reviews.py`)

## Phase 7 — SIH Demo
- [x] Prepare 100–500 parcel pilot dataset (Chandigarh Sector 17 synthetic dataset)
- [x] Seed 10–20 known conflicts (Planted area, boundary, missing record, ownership, and encroachment conflicts)
- [x] Prepare 3-minute demo script & narrative (`demo_script.md` / `prototype.html`)
- [x] Prepare architecture slide & diagram (`Architecture.md`)
- [x] Prepare AI-vs-GIS explanation (`PRD.md`, `Memory.md`, `Architecture.md`)
- [x] Prepare limitations and future scope (`PRD.md §10`, `Rules.md`)

## Suggested Team Split

### GIS/Data
Ingestion, CRS, PostGIS, spatial processing.

### AI/ML
Feature extraction, matching, anomaly detection, confidence model.

### Backend
APIs, processing jobs, auth, audit trail.

### Frontend
Web-GIS, dashboard, review UI.

### Research/Pitch
Dataset provenance, evaluation, PPT, demo script.
