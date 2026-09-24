# BHOOMI-X — Engineering & Product Rules

## Data Rules

1. Never treat synthetic/demo records as official government records.
2. Every record must retain its source dataset and source identifier.
3. Never silently overwrite source data.
4. Preserve original geometry before transformation.
5. Store CRS metadata and transformation history.
6. Validate geometry before spatial analysis.
7. Reject or quarantine invalid geometries rather than silently fixing them.

## AI Rules

1. AI must be explainable at the decision level.
2. AI must not make legal ownership decisions.
3. Low-confidence matches require human review.
4. Do not invent missing attributes.
5. Do not present a recommendation as an authoritative fact.
6. Keep deterministic GIS operations separate from probabilistic AI predictions.
7. All model thresholds must be configurable and testable.

## Matching Rules

1. Candidate generation must use spatial constraints before expensive semantic matching.
2. Use multiple evidence signals where available.
3. A high spatial score alone must not guarantee a final match.
4. Conflicting authoritative-looking records must be flagged, not silently resolved.
5. Every match should expose its evidence:
   - spatial overlap/distance
   - attribute similarity
   - source agreement
   - data quality

## Review Rules

1. Reviewer decisions are auditable.
2. Reviewers can accept, reject or request further evidence.
3. A rejected recommendation must remain available in the audit trail.
4. Official records should require explicit authorization before any write-back.

## UI Rules

1. Use clear status colors consistently:
   - green = validated/high confidence
   - amber = review required
   - red = conflict
   - blue = informational
2. Never rely on color alone; use labels/icons too.
3. Show source provenance when a parcel is selected.
4. Show why a match was suggested.
5. Avoid dashboards that hide uncertainty.

## Prototype Rules

1. Optimize for an end-to-end demonstrable workflow.
2. Prefer a small labelled pilot area over a huge incomplete dataset.
3. Keep real/public geometry separate from synthetic attributes.
4. Seed known conflicts so the demo can prove detection and review.
