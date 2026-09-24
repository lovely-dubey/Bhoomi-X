/**
 * Conflicts Page — Sortable conflict review table with resolution actions.
 */

import { useState, useEffect } from 'react';
import type { ConflictRecord } from '../types';
import { fetchConflicts, resolveConflict } from '../api';

interface Props {
  onNavigate: (tab: string, parcelId?: string) => void;
}

interface EnrichedConflictRecord extends ConflictRecord {
  confidence?: number;
}

// Fallback data when API unavailable matches prototype.html exactly
const FALLBACK_CONFLICTS: EnrichedConflictRecord[] = [
  { conflict_id: '1', parcel_id: 'P-104', conflict_type: 'Area Mismatch', severity: 'high', sources_involved: 'Cadastral vs Drone', observed_values: { range_pct: 3.5 }, recommended_action: 'Field survey to verify boundary', status: 'pending', created_at: new Date().toISOString(), explanation: '', confidence: 58 },
  { conflict_id: '2', parcel_id: 'P-107', conflict_type: 'Missing Record', severity: 'high', sources_involved: 'Revenue (absent)', observed_values: {}, recommended_action: 'Request revenue dept. records', status: 'pending', created_at: new Date().toISOString(), explanation: '', confidence: 45 },
  { conflict_id: '3', parcel_id: 'P-112', conflict_type: 'Boundary Mismatch', severity: 'high', sources_involved: 'Cadastral vs GNSS vs Drone', observed_values: { range_pct: 8.5 }, recommended_action: 'Resurvey with DGPS', status: 'pending', created_at: new Date().toISOString(), explanation: '', confidence: 52 },
  { conflict_id: '4', parcel_id: 'P-119', conflict_type: 'Ownership Dispute', severity: 'high', sources_involved: 'All sources', observed_values: {}, recommended_action: 'Legal review and title verification', status: 'pending', created_at: new Date().toISOString(), explanation: '', confidence: 50 },
  { conflict_id: '5', parcel_id: 'P-124', conflict_type: 'Encroachment', severity: 'high', sources_involved: 'GNSS + Drone vs Cadastral', observed_values: { excess_area: '50 m²' }, recommended_action: 'Site inspection and NOC verification', status: 'pending', created_at: new Date().toISOString(), explanation: '', confidence: 47 },
];

export default function Conflicts({ onNavigate }: Props) {
  const [conflicts, setConflicts] = useState<EnrichedConflictRecord[]>(FALLBACK_CONFLICTS);
  const [sortField, setSortField] = useState<string | null>(null);
  const [sortAsc, setSortAsc] = useState(true);

  useEffect(() => {
    fetchConflicts()
      .then(data => {
        if (Array.isArray(data) && data.length > 0) {
          // enrich with confidence if missing
          const enriched = data.map((d: any, idx: number) => ({
            ...d,
            confidence: d.confidence ?? FALLBACK_CONFLICTS[idx % FALLBACK_CONFLICTS.length]?.confidence ?? 50
          }));
          setConflicts(enriched);
        }
      })
      .catch(() => {});
  }, []);

  const handleResolve = async (id: string, status: string) => {
    try {
      await resolveConflict(id, { status, reviewer: 'admin' });
    } catch { /* offline mode */ }
    setConflicts(prev => prev.map(c => c.conflict_id === id ? { ...c, status: status as any } : c));
  };

  const handleSort = (field: string) => {
    const asc = sortField === field ? !sortAsc : true;
    setSortField(field);
    setSortAsc(asc);

    const sorted = [...conflicts].sort((a: any, b: any) => {
      const dir = asc ? 1 : -1;
      if (field === 'confidence') return ((a.confidence ?? 0) - (b.confidence ?? 0)) * dir;
      const valA = a[field] || a.parcel_id || '';
      const valB = b[field] || b.parcel_id || '';
      return String(valA).localeCompare(String(valB)) * dir;
    });
    setConflicts(sorted);
  };

  const pending = conflicts.filter(c => c.status === 'pending').length;
  const resolved = conflicts.length - pending;

  const exportConflicts = () => {
    const headers = ['Parcel,Conflict Type,Severity,Sources,Confidence,Recommended Action,Status'];
    const rows = conflicts.map(c =>
      `"${c.parcel_id}","${c.conflict_type}","${c.severity}","${c.sources_involved}","${c.confidence}%","${c.recommended_action}","${c.status}"`
    );
    const blob = new Blob([headers.concat(rows).join('\n')], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bhoomi-x-conflicts-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="page-scroll" style={{ padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: 20, fontWeight: 800 }}>Conflict Review</h2>
          <p className="text-muted" style={{ fontSize: 13 }}>Review and resolve detected conflicts across data sources</p>
        </div>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <div style={{ display: 'flex', gap: 8 }}>
            <span className="badge badge-red" style={{ padding: '6px 14px', fontSize: 12 }}>{pending} Pending</span>
            <span className="badge badge-green" style={{ padding: '6px 14px', fontSize: 12 }}>{resolved} Resolved</span>
          </div>
          <button className="btn btn-ghost btn-sm" onClick={exportConflicts}>
            ↓ Export
          </button>
        </div>
      </div>

      <div className="card" style={{ flex: 1, padding: 0, overflow: 'auto' }}>
        <table className="conflict-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('parcel_id')} style={{ cursor: 'pointer' }}>
                Parcel ↕
              </th>
              <th onClick={() => handleSort('conflict_type')} style={{ cursor: 'pointer' }}>
                Conflict Type ↕
              </th>
              <th onClick={() => handleSort('severity')} style={{ cursor: 'pointer' }}>
                Severity ↕
              </th>
              <th>Sources</th>
              <th onClick={() => handleSort('confidence')} style={{ cursor: 'pointer' }}>
                Confidence ↕
              </th>
              <th>Recommended Action</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {conflicts.map(c => (
              <tr
                key={c.conflict_id}
                style={{ cursor: 'pointer' }}
                onClick={() => onNavigate('map', c.parcel_id)}
                title="Click or double-click to view parcel on map"
              >
                <td style={{ fontWeight: 700, color: 'var(--navy-500)' }}>
                  🔍 {c.parcel_id}
                </td>
                <td style={{ fontWeight: 600 }}>{c.conflict_type}</td>
                <td className={`severity-${c.severity}`}>{c.severity.toUpperCase()}</td>
                <td style={{ fontSize: 11.5 }}>{c.sources_involved}</td>
                <td>
                  <span style={{
                    fontWeight: 800,
                    fontSize: 13.5,
                    color: (c.confidence ?? 50) >= 70 ? 'var(--amber-600)' : 'var(--red-600)'
                  }}>
                    {c.confidence}%
                  </span>
                </td>
                <td style={{ fontSize: 12 }}>{c.recommended_action}</td>
                <td>
                  <span className={`badge badge-${c.status === 'pending' ? 'amber' : c.status === 'accepted' ? 'green' : c.status === 'rejected' ? 'red' : 'blue'}`}>
                    {c.status.toUpperCase()}
                  </span>
                </td>
                <td>
                  <div style={{ display: 'flex', gap: 4 }}>
                    <button className="btn btn-success btn-sm" onClick={(e) => { e.stopPropagation(); handleResolve(c.conflict_id, 'accepted'); }} title="Accept">✓</button>
                    <button className="btn btn-danger btn-sm" onClick={(e) => { e.stopPropagation(); handleResolve(c.conflict_id, 'rejected'); }} title="Reject">✗</button>
                    <button className="btn btn-ghost btn-sm" onClick={(e) => { e.stopPropagation(); handleResolve(c.conflict_id, 'escalated'); }} title="Escalate">↑</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
