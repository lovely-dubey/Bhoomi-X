/**
 * BHOOMI-X API Client
 * Axios-based API client pointing to FastAPI backend
 */

import axios from 'axios';
import type {
  Parcel, ParcelStats, ConflictRecord, ConflictStats,
  ReviewRecord, PipelineStatus, DatasetInfo, GeoJSONFeatureCollection
} from './types';

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

// ─── Parcels ───
export const fetchParcels = (params?: { status?: string; min_confidence?: number }) =>
  api.get<Parcel[]>('/parcels/', { params }).then(r => r.data);

export const fetchParcelStats = () =>
  api.get<ParcelStats>('/parcels/stats').then(r => r.data);

export const fetchParcelDetail = (parcelId: string) =>
  api.get<Parcel>(`/parcels/${parcelId}`).then(r => r.data);

export const fetchParcelsGeoJSON = (params?: { status?: string; min_confidence?: number }) =>
  api.get<GeoJSONFeatureCollection>('/parcels/geojson', { params }).then(r => r.data);

// ─── Conflicts ───
export const fetchConflicts = (params?: { status?: string; severity?: string }) =>
  api.get<ConflictRecord[]>('/conflicts/', { params }).then(r => r.data);

export const fetchConflictStats = () =>
  api.get<ConflictStats>('/conflicts/stats').then(r => r.data);

export const resolveConflict = (conflictId: string, body: { status: string; reviewer?: string; comment?: string }) =>
  api.put(`/conflicts/${conflictId}`, body).then(r => r.data);

// ─── Reviews ───
export const createReview = (body: { parcel_id: string; decision: string; reviewer?: string; comment?: string }) =>
  api.post<ReviewRecord>('/reviews/', body).then(r => r.data);

export const fetchAuditTrail = () =>
  api.get('/reviews/audit').then(r => r.data);

// ─── Pipeline ───
export const fetchPipelineStatus = () =>
  api.get<PipelineStatus>('/pipeline/status').then(r => r.data);

export const runPipeline = () =>
  api.post<PipelineStatus>('/pipeline/run').then(r => r.data);

export const resetPipeline = () =>
  api.post<PipelineStatus>('/pipeline/reset').then(r => r.data);

// ─── Data Ingestion ───
export const fetchDatasets = () =>
  api.get<DatasetInfo[]>('/ingest/datasets').then(r => r.data);

export const uploadDataset = (file: File, sourceType: string, name?: string) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('source_type', sourceType);
  if (name) formData.append('dataset_name', name);
  return api.post('/ingest/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(r => r.data);
};

export const loadSampleData = () =>
  api.post('/ingest/sample').then(r => r.data);

// ─── Export ───
export const exportGeoJSON = () =>
  api.get('/export/geojson').then(r => r.data);

export const exportReport = () =>
  api.get('/export/report').then(r => r.data);

// ─── Health ───
export const healthCheck = () =>
  api.get('/health').then(r => r.data);

export default api;
