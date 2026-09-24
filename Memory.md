# BHOOMI-X — Project Memory

## Identity

**Project:** BHOOMI-X  
**Full Name:** AI-Powered Geospatial Reconciliation & Harmonization Platform for Urban Land Records  
**SIH:** Smart India Hackathon 2026  
**PS:** 26013

## One-Sentence Definition

BHOOMI-X is an AI + GIS platform that integrates fragmented multi-source urban land data, aligns and matches corresponding records, detects conflicts and changes, assigns explainable confidence scores, and routes uncertain cases to authorized human reviewers.

## Core Problem

The same physical land parcel may appear across cadastral, revenue, municipal, imagery and survey datasets with differences in identifiers, schemas, coordinates, geometry and attributes.

## Core Solution

```text
Multi-source data
→ ingestion
→ standardization
→ georeferencing
→ GIS processing
→ AI matching
→ conflict/change detection
→ confidence scoring
→ human verification
→ harmonized land record
```

## AI Responsibilities

- imagery feature extraction
- semantic attribute mapping
- candidate matching
- anomaly detection
- confidence estimation
- explainable recommendations

## GIS Responsibilities

- CRS transformation
- georeferencing
- geometry operations
- spatial joins
- topology validation
- map visualization
- spatial indexing

## Key Product Principle

**AI recommends; GIS computes; authorized humans verify.**

## Prototype Data Strategy

Use a combination of:
- public/open geospatial layers where available
- self-generated drone/GNSS/ground-truth data
- clearly labelled synthetic revenue/municipal/utility attributes

Do not represent synthetic data as official data.

## Demo Narrative

1. Upload heterogeneous datasets.
2. System standardizes and aligns them.
3. System identifies corresponding parcel records.
4. System detects a planted conflict.
5. System explains the conflict.
6. System provides a confidence score.
7. Reviewer approves/rejects.
8. Harmonized parcel appears on the Web-GIS.

## Product Language

Preferred:
- harmonization
- reconciliation
- provenance
- confidence
- evidence
- human verification
- multi-source geospatial data

Avoid:
- “AI decides ownership”
- “100% accurate”
- “replaces government officers”
- “official legal truth” for prototype outputs
