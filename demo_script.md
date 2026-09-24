# BHOOMI-X — SIH 2026 Pitch & 3-Minute Demo Script
**Problem Statement:** PS 26013  
**Tagline:** *AI recommends; GIS computes; authorized humans verify.*

---

## 1. The 3-Minute Demo Flow

### Minute 0:00 - 0:30 — The Problem Statement & Ingestion
- **Narrative:** "Urban land administration in India is plagued by siloed records. Revenue records say one thing, municipal GIS maps show another, satellite and drone surveys show a third, and ground DGPS surveys reveal physical encroachments. Reconciling them manually takes months."
- **Action on Screen:**
  - Open **Dashboard** showing high-level KPIs: 125 Total Parcels, 117 Harmonized, 6 Review Required, 5 Conflicts.
  - Navigate to **Data Ingestion** tab: Click **"Load Demo Datasets"** to show real-time ingestion of 5 distinct sources (Cadastral GeoJSON, Revenue CSV, Municipal GIS, GNSS Survey, Drone Orthomosaic).
  - Point out automatic CRS detection (normalizing from UTM 43N to WGS 84) and geometry quarantine rules.

### Minute 0:30 - 1:15 — The Harmonization Pipeline
- **Narrative:** "BHOOMI-X uses an 8-stage automated harmonization pipeline combining deterministic GIS spatial joins with AI attribute matching and anomaly detection."
- **Action on Screen:**
  - Navigate to **Pipeline** tab.
  - Click **"Run Full Pipeline"**.
  - Watch the live execution stages animate:
    1. Ingestion & CRS Standardization
    2. Geometry Topology Validation
    3. Spatial Candidate Generation (via R-tree spatial indexing)
    4. Attribute & Identifier Fuzzy Matching
    5. Conflict & Encroachment Detection
    6. Explainable Confidence Scoring (50% Spatial, 30% Attribute, 20% Source Agreement)
    7. Automated Human Review Routing

### Minute 1:15 - 2:15 — Map-First Evidence & Conflict Inspection
- **Narrative:** "Here is our core philosophy: *Map first → evidence second → action third.* Every recommendation is explainable; no black-box AI makes autonomous legal property decisions."
- **Action on Screen:**
  - Navigate to **Map** tab showing Chandigarh Sector 17 parcels styled by status (Green = Validated, Amber = Review, Red = Conflict, Blue = Changed).
  - Click on **Parcel P-104** (Area Mismatch Conflict):
    - Show the right-hand **Inspection Drawer**:
    - Confidence gauge: 58%.
    - Evidence breakdown: Cadastral reports 1,000 m², drone survey reveals 1,035 m² (+3.5% discrepancy).
    - AI Explanation: *"Area measurements differ across sources. Observed values: Cadastral vs Drone. Field survey recommended."*
  - Click on **Parcel P-124** (Encroachment Conflict):
    - Show building footprint overlay exceeding the cadastral boundary by 50 m².
    - Highlight the recommendation for on-site NOC verification.

### Minute 2:15 - 3:00 — Conflict Resolution, Review Audit Trail & Export
- **Narrative:** "Authorized officers retain complete control. Every human decision is cryptographically logged in an immutable audit trail."
- **Action on Screen:**
  - Navigate to **Conflicts** tab:
    - View the sortable queue of flagged conflicts.
    - Click **"Accept"** or **"Resolve"** on a conflict with a review comment.
    - Show that the audit trail logs the reviewer, timestamp, and rationale.
  - Click **"Export Harmonized Report"** (GeoJSON / CSV) ready for integration into state land records portals.

---

## 2. Key Differentiation Slide (AI vs GIS)

| Feature | Deterministic GIS Engine | Probabilistic AI/ML Engine |
| :--- | :--- | :--- |
| **Responsibilities** | CRS reprojection, exact intersection, Hausdorff distance, topology validation, PostGIS spatial indexing. | Identifier transliteration, fuzzy owner name matching, drone computer vision extraction, anomaly isolation forest. |
| **Governance Rule** | Mathematically rigorous, reproducible. | Provides explainable recommendations; **never** alters legal title autonomously. |

---

## 3. Limitations & Future Scope

### Limitations
- Prototype uses synthetic demo datasets (Chandigarh Sector 17) to ensure privacy and compliance with government data rules.
- High-resolution drone orthomosaics require local GPU infrastructure for heavy computer vision inference.

### Future Scope
- Real-time Webhook integration with state land record portals (e.g., Bhoomi Karnataka, Bhulekh UP, Dharani Telangana).
- 3D cadastral parcel management incorporating LiDAR point clouds and building BIM models.
