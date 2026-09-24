# BHOOMI-X — Architecture

## 1. High-Level Architecture

```text
                 DATA SOURCES
  ┌────────┬────────┬─────────┬───────────┐
  │Cadastral│Revenue │Municipal│Drone/ORI  │
  │Maps     │Records │GIS      │Imagery    │
  └────┬────┴────┬───┴────┬────┴─────┬─────┘
       └─────────┴────────┴───────────┘
                         │
                  Data Ingestion
                         │
                  Validation/ETL
                         │
             ┌───────────┴───────────┐
             │                       │
        GIS ENGINE               AI ENGINE
        - CRS/GeoRef             - CV extraction
        - Geometry               - Spatial matching
        - Topology               - Attribute mapping
        - Spatial joins          - Anomaly detection
             │                       │
             └───────────┬───────────┘
                         │
                 Harmonization Engine
                         │
            Conflict + Change Analysis
                         │
                  Confidence Score
                         │
                 Human Verification
                         │
                    PostGIS DB
                         │
                    REST API
                         │
                    Web-GIS UI
```

## 2. Recommended Stack

### Frontend
- React
- TypeScript
- Leaflet or OpenLayers
- Tailwind CSS

### Backend
- Python FastAPI for geospatial/AI services
- Optional Node.js gateway if the team prefers it
- REST/JSON APIs

### Geospatial
- PostGIS
- GeoPandas
- Shapely
- Rasterio
- GDAL/OGR where needed

### AI/ML
- Python
- scikit-learn for baseline matching/anomaly models
- OpenCV for image processing
- PyTorch/Ultralytics or equivalent for building detection if required

### Infrastructure
- Docker
- PostgreSQL/PostGIS
- Object storage for imagery
- Local deployment for hackathon demo

## 3. Data Model

### Parcel
- parcel_id
- source_id
- geometry
- area
- land_use
- confidence
- status

### SourceRecord
- source_record_id
- source_type
- source_dataset
- external_id
- attributes
- geometry

### Match
- match_id
- source_record_id
- parcel_id
- spatial_score
- attribute_score
- overall_score
- reasons
- status

### Conflict
- conflict_id
- parcel_id
- conflict_type
- severity
- observed_values
- recommended_action
- status

### Review
- review_id
- parcel_id
- reviewer
- decision
- comment
- timestamp

## 4. Matching Pipeline

1. Normalize CRS.
2. Validate geometries.
3. Generate spatial candidates.
4. Calculate overlap/distance/geometry features.
5. Compare attributes.
6. Combine features into a match score.
7. Apply thresholds.
8. Generate explanation.
9. Send uncertain cases to review.

Example score:

```text
overall =
  0.50 * spatial_score +
  0.30 * attribute_score +
  0.20 * source_agreement
```

Weights are configurable and must be validated on labelled test data.

## 5. Security

- Authentication and role-based access
- Do not expose sensitive owner attributes in public views
- Encrypt data in transit
- Maintain audit logs
- Separate demo/synthetic data from official data

## 6. Deployment

For SIH prototype:

```text
Docker Compose
 ├── frontend
 ├── api
 ├── worker
 ├── postgres-postgis
 └── object-storage/local-files
```

Production can later move to managed cloud services.
