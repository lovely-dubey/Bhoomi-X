/**
 * BHOOMI-X React Frontend — App Component
 * Routes between Dashboard, Map, Conflicts, Data, and Pipeline screens.
 * Includes Error Boundary to guarantee zero white screen crashes.
 */

import { useState, Component, type ErrorInfo, type ReactNode } from 'react';
import Dashboard from './pages/Dashboard';
import MapWorkspace from './pages/MapWorkspace';
import Conflicts from './pages/Conflicts';
import DataIngestion from './pages/DataIngestion';
import Pipeline from './pages/Pipeline';
import './index.css';

type Tab = 'dashboard' | 'map' | 'conflicts' | 'data' | 'pipeline';

const TABS: { id: Tab; label: string; icon: string }[] = [
  { id: 'dashboard', label: 'Dashboard', icon: '⊞' },
  { id: 'map', label: 'Map', icon: '🗺' },
  { id: 'conflicts', label: 'Conflicts', icon: '⚠' },
  { id: 'data', label: 'Data', icon: '⬆' },
  { id: 'pipeline', label: 'Pipeline', icon: '⚡' },
];

interface ErrorBoundaryProps {
  children: ReactNode;
  fallbackTab: () => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

class TabErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('BHOOMI-X Tab Error Caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '40px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
          <div className="card" style={{ maxWidth: '560px', width: '100%', textAlign: 'center', padding: '32px' }}>
            <div style={{ fontSize: '42px', marginBottom: '12px' }}>⚠️</div>
            <h3 style={{ fontSize: '18px', fontWeight: 800, marginBottom: '8px', color: 'var(--grey-900)' }}>
              Component Render Recovered
            </h3>
            <p className="text-muted" style={{ fontSize: '13px', marginBottom: '20px' }}>
              {this.state.error?.message || 'An unexpected error occurred while rendering this tab.'}
            </p>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
              <button
                className="btn btn-primary"
                onClick={() => this.setState({ hasError: false })}
              >
                ↻ Retry Tab
              </button>
              <button
                className="btn btn-ghost"
                onClick={() => {
                  this.setState({ hasError: false });
                  this.props.fallbackTab();
                }}
              >
                ⊞ Return to Dashboard
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>('dashboard');
  const [selectedParcelId, setSelectedParcelId] = useState<string | undefined>();
  const [conflictCount] = useState(5);
  const [pipelineAutoRun, setPipelineAutoRun] = useState(false);

  const handleNavigate = (tab: string, parcelId?: string) => {
    if (tab === 'pipeline_autorun') {
      setActiveTab('pipeline');
      setPipelineAutoRun(true);
      return;
    }
    setActiveTab(tab as Tab);
    setPipelineAutoRun(false);
    if (parcelId) {
      setSelectedParcelId(parcelId);
    }
  };

  return (
    <div className="app">
      {/* Enhanced Header */}
      <header className="app-header">
        {/* Animated gradient border at bottom */}
        <div className="header-glow-border" />

        {/* Top bar: Brand + Actions */}
        <div className="header-top-bar">
          <div className="brand-block" onClick={() => setActiveTab('dashboard')} style={{ cursor: 'pointer' }}>
            <div className="brand-logo-wrap">
              <div className="brand-logo-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                  <polygon points="1 6 12 2 23 6 23 18 12 22 1 18" />
                  <line x1="12" y1="2" x2="12" y2="22" />
                  <line x1="1" y1="6" x2="23" y2="6" />
                  <polyline points="6 4 6 20" opacity="0.4" />
                  <polyline points="18 4 18 20" opacity="0.4" />
                </svg>
              </div>
              <div className="brand-text-container">
                <div className="brand-name">BHOOMI-X</div>
                <div className="brand-sub">AI-Powered Geospatial Reconciliation & Harmonization</div>
              </div>
            </div>
          </div>

          <div className="header-right">
            {/* Live System Status */}
            <div className="header-status-pill">
              <span className="status-dot status-dot--live" />
              <span>System Online</span>
            </div>

            {/* Notification Bell */}
            <button className="header-icon-btn" title="Notifications" onClick={() => setActiveTab('conflicts')}>
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                <path d="M13.73 21a2 2 0 0 1-3.46 0" />
              </svg>
              {conflictCount > 0 && <span className="notification-dot">{conflictCount}</span>}
            </button>

            {/* SIH Badge */}
            <span className="sih-badge">
              <span className="sih-badge-icon">🏛</span>
              SIH 2026
            </span>

            {/* User Avatar with name */}
            <div className="user-block">
              <div className="user-avatar">AH</div>
              <div className="user-info">
                <span className="user-name">Admin</span>
                <span className="user-role">Surveyor</span>
              </div>
            </div>
          </div>
        </div>

        {/* Desktop Tab Navigation Row (hidden on mobile) */}
        <nav className="nav-tabs-wrapper desktop-only-nav">
          <div className="nav-tabs">
            {TABS.map(tab => (
              <button
                key={tab.id}
                className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                <span className="tab-icon">{tab.icon}</span>
                <span className="tab-label">{tab.label}</span>
                {tab.id === 'conflicts' && conflictCount > 0 && (
                  <span className="tab-badge">
                    <span className="badge-ping" />
                    {conflictCount}
                  </span>
                )}
                {activeTab === tab.id && <span className="tab-active-indicator" />}
              </button>
            ))}
          </div>
        </nav>
      </header>

      {/* Main Content with Error Boundary */}
      <main className="app-main">
        <TabErrorBoundary key={activeTab} fallbackTab={() => setActiveTab('dashboard')}>
          {activeTab === 'dashboard' && <Dashboard onNavigate={handleNavigate} />}
          {activeTab === 'map' && <MapWorkspace initialParcelId={selectedParcelId} />}
          {activeTab === 'conflicts' && <Conflicts onNavigate={handleNavigate} />}
          {activeTab === 'data' && <DataIngestion onNavigate={handleNavigate} />}
          {activeTab === 'pipeline' && <Pipeline onNavigate={handleNavigate} autoRun={pipelineAutoRun} />}
        </TabErrorBoundary>
      </main>

      {/* Mobile Bottom Navigation Bar — Native App Style */}
      <nav className="mobile-bottom-nav">
        {TABS.map(tab => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              className={`mobile-nav-btn ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <div className="mobile-nav-icon-wrap">
                <span className="mobile-nav-icon">{tab.icon}</span>
                {tab.id === 'conflicts' && conflictCount > 0 && (
                  <span className="mobile-nav-badge">{conflictCount}</span>
                )}
              </div>
              <span className="mobile-nav-label">{tab.label}</span>
              {isActive && <span className="mobile-nav-pill-indicator" />}
            </button>
          );
        })}
      </nav>
    </div>
  );
}
