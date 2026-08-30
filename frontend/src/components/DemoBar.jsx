import React from 'react';
import { RefreshCw, Zap, VolumeX } from 'lucide-react';

export default function DemoBar({ onSeed, onTriggerDuplicate, onSimulateDrop, loading }) {
  return (
    <div className="demo-bar">
      <div className="demo-title-box">
        <span className="demo-badge">Interactive Demo Controls</span>
        <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
          Test similarity matching, zero-log silent drops & technical debt limits
        </span>
      </div>

      <div className="demo-actions">
        <button
          id="btn-reset-seed"
          className="btn btn-primary"
          onClick={onSeed}
          disabled={loading}
        >
          <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
          Reset & Seed
        </button>

        <button
          id="btn-trigger-duplicate"
          className="btn btn-amber"
          onClick={onTriggerDuplicate}
          disabled={loading}
        >
          <Zap size={16} />
          Trigger Duplicate Incident
        </button>

        <button
          id="btn-simulate-drop"
          className="btn btn-rose"
          onClick={onSimulateDrop}
          disabled={loading}
        >
          <VolumeX size={16} />
          Simulate Silent Drop
        </button>
      </div>
    </div>
  );
}
