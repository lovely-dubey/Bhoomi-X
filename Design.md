# BHOOMI-X — Product & UI Design

## 1. Design Goal

The interface should feel like a professional government geospatial operations console: map-first, evidence-driven, calm and readable.

## 2. Main Screens

### A. Overview Dashboard
Show:
- Total parcels
- Harmonized
- High confidence
- Review required
- Conflicts
- Recent changes

### B. Map Workspace
Layers:
- parcels
- buildings
- roads
- imagery
- utilities
- conflicts
- changes

Controls:
- layer toggle
- search parcel
- upload dataset
- filter by confidence/status
- time slider for historical comparison

### C. Parcel Detail
When a parcel is selected:

```text
Parcel P124
Status: Review Required
Confidence: 82%

Sources
✓ Cadastral
✓ Revenue
✓ Municipal
✓ GNSS
✓ Drone

Evidence
- 96% spatial overlap
- 91% attribute similarity
- area discrepancy: 2.1%

Recommendation
Review GNSS vs cadastral boundary
```

### D. Conflict Review
Table columns:
- parcel
- conflict type
- severity
- sources
- confidence
- recommended action
- review status

Actions:
- Accept
- Reject
- Escalate

### E. Data Ingestion
Upload card:
- dataset name
- source type
- format
- CRS
- validation result

## 3. Visual Language

- Primary: deep navy/blue
- Success: green
- Warning: amber
- Conflict: red
- Background: off-white/light grey
- Use one strong accent color only

Typography:
- Inter or another highly legible sans-serif
- Large section headings
- Compact data labels

## 4. Map Symbology

Parcel status:
- validated: green outline
- review: amber outline
- conflict: red outline
- changed: blue outline

Use patterns/icons in addition to color for accessibility.

## 5. Design Principle

**Map first → evidence second → action third.**

The user should always understand:
1. What parcel am I looking at?
2. What sources support it?
3. What is inconsistent?
4. Why did the system recommend this?
5. What action can I take?

## 6. Demo Story

Open dashboard → upload 3–5 datasets → show automatic alignment → click a parcel → show source comparison → show conflict → show AI recommendation → approve → show harmonized result on map.
