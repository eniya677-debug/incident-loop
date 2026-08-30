import React from 'react';
import { AlertTriangle, Wrench, ShieldAlert } from 'lucide-react';

export default function DebtRadar({ techDebtGroups }) {
  const debtFlagged = techDebtGroups.filter(g => g.flagged_as_debt);

  return (
    <div className="glass-card">
      <div className="section-header" style={{ marginBottom: '1rem' }}>
        <div className="section-title" style={{ fontSize: '1rem' }}>
          <Wrench size={18} color="#f59e0b" />
          Technical Debt Radar
          <span className="count-badge" style={{ color: debtFlagged.length > 0 ? '#f59e0b' : '#94a3b8' }}>
            {debtFlagged.length} High Fragility Endpoints
          </span>
        </div>
      </div>

      <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '1rem' }}>
        Flags endpoints failing repeatedly (&ge; 3 occurrences) to prioritize refactoring over patch fixes.
      </p>

      {techDebtGroups.length === 0 ? (
        <div style={{ padding: '1rem', background: '#090d16', borderRadius: '10px', fontSize: '0.8rem', color: '#94a3b8' }}>
          No technical debt signatures recorded yet.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {techDebtGroups.map((g) => (
            <div
              key={g.id}
              style={{
                background: g.flagged_as_debt ? 'rgba(245, 158, 11, 0.1)' : '#090d16',
                border: g.flagged_as_debt ? '1px solid rgba(245, 158, 11, 0.4)' : '1px solid var(--border-color)',
                borderRadius: '12px',
                padding: '0.85rem'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                <span className="endpoint-path" style={{ margin: 0, fontSize: '0.8rem' }}>
                  {g.service}:{g.endpoint}
                </span>
                <span style={{ fontSize: '0.7rem', fontWeight: '800', color: g.flagged_as_debt ? '#f59e0b' : '#38bdf8', padding: '0.15rem 0.4rem', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '4px' }}>
                  {g.occurrence_count} FAILURES
                </span>
              </div>

              <div style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: '600', marginTop: '0.2rem' }}>
                Signature: <span style={{ fontFamily: 'var(--font-mono)', color: '#94a3b8' }}>{g.error_type}</span>
              </div>

              {g.flagged_as_debt && (
                <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: '#fef3c7', background: 'rgba(15, 23, 42, 0.8)', padding: '0.5rem', borderRadius: '6px', borderLeft: '3px solid #f59e0b' }}>
                  <strong style={{ color: '#f59e0b' }}>Debt Alert:</strong> {g.recommendation}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
