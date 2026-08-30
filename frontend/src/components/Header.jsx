import React from 'react';
import { Activity, ShieldCheck, Database, Cpu } from 'lucide-react';

export default function Header({ incidentsCount, openCount, resolvedCount }) {
  return (
    <header className="header-bar">
      <div className="brand-section">
        <div className="brand-icon">
          <Activity size={24} />
        </div>
        <div>
          <h1 className="brand-title">IncidentLoop</h1>
          <p className="brand-subtitle">Production Incident Memory & Failure Anomaly Engine</p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
        <div style={{ display: 'flex', gap: '1rem', fontSize: '0.85rem' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: '#94a3b8' }}>
            <Database size={15} color="#38bdf8" /> Memory Pool: <strong style={{ color: '#fff' }}>{incidentsCount}</strong>
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: '#94a3b8' }}>
            <Cpu size={15} color="#f43f5e" /> Active Open: <strong style={{ color: '#f43f5e' }}>{openCount}</strong>
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: '#94a3b8' }}>
            <ShieldCheck size={15} color="#10b981" /> Verified Solved: <strong style={{ color: '#10b981' }}>{resolvedCount}</strong>
          </span>
        </div>

        <div className="status-pill">
          <span className="pulse-dot"></span>
          System Active
        </div>
      </div>
    </header>
  );
}
