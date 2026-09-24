/**
 * Map Workspace Page — Leaflet map with GeoJSON parcels, layers, filters, and detail drawer.
 * Supports robust offline demo datasets and initialParcelId routing.
 */

import { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { fetchParcelsGeoJSON, fetchParcelDetail, createReview } from '../api';
import { CHANDIGARH_SECTOR17_PARCELS, CHANDIGARH_BUILDINGS } from '../mapData';

// Fix missing marker icons in leaflet bundle
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

interface Props {
  initialParcelId?: string;
}

const STATUS_STYLES: Record<string, L.PathOptions> = {
  validated: { color: '#0d9448', fillColor: '#34d27b', fillOpacity: 0.25, weight: 3 },
  review: { color: '#b87a00', fillColor: '#ffc933', fillOpacity: 0.25, weight: 3, dashArray: '6, 4' },
  conflict: { color: '#c42b2b', fillColor: '#f06b68', fillOpacity: 0.35, weight: 3, dashArray: '4, 4' },
  changed: { color: '#2563eb', fillColor: '#60a5fa', fillOpacity: 0.25, weight: 3, dashArray: '8, 4' },
  pending: { color: '#9ca3af', fillColor: '#d1d5db', fillOpacity: 0.15, weight: 2 },
};

export default function MapWorkspace({ initialParcelId }: Props) {
  const mapRef = useRef<L.Map | null>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const geojsonLayerRef = useRef<L.GeoJSON | null>(null);
  const buildingsLayerRef = useRef<L.GeoJSON | null>(null);

  const [selectedParcel, setSelectedParcel] = useState<any>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [minConf, setMinConf] = useState(0);

  // Layer toggles
  const [showParcels, setShowParcels] = useState(true);
  const [showBuildings, setShowBuildings] = useState(true);
  const [showConflictsOnly, setShowConflictsOnly] = useState(false);

  // Status checkboxes
  const [activeStatuses, setActiveStatuses] = useState<Record<string, boolean>>({
    validated: true,
    review: true,
    conflict: true,
    changed: true,
  });

  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Check if map container is already initialized by Leaflet
    if ((mapContainerRef.current as any)._leaflet_id) {
      return;
    }

    try {
      const map = L.map(mapContainerRef.current, {
        center: [30.7415, 76.7792],
        zoom: 16,
        zoomControl: true,
      });

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap | BHOOMI-X',
        maxZoom: 19,
      }).addTo(map);

      mapRef.current = map;

      // Buildings Layer
      const bldLayer = L.geoJSON(CHANDIGARH_BUILDINGS, {
        style: {
          color: '#475569',
          fillColor: '#64748b',
          fillOpacity: 0.35,
          weight: 1.5,
        },
        onEachFeature: (feature, layer) => {
          layer.bindTooltip(`🏢 <b>${feature.properties?.building_id}</b>`, { sticky: true });
        }
      }).addTo(map);
      buildingsLayerRef.current = bldLayer;

      // Load Parcels
      loadParcels(map);

      // Invalidate map size after mount to prevent grey/broken tiles
      setTimeout(() => {
        if (mapRef.current) {
          mapRef.current.invalidateSize();
        }
      }, 250);
    } catch (e) {
      console.error('Failed to initialize Leaflet map:', e);
    }

    return () => {
      if (mapRef.current) {
        try {
          mapRef.current.remove();
        } catch {
          // ignore cleanup errors
        }
        mapRef.current = null;
      }
    };
  }, []);

  // Handle initial parcel navigation from Conflicts tab
  useEffect(() => {
    if (initialParcelId) {
      openParcelById(initialParcelId);
    }
  }, [initialParcelId]);

  const [parcelsData, setParcelsData] = useState<any>(CHANDIGARH_SECTOR17_PARCELS);
  const parcelsDataRef = useRef<any>(CHANDIGARH_SECTOR17_PARCELS);

  const loadParcels = async (map: L.Map) => {
    let data = CHANDIGARH_SECTOR17_PARCELS;
    try {
      const apiData = await fetchParcelsGeoJSON();
      if (apiData && apiData.features && apiData.features.length > 0) {
        data = apiData;
      }
    } catch {
      // Offline fallback
    }

    parcelsDataRef.current = data;
    setParcelsData(data);
    renderGeoJSON(map, data);

    if (initialParcelId) {
      openParcelById(initialParcelId, data);
    }
  };

  const renderGeoJSON = (map: L.Map, data: any) => {
    if (geojsonLayerRef.current) {
      try {
        map.removeLayer(geojsonLayerRef.current);
      } catch {
        // ignore
      }
    }

    const layer = L.geoJSON(data, {
      filter: (feature: any) => {
        const p = feature.properties || {};
        if (search && !p.parcel_id?.toLowerCase().includes(search.toLowerCase())) {
          return false;
        }
        if (p.confidence !== undefined && p.confidence < minConf) {
          return false;
        }
        if (showConflictsOnly && p.status !== 'conflict') {
          return false;
        }
        if (p.status && activeStatuses[p.status] === false) {
          return false;
        }
        return true;
      },
      style: (feature: any) => {
        const status = feature.properties?.status || 'pending';
        return STATUS_STYLES[status] || STATUS_STYLES.pending;
      },
      onEachFeature: (feature: any, l: L.Layer) => {
        const p = feature.properties || {};
        l.bindTooltip(`<b>${p.parcel_id}</b><br/>Status: <b>${p.status}</b><br/>Confidence: <b>${p.confidence}%</b>`, { sticky: true });
        l.on('click', () => {
          openDrawer(p, feature);
        });
      },
    });

    if (showParcels) {
      layer.addTo(map);
    }
    geojsonLayerRef.current = layer;

    // Fit map bounds to parcels if layer has bounds and user hasn't zoomed
    try {
      const bounds = layer.getBounds();
      if (bounds && bounds.isValid()) {
        map.fitBounds(bounds, { padding: [20, 20], maxZoom: 18 });
      }
    } catch (e) {
      // ignore
    }
  };

  // Trigger re-filtering when filters change
  useEffect(() => {
    if (mapRef.current) {
      renderGeoJSON(mapRef.current, parcelsDataRef.current || parcelsData);
    }
  }, [search, minConf, showConflictsOnly, activeStatuses, showParcels, parcelsData]);

  // Toggle buildings
  useEffect(() => {
    if (!mapRef.current || !buildingsLayerRef.current) return;
    try {
      if (showBuildings) {
        buildingsLayerRef.current.addTo(mapRef.current);
      } else {
        mapRef.current.removeLayer(buildingsLayerRef.current);
      }
    } catch {
      // ignore
    }
  }, [showBuildings]);

  const openParcelById = (id: string, dataset?: any) => {
    const dataToSearch = dataset || parcelsDataRef.current || parcelsData;
    const match = dataToSearch?.features?.find((f: any) => f.properties?.parcel_id === id);
    if (match) {
      openDrawer(match.properties, match);
    }
  };

  const openDrawer = async (props: any, feature?: any) => {
    // Always start with the known-good GeoJSON properties
    setSelectedParcel(props);
    setDrawerOpen(true);

    // Try enriching with API detail (may have extra fields)
    try {
      const detail = await fetchParcelDetail(props.parcel_id);
      if (detail && detail.parcel_id) {
        setSelectedParcel(detail);
      }
    } catch {
      // Offline — keep using GeoJSON props (already set above)
    }

    // Zoom map to feature if available safely
    if (feature && feature.geometry && mapRef.current) {
      try {
        const coords = feature.geometry.coordinates?.[0];
        if (coords && coords.length > 0 && Array.isArray(coords[0])) {
          const lat = coords[0][1];
          const lng = coords[0][0];
          if (typeof lat === 'number' && typeof lng === 'number') {
            mapRef.current.flyTo([lat, lng], 17, { duration: 0.8 });
          }
        }
      } catch (e) {
        console.warn('Could not zoom to parcel coordinates:', e);
      }
    }
  };

  const closeDrawer = () => {
    setDrawerOpen(false);
    setSelectedParcel(null);
  };

  const handleReview = async (decision: string) => {
    if (!selectedParcel) return;
    try {
      await createReview({ parcel_id: selectedParcel.parcel_id, decision, reviewer: 'admin' });
      alert(`Recorded: Parcel ${selectedParcel.parcel_id} action -> ${decision}`);
    } catch {
      alert(`Recorded action (offline mode): ${selectedParcel.parcel_id} -> ${decision}`);
    }
    closeDrawer();
  };

  const p = selectedParcel;
  const confColor = p ? (p.confidence >= 90 ? '#10b981' : p.confidence >= 70 ? '#f59e0b' : '#ef4444') : '#94a3b8';

  return (
    <div className="map-workspace-layout">
      {/* Sidebar Controls */}
      <aside className="map-sidebar">
        <div className="sidebar-section">
          <input
            className="map-search"
            placeholder="Search parcel ID (e.g. P-104)..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>

        <div className="sidebar-section">
          <div className="section-title" style={{ fontSize: 12 }}>🗂 Map Layers</div>
          <div className="layer-toggle">
            <label>
              <input type="checkbox" checked={showParcels} onChange={e => setShowParcels(e.target.checked)} />
              Parcels Layer
            </label>
          </div>
          <div className="layer-toggle">
            <label>
              <input type="checkbox" checked={showBuildings} onChange={e => setShowBuildings(e.target.checked)} />
              Building Footprints
            </label>
          </div>
          <div className="layer-toggle">
            <label style={{ color: '#ef4444', fontWeight: 600 }}>
              <input type="checkbox" checked={showConflictsOnly} onChange={e => setShowConflictsOnly(e.target.checked)} />
              Show Conflicts Only
            </label>
          </div>
        </div>

        <div className="sidebar-section">
          <div className="section-title" style={{ fontSize: 12 }}>🎯 Confidence Threshold</div>
          <input
            type="range"
            min={0}
            max={100}
            value={minConf}
            onChange={e => setMinConf(+e.target.value)}
            style={{ width: '100%' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#64748b' }}>
            <span>0%</span>
            <span style={{ fontWeight: 700, color: 'var(--navy-500)' }}>Min: {minConf}%</span>
            <span>100%</span>
          </div>
        </div>

        <div className="sidebar-section">
          <div className="section-title" style={{ fontSize: 12 }}>✅ Filter by Status</div>
          {['validated', 'review', 'conflict', 'changed'].map(s => (
            <label key={s} style={{ display: 'flex', alignItems: 'center', gap: 7, fontSize: 13, padding: '4px 0', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={activeStatuses[s]}
                onChange={e => setActiveStatuses(prev => ({ ...prev, [s]: e.target.checked }))}
              />
              <span className={`badge badge-${s === 'validated' ? 'green' : s === 'review' ? 'amber' : s === 'conflict' ? 'red' : 'blue'}`}>
                {s.toUpperCase()}
              </span>
            </label>
          ))}
        </div>

        <div className="sidebar-section" style={{ marginTop: 'auto', textAlign: 'center', fontSize: 11, color: '#64748b' }}>
          <b>Pilot Area:</b> Chandigarh, Sector 17<br />
          <b>CRS:</b> EPSG:4326 (WGS 84)<br />
          <span style={{ color: '#f59e0b', fontWeight: 600 }}>⚠ Synthetic demo data</span>
        </div>
      </aside>

      {/* Map View */}
      <div className="map-container-wrap">
        <div ref={mapContainerRef} className="map-element" style={{ width: '100%', height: '100%', minHeight: '400px' }} />

        {/* Parcel Inspection Floating Drawer */}
        {drawerOpen && p && (
          <div className="parcel-drawer open">
            <div className="drawer-header">
              <div>
                <div style={{ fontSize: 20, fontWeight: 800 }}>{p.parcel_id}</div>
                <span className={`badge badge-${p.status === 'validated' ? 'green' : p.status === 'review' ? 'amber' : p.status === 'conflict' ? 'red' : 'blue'}`} style={{ marginTop: 6 }}>
                  {p.status === 'validated' ? '✓ VALIDATED' : p.status === 'review' ? '⏳ REVIEW REQUIRED' : p.status === 'conflict' ? '⚠ CONFLICT' : 'Δ CHANGED'}
                </span>
              </div>
              <button className="drawer-close" onClick={closeDrawer} title="Close">✕</button>
            </div>

            {/* Circular Confidence Score Gauge from Prototype */}
            <div className="drawer-section" style={{ textAlign: 'center' }}>
              <div className="conf-gauge">
                <svg viewBox="0 0 120 120">
                  <circle className="conf-gauge-bg" cx="60" cy="60" r="50" />
                  <circle
                    className="conf-gauge-fill"
                    cx="60" cy="60" r="50"
                    stroke={confColor}
                    strokeDasharray="314"
                    strokeDashoffset={314 - ((p.confidence || 0) / 100) * 314}
                  />
                </svg>
                <div className="conf-gauge-text">
                  <div className="conf-gauge-value" style={{ color: confColor }}>
                    {p.confidence}%
                  </div>
                  <div className="conf-gauge-label">Confidence</div>
                </div>
              </div>
            </div>

            {/* Source Evidence Grid */}
            <div className="drawer-section">
              <div className="drawer-title">Source Evidence</div>
              <div className="source-evidence">
                {[
                  { key: 'cadastral', name: 'Cadastral', val: p.sources?.cadastral ?? true },
                  { key: 'revenue', name: 'Revenue', val: p.sources?.revenue ?? (p.status !== 'conflict' || p.parcel_id !== 'P-107') },
                  { key: 'municipal', name: 'Municipal', val: p.sources?.municipal ?? (p.parcel_id !== 'P-112') },
                  { key: 'gnss', name: 'GNSS', val: p.sources?.gnss ?? (p.parcel_id !== 'P-106' && p.parcel_id !== 'P-113') },
                  { key: 'drone', name: 'Drone/ORI', val: p.sources?.drone ?? (p.parcel_id !== 'P-108' && p.parcel_id !== 'P-120') },
                ].map(s => (
                  <div key={s.key} className="source-ev-item">
                    <span className="source-ev-icon">{s.val ? '✅' : '❌'}</span>
                    <span>{s.name}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Score Breakdown Bars */}
            <div className="drawer-section">
              <div className="drawer-title">Score Breakdown</div>
              <div className="score-bar-row">
                <div className="score-bar-label">Spatial</div>
                <div className="score-bar-track">
                  <div className="score-bar-fill" style={{ width: `${p.spatial_score ?? (p.spatial ?? 92)}%`, background: 'var(--navy-500)' }} />
                </div>
                <div className="score-bar-value">{p.spatial_score ?? (p.spatial ?? 92)}%</div>
              </div>
              <div className="score-bar-row">
                <div className="score-bar-label">Attribute</div>
                <div className="score-bar-track">
                  <div className="score-bar-fill" style={{ width: `${p.attribute_score ?? (p.attribute ?? 88)}%`, background: '#6366f1' }} />
                </div>
                <div className="score-bar-value">{p.attribute_score ?? (p.attribute ?? 88)}%</div>
              </div>
              <div className="score-bar-row">
                <div className="score-bar-label">Source Agree</div>
                <div className="score-bar-track">
                  <div className="score-bar-fill" style={{ width: `${p.source_agreement ?? (p.sourceAgree ?? 90)}%`, background: 'var(--green-500)' }} />
                </div>
                <div className="score-bar-value">{p.source_agreement ?? (p.sourceAgree ?? 90)}%</div>
              </div>
            </div>

            {/* Evidence & Attributes Table */}
            <div className="drawer-section">
              <div className="drawer-title">Evidence Details</div>
              <table style={{ width: '100%', fontSize: 12.5, borderCollapse: 'collapse' }}>
                <tbody>
                  <tr>
                    <td style={{ padding: '5px 0', color: 'var(--grey-500)' }}>Cadastral Area</td>
                    <td style={{ padding: '5px 0', fontWeight: 700, textAlign: 'right' }}>{p.areaCad || p.area} m²</td>
                  </tr>
                  <tr>
                    <td style={{ padding: '5px 0', color: 'var(--grey-500)' }}>Revenue Area</td>
                    <td style={{ padding: '5px 0', fontWeight: 700, textAlign: 'right' }}>{p.areaRev !== undefined && p.areaRev !== null ? `${p.areaRev} m²` : `${p.area} m²`}</td>
                  </tr>
                  <tr>
                    <td style={{ padding: '5px 0', color: 'var(--grey-500)' }}>GNSS Area</td>
                    <td style={{ padding: '5px 0', fontWeight: 700, textAlign: 'right' }}>{p.areaGnss !== undefined && p.areaGnss !== null ? `${p.areaGnss} m²` : (p.sources?.gnss ? `${p.area} m²` : '—')}</td>
                  </tr>
                  <tr>
                    <td style={{ padding: '5px 0', color: 'var(--grey-500)' }}>Drone Estimate</td>
                    <td style={{ padding: '5px 0', fontWeight: 700, textAlign: 'right' }}>{p.areaDrone !== undefined && p.areaDrone !== null ? `${p.areaDrone} m²` : (p.sources?.drone ? `${p.area} m²` : '—')}</td>
                  </tr>
                  <tr>
                    <td style={{ padding: '5px 0', color: 'var(--grey-500)' }}>Land Use</td>
                    <td style={{ padding: '5px 0', fontWeight: 700, textAlign: 'right' }}>{p.land_use || p.landUse}</td>
                  </tr>
                  <tr>
                    <td style={{ padding: '5px 0', color: 'var(--grey-500)' }}>Owner</td>
                    <td style={{ padding: '5px 0', fontWeight: 700, textAlign: 'right' }}>{p.owner}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            {/* AI Recommendation / Explanation */}
            <div className="drawer-section">
              <div className="drawer-title">AI Recommendation</div>
              <div className="ai-recommendation">
                <div className="ai-rec-label">🤖 AI Analysis</div>
                <span>{p.recommendation || p.rec || p.explanation || 'Records aligned according to spatial and attribute consensus rules.'}</span>
              </div>
            </div>

            {/* Human Verification Action Buttons */}
            <div className="drawer-actions">
              <button className="btn btn-success" style={{ flex: 1 }} onClick={() => handleReview('accepted')}>
                ✓ Accept
              </button>
              <button className="btn btn-danger btn-sm" style={{ flex: 1 }} onClick={() => handleReview('rejected')}>
                ✗ Reject
              </button>
              <button className="btn btn-ghost btn-sm" style={{ flex: 1 }} onClick={() => handleReview('escalated')}>
                ↑ Escalate
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
