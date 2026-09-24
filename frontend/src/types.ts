/**
 * BHOOMI-X TypeScript Type Definitions
 * Matches backend Pydantic schemas
 */

export interface Parcel {
  parcel_id: string;
  source_id?: string;
  area?: number;
  land_use?: string;
  owner?: string;
  confidence: number;
  status: 'validated' | 'review' | 'conflict' | 'changed' | 'pending';
  geometry?: GeoJSONGeometry;
  source_records?: SourceRecord[];
  matches?: MatchRecord[];
  conflicts?: ConflictRecord[];
  reviews?: ReviewRecord[];
}

export interface SourceRecord {
  source_type: string;
  source_dataset: string;
  external_id?: string;
  area?: number;
  land_use?: string;
  owner?: string;
  is_valid: string;
}

export interface MatchRecord {
  match_id: string;
  spatial_score: number;
  attribute_score: number;
  overall_score: number;
  explanation?: string;
  status: string;
}

export interface ConflictRecord {
  conflict_id: string;
  parcel_id: string;
  conflict_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  observed_values: Record<string, any>;
  recommended_action?: string;
  explanation?: string;
  status: 'pending' | 'accepted' | 'rejected' | 'escalated';
  sources_involved?: string;
  created_at: string;
  resolved_at?: string;
  resolved_by?: string;
}

export interface ReviewRecord {
  review_id: string;
  parcel_id: string;
  reviewer: string;
  decision: 'accepted' | 'rejected' | 'escalated';
  comment?: string;
  timestamp: string;
}

export interface ParcelStats {
  total_parcels: number;
  harmonized: number;
  high_confidence: number;
  review_required: number;
  conflicts: number;
  recent_changes: number;
}

export interface PipelineStep {
  step_number: number;
  name: string;
  description: string;
  status: 'pending' | 'running' | 'complete' | 'error';
  records_processed?: string;
  duration_seconds?: number;
  errors: string[];
}

export interface PipelineStatus {
  pipeline_id: string;
  status: 'idle' | 'running' | 'complete' | 'error';
  current_step: number;
  total_steps: number;
  steps: PipelineStep[];
  started_at?: string;
  completed_at?: string;
  summary?: string;
}

export interface DatasetInfo {
  name: string;
  source_type: string;
  file_format: string;
  crs?: string;
  record_count: number;
  file_size?: string;
  status: 'valid' | 'warning' | 'error';
  upload_id?: string;
  validation_errors: string[];
}

export interface ConflictStats {
  total: number;
  pending: number;
  accepted: number;
  rejected: number;
  escalated: number;
}

export interface GeoJSONGeometry {
  type: string;
  coordinates: number[][][] | number[][] | number[];
}

export interface GeoJSONFeature {
  type: 'Feature';
  properties: Record<string, any>;
  geometry: GeoJSONGeometry;
}

export interface GeoJSONFeatureCollection {
  type: 'FeatureCollection';
  features: GeoJSONFeature[];
}
