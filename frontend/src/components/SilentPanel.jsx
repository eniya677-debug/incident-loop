import React from 'react';
import { VolumeX, ShieldCheck, AlertOctagon } from 'lucide-react';

export default function SilentPanel({ silentFailures }) {
  return (
    <div className="glass-card">
      <div className="section-header" style={{ marginBottom: '1rem' }}>
        <div className="section-title" style={{ fontSize: '1rem' }}>
          <VolumeX size={18} color="#f43f5e" />
          Silent Failure Detector
          <span className="count-badge" style={{ color: silentFailures.length > 0 ? '#f43f5e' : '#10b981' }}>
            {silentFailures.length} Anomalies
          </span>
        </div>
      </div>

      <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '1rem' }}>
        Monitors heartbeat baselines to catch silent service drops with 0 error logs.
      </p>

      {silentFailures.length === 0 ? (
        <div style={{ padding: '1rem', background: '#090d16', borderRadius: '10px', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: '#10b981' }}>
          <ShieldCheck size={16} /> All monitored endpoints healthy. Traffic matching baselines.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {silentFailures.map((s, idx) => (
            <div
              key={idx}
              style={{
                background: 'rgba(244, 63, 94, 0.1)',
                border: '1px solid rgba(244, 63, 94, 0.3)',
                borderRadius: '12px',
                padding: '1rem'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                <span className="service-tag">{s.service}</span>
                <span style={{ fontSize: '0.7rem', fontWeight: '800', color: '#f43f5e', textTransform: 'uppercase', padding: '0.15rem 0.4rem', background: 'rgba(244, 63, 94, 0.2)', borderRadius: '4px' }}>
                  {s.status}
                </span>
              </div>

              <div style={{ fontSize: '0.9rem', fontWeight: '700', color: 'white', fontFamily: 'var(--font-mono)' }}>
                {s.endpoint}
              </div>

              <div style={{ fontSize: '0.75rem', color: '#cbd5e1', marginTop: '0.4rem' }}>
                <strong>Inactive for:</strong> {Math.round(s.seconds_inactive / 60)} minutes (Expected window: {Math.round(s.window / 60)}m)
              </div>

              <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.4rem', background: '#090d16', padding: '0.5rem', borderRadius: '6px' }}>
                <strong style={{ color: '#f43f5e' }}>Recommendation:</strong> {s.recommendation}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
