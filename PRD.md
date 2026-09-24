# BHOOMI-X — Product Requirements Document

## 1. Product

**Name:** BHOOMI-X  
**Subtitle:** AI-Powered Geospatial Reconciliation & Harmonization Platform for Urban Land Records  
**Problem Statement:** SIH 2026 — PS 26013

## 2. Problem

Urban land information is fragmented across cadastral maps, revenue records, municipal GIS, imagery, survey/GNSS data, utilities and building footprints. These sources may differ in format, schema, coordinate reference system, geometry, identifiers and attribute values.

The operational problem is not simply viewing these layers together. It is establishing reliable relationships between them, identifying inconsistencies, detecting changes, and producing a unified, reviewable land record.

## 3. Product Goal

Build a prototype that can:

1. ingest heterogeneous geospatial datasets;
2. standardize schemas and coordinate systems;
3. match records and spatial features belonging to the same parcel;
4. detect geometry, attribute and source conflicts;
5. identify changes between historical/current datasets;
6. calculate explainable confidence scores;
7. route uncertain cases to human review;
8. present the result through an interactive Web-GIS dashboard.

## 4. Target Users

- Land/revenue officials
- Municipal GIS teams
- Urban planners
- Survey and mapping teams
- Data administrators

## 5. Core User Journey

Upload datasets → validate → standardize → align → match → detect conflicts/changes → review recommendations → approve/reject → export harmonized parcel record.

## 6. MVP Scope

### Must Have
- GeoJSON/CSV/GeoTIFF ingestion
- CRS detection/transformation
- Parcel visualization
- Attribute/schema mapping
- Spatial matching
- Conflict detection
- Confidence scoring
- Human review workflow
- Web-GIS dashboard
- Export of harmonized parcel data

### Should Have
- Building footprint extraction
- Topology checks
- Historical change detection
- Explainable match reasons

### Later
- Real-time inter-department synchronization
- Advanced 3D/DSM/DTM analysis
- Large-scale cloud processing
- Production-grade government integrations

## 7. Functional Requirements

### FR-01 Data Ingestion
Users can upload supported geospatial/tabular datasets and see validation errors.

### FR-02 Standardization
System normalizes field names, data types and coordinate reference systems.

### FR-03 Spatial Alignment
System transforms datasets to a project CRS and records the transformation.

### FR-04 Parcel Matching
System generates candidate matches using spatial overlap, distance and geometry similarity.

### FR-05 Attribute Matching
System compares parcel identifiers, owner/holder fields, area, land use and other attributes where available.

### FR-06 Conflict Detection
System flags area mismatch, identifier mismatch, boundary mismatch, missing records, overlaps and other configured anomalies.

### FR-07 Confidence
Every proposed match/harmonization result receives a score plus contributing factors.

### FR-08 Human Review
Low-confidence or high-impact cases can be accepted, rejected or marked for further investigation.

### FR-09 Auditability
The system records source datasets, processing steps, match reasons and reviewer actions.

### FR-10 Export
Users can export harmonized records and review reports.

## 8. Non-Functional Requirements

- Explainable results
- Reproducible processing
- Secure access
- Modular services
- Spatial indexing for performance
- Clear distinction between official and synthetic/demo data
- No autonomous legal ownership decisions

## 9. Success Metrics

Prototype targets:
- ≥95% successful ingestion of valid demo files
- ≥90% correct parcel matching on labelled test cases
- 100% of flagged conflicts have an explanation
- 100% of low-confidence records routed to review
- End-to-end processing demonstrated on a pilot area

These are prototype engineering targets, not claims about real-world legal accuracy.

## 10. Out of Scope

- Legal determination of land ownership
- Replacing official cadastral/revenue systems
- Public disclosure of sensitive personal land-owner data
- Autonomous modification of authoritative government records

## 11. Key Principle

**AI recommends; GIS computes; authorized humans verify.**
