/**
 * Dashboard Page — Rich Visualization with interactive charts.
 * Uses Chart.js via react-chartjs-2 for doughnut, bar, line, and radar charts.
 */

import { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  RadialLinearScale,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';
import { Doughnut, Bar, Line, Radar } from 'react-chartjs-2';
import type { ParcelStats } from '../types';
import { fetchParcelStats } from '../api';

// Register all Chart.js components
ChartJS.register(
  CategoryScale, LinearScale, BarElement, LineElement,
  PointElement, ArcElement, RadialLinearScale, Filler,
  Tooltip, Legend,
);

// Global chart defaults
ChartJS.defaults.font.family = "'Inter', sans-serif";
ChartJS.defaults.color = '#6b7280';

interface Props {
  onNavigate: (tab: string) => void;
}

export default function Dashboard({ onNavigate }: Props) {
  const [stats, setStats] = useState<ParcelStats>({
    total_parcels: 125, harmonized: 117, high_confidence: 102,
    review_required: 6, conflicts: 5, recent_changes: 3,
  });

  useEffect(() => {
    fetchParcelStats()
      .then(data => {
        if (data && typeof data.total_parcels === 'number') {
          setStats(data);
        }
      })
      .catch(() => {});
  }, []);

  const kpis = [
    { label: 'Total Parcels', value: stats.total_parcels, color: '#3b82f6', icon: '📍', trend: 'Pilot Area: Sector 17', trendIcon: '◉' },
    { label: 'Harmonized', value: stats.harmonized, color: '#10b981', icon: '✓', trend: `${((stats.harmonized / Math.max(stats.total_parcels, 1)) * 100).toFixed(1)}% match rate`, trendIcon: '↗' },
    { label: 'High Confidence', value: stats.high_confidence, color: '#8b5cf6', icon: '◆', trend: '≥90% confidence', trendIcon: '↗' },
    { label: 'Review Required', value: stats.review_required, color: '#f59e0b', icon: '⚑', trend: 'Needs human review', trendIcon: '▼' },
    { label: 'Conflicts', value: stats.conflicts, color: '#ef4444', icon: '⚠', trend: 'Active conflicts', trendIcon: '▼' },
    { label: 'Recent Changes', value: stats.recent_changes, color: '#06b6d4', icon: '↻', trend: 'Last 7 days', trendIcon: '◉' },
  ];

  // === CHART DATA ===

  // 1. Doughnut — Parcel Status Breakdown
  const doughnutData = {
    labels: ['Harmonized', 'High Confidence', 'Review Required', 'Conflicts'],
    datasets: [{
      data: [stats.harmonized, stats.high_confidence, stats.review_required, stats.conflicts],
      backgroundColor: [
        'rgba(16, 185, 129, 0.85)',
        'rgba(139, 92, 246, 0.85)',
        'rgba(245, 158, 11, 0.85)',
        'rgba(239, 68, 68, 0.85)',
      ],
      borderColor: [
        'rgba(16, 185, 129, 1)',
        'rgba(139, 92, 246, 1)',
        'rgba(245, 158, 11, 1)',
        'rgba(239, 68, 68, 1)',
      ],
      borderWidth: 2,
      hoverOffset: 8,
      spacing: 3,
    }],
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '72%',
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          padding: 16,
          usePointStyle: true,
          pointStyleWidth: 10,
          font: { size: 11.5, weight: 600 as const },
        },
      },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.92)',
        titleFont: { size: 13, weight: 700 as const },
        bodyFont: { size: 12 },
        padding: 12,
        cornerRadius: 10,
        displayColors: true,
        boxPadding: 4,
      },
    },
    animation: {
      animateRotate: true,
      animateScale: true,
      duration: 1200,
    },
  };

  // 2. Bar Chart — Data Sources Records Count
  const sources = [
    { name: 'Cadastral Map', records: 125, color: '#3b82f6' },
    { name: 'Revenue Records', records: 118, color: '#8b5cf6' },
    { name: 'Municipal GIS', records: 122, color: '#10b981' },
    { name: 'GNSS Survey', records: 89, color: '#f59e0b' },
    { name: 'Drone / ORI', records: 95, color: '#ef4444' },
  ];

  const barData = {
    labels: sources.map(s => s.name),
    datasets: [{
      label: 'Records',
      data: sources.map(s => s.records),
      backgroundColor: sources.map(s => s.color + 'cc'),
      borderColor: sources.map(s => s.color),
      borderWidth: 2,
      borderRadius: 8,
      borderSkipped: false,
      barThickness: 32,
    }],
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.92)',
        titleFont: { size: 13, weight: 700 as const },
        bodyFont: { size: 12 },
        padding: 12,
        cornerRadius: 10,
        callbacks: {
          label: (ctx: any) => ` ${ctx.parsed.y} records loaded`,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: { color: 'rgba(0,0,0,0.04)', drawBorder: false },
        ticks: { font: { size: 11 }, padding: 8 },
        border: { display: false },
      },
      x: {
        grid: { display: false },
        ticks: { font: { size: 10.5, weight: 600 as const }, padding: 4 },
        border: { display: false },
      },
    },
    animation: {
      duration: 1000,
      easing: 'easeOutQuart' as const,
    },
  };

  // 3. Line Chart — Harmonization Progress Over Time (simulated 7-day trend)
  const lineData = {
    labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Today'],
    datasets: [
      {
        label: 'Parcels Harmonized',
        data: [42, 58, 71, 85, 96, 108, stats.harmonized],
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.08)',
        fill: true,
        tension: 0.4,
        pointRadius: 5,
        pointBackgroundColor: '#10b981',
        pointBorderColor: '#fff',
        pointBorderWidth: 2.5,
        pointHoverRadius: 8,
        borderWidth: 3,
      },
      {
        label: 'Conflicts Detected',
        data: [2, 3, 4, 5, 6, 5, stats.conflicts],
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.05)',
        fill: true,
        tension: 0.4,
        pointRadius: 5,
        pointBackgroundColor: '#ef4444',
        pointBorderColor: '#fff',
        pointBorderWidth: 2.5,
        pointHoverRadius: 8,
        borderWidth: 3,
      },
    ],
  };

  const lineOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        align: 'end' as const,
        labels: {
          usePointStyle: true,
          pointStyleWidth: 8,
          padding: 16,
          font: { size: 11.5, weight: 600 as const },
        },
      },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.92)',
        titleFont: { size: 13, weight: 700 as const },
        bodyFont: { size: 12 },
        padding: 12,
        cornerRadius: 10,
        mode: 'index' as const,
        intersect: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: { color: 'rgba(0,0,0,0.04)', drawBorder: false },
        ticks: { font: { size: 11 }, padding: 8 },
        border: { display: false },
      },
      x: {
        grid: { display: false },
        ticks: { font: { size: 11 }, padding: 4 },
        border: { display: false },
      },
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false,
    },
    animation: {
      duration: 1400,
      easing: 'easeOutQuart' as const,
    },
  };

  // 4. Radar Chart — Data Quality Metrics
  const radarData = {
    labels: ['Spatial Accuracy', 'Attribute Match', 'CRS Validity', 'Boundary Overlap', 'Owner Match', 'Area Consistency'],
    datasets: [{
      label: 'Current Score',
      data: [92, 88, 97, 85, 78, 91],
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59, 130, 246, 0.12)',
      pointBackgroundColor: '#3b82f6',
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
      pointRadius: 5,
      pointHoverRadius: 7,
      borderWidth: 2.5,
      fill: true,
    }, {
      label: 'Target Threshold',
      data: [95, 90, 95, 90, 85, 90],
      borderColor: 'rgba(139, 92, 246, 0.6)',
      backgroundColor: 'rgba(139, 92, 246, 0.06)',
      pointBackgroundColor: '#8b5cf6',
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
      pointRadius: 4,
      pointHoverRadius: 6,
      borderWidth: 2,
      borderDash: [6, 4],
      fill: true,
    }],
  };

  const radarOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          usePointStyle: true,
          pointStyleWidth: 10,
          padding: 16,
          font: { size: 11.5, weight: 600 as const },
        },
      },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.92)',
        titleFont: { size: 13, weight: 700 as const },
        bodyFont: { size: 12 },
        padding: 12,
        cornerRadius: 10,
        callbacks: {
          label: (ctx: any) => ` ${ctx.dataset.label}: ${ctx.parsed.r}%`,
        },
      },
    },
    scales: {
      r: {
        beginAtZero: false,
        min: 50,
        max: 100,
        ticks: {
          stepSize: 10,
          backdropColor: 'transparent',
          font: { size: 10 },
          color: '#9ca3af',
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.06)',
          circular: true,
        },
        pointLabels: {
          font: { size: 11, weight: 600 as const },
          color: '#4b5563',
        },
        angleLines: {
          color: 'rgba(0, 0, 0, 0.06)',
        },
      },
    },
    animation: {
      duration: 1200,
    },
  };

  // Confidence distribution for horizontal bar
  const confDistData = {
    labels: ['≥95%', '90–95%', '80–90%', '70–80%', '<70%'],
    datasets: [{
      label: 'Parcels',
      data: [68, 34, 12, 7, 4],
      backgroundColor: [
        'rgba(16, 185, 129, 0.8)',
        'rgba(59, 130, 246, 0.8)',
        'rgba(139, 92, 246, 0.8)',
        'rgba(245, 158, 11, 0.8)',
        'rgba(239, 68, 68, 0.8)',
      ],
      borderColor: [
        '#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444',
      ],
      borderWidth: 2,
      borderRadius: 6,
      barThickness: 18,
    }],
  };

  const confDistOptions = {
    indexAxis: 'y' as const,
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.92)',
        titleFont: { size: 13, weight: 700 as const },
        bodyFont: { size: 12 },
        padding: 12,
        cornerRadius: 10,
        callbacks: {
          label: (ctx: any) => ` ${ctx.parsed.x} parcels`,
        },
      },
    },
    scales: {
      x: {
        beginAtZero: true,
        grid: { color: 'rgba(0,0,0,0.04)', drawBorder: false },
        ticks: { font: { size: 11 }, padding: 4 },
        border: { display: false },
      },
      y: {
        grid: { display: false },
        ticks: { font: { size: 11, weight: 600 as const }, padding: 8 },
        border: { display: false },
      },
    },
    animation: {
      duration: 1000,
      easing: 'easeOutQuart' as const,
    },
  };

  // Activities for the feed
  const activities = [
    { msg: 'Pipeline completed — 117 parcels harmonized', time: '2 min ago', color: '#10b981', icon: '✓' },
    { msg: 'Conflict detected: P-104 area mismatch (3.5%)', time: '5 min ago', color: '#ef4444', icon: '⚠' },
    { msg: 'P-103 routed to review — boundary discrepancy', time: '5 min ago', color: '#f59e0b', icon: '⚑' },
    { msg: 'GNSS Survey dataset uploaded (89 records)', time: '12 min ago', color: '#3b82f6', icon: '↑' },
    { msg: 'CRS transformation complete → EPSG:4326', time: '15 min ago', color: '#10b981', icon: '◆' },
    { msg: 'Cadastral Map loaded — 125 parcels ingested', time: '20 min ago', color: '#3b82f6', icon: '📍' },
  ];

  return (
    <div className="page-scroll" style={{ padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* KPI Cards Row */}
      <div className="dash-top" style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 14 }}>
        {kpis.map(k => (
          <div key={k.label} className="card kpi-card" style={{ borderTop: `3px solid ${k.color}` }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div className="kpi-label">{k.label}</div>
              <div style={{
                width: 28, height: 28, borderRadius: 8,
                background: k.color + '14', display: 'flex', alignItems: 'center',
                justifyContent: 'center', fontSize: 13,
              }}>{k.icon}</div>
            </div>
            <div className="kpi-value">{k.value}</div>
            <div className="kpi-trend">
              <span style={{ color: k.color, fontWeight: 700 }}>{k.trendIcon}</span>
              {k.trend}
            </div>
          </div>
        ))}
      </div>

      {/* Charts Row 1 — Status Doughnut + Harmonization Trend Line */}
      <div className="dash-charts-row" style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 16 }}>
        {/* Doughnut Chart */}
        <div className="card chart-card">
          <div className="section-title">
            <span style={{ fontSize: 16 }}>🎯</span> Parcel Status Breakdown
          </div>
          <div style={{ position: 'relative', height: 280, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Doughnut data={doughnutData} options={doughnutOptions} />
            {/* Center label */}
            <div style={{
              position: 'absolute', top: '42%', left: '50%', transform: 'translate(-50%, -50%)',
              textAlign: 'center', pointerEvents: 'none',
            }}>
              <div style={{ fontSize: 28, fontWeight: 900, color: '#111827', lineHeight: 1 }}>
                {((stats.harmonized / Math.max(stats.total_parcels, 1)) * 100).toFixed(0)}%
              </div>
              <div style={{ fontSize: 10.5, color: '#6b7280', fontWeight: 600, marginTop: 2 }}>Harmonized</div>
            </div>
          </div>
        </div>

        {/* Line Chart */}
        <div className="card chart-card">
          <div className="section-title">
            <span style={{ fontSize: 16 }}>📈</span> Harmonization Progress (7-day)
          </div>
          <div style={{ height: 280 }}>
            <Line data={lineData} options={lineOptions} />
          </div>
        </div>
      </div>

      {/* Charts Row 2 — Data Sources Bar + Confidence Distribution + Radar */}
      <div className="dash-charts-row" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16 }}>
        {/* Bar Chart */}
        <div className="card chart-card">
          <div className="section-title">
            <span style={{ fontSize: 16 }}>🗄</span> Data Sources
          </div>
          <div style={{ height: 240 }}>
            <Bar data={barData} options={barOptions} />
          </div>
        </div>

        {/* Confidence Distribution */}
        <div className="card chart-card">
          <div className="section-title">
            <span style={{ fontSize: 16 }}>📊</span> Confidence Distribution
          </div>
          <div style={{ height: 240 }}>
            <Bar data={confDistData} options={confDistOptions} />
          </div>
        </div>

        {/* Radar Chart */}
        <div className="card chart-card">
          <div className="section-title">
            <span style={{ fontSize: 16 }}>🔬</span> Data Quality Metrics
          </div>
          <div style={{ height: 240 }}>
            <Radar data={radarData} options={radarOptions} />
          </div>
        </div>
      </div>

      {/* Bottom Row — Activity Feed + Quick Actions */}
      <div className="dash-body" style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16 }}>
        {/* Recent Activity */}
        <div className="card">
          <div className="section-title">🕐 Recent Activity</div>
          {activities.map((a, i) => (
            <div key={i} className="activity-item">
              <div className="activity-dot" style={{ background: a.color }} />
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 13 }}>{a.msg}</div>
                <div className="text-muted" style={{ fontSize: 11, marginTop: 2 }}>{a.time}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Quick Actions */}
        <div className="card">
          <div className="section-title">⚡ Quick Actions</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {[
              { icon: '▶', title: 'Run Harmonization', sub: 'Execute full reconciliation pipeline', tab: 'pipeline', color: '#3b82f6' },
              { icon: '↑', title: 'Upload Dataset', sub: 'Add GeoJSON, CSV, or GeoTIFF', tab: 'data', color: '#10b981' },
              { icon: '⚠', title: 'Review Conflicts', sub: `${stats.conflicts} conflicts pending review`, tab: 'conflicts', color: '#f59e0b' },
              { icon: '↓', title: 'Export Report', sub: 'Download harmonized records', tab: 'data', color: '#8b5cf6' },
            ].map(qa => (
              <button key={qa.title} className="quick-action-btn" onClick={() => onNavigate(qa.tab as any)}>
                <div className="qa-icon" style={{ background: qa.color + '14', color: qa.color }}>{qa.icon}</div>
                <div>
                  <div style={{ fontWeight: 700 }}>{qa.title}</div>
                  <div className="text-muted-qa" style={{ fontSize: 11, opacity: 0.7 }}>{qa.sub}</div>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
