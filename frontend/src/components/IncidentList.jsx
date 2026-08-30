import React, { useState } from 'react';
import { AlertTriangle, CheckCircle, Clock, Search, ArrowRight } from 'lucide-react';

export default function IncidentList({ incidents, onSelectIncident, activeFilter, setFilter }) {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredIncidents = incidents.filter(inc => {
    const matchesFilter = activeFilter === 'ALL' || inc.status === activeFilter;
    const matchesQuery = 
      inc.service.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inc.endpoint.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inc.error_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inc.error_message.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesQuery;
  });

  return (
    <div className="glass-card">
      <div className="section-header">
        <div className="section-title">
          <Clock size={20} color="#38bdf8" />
          Incident Memory Stream
          <span className="count-badge">{filteredIncidents.length}</span>
        </div>

        {/* Filter Tabs */}
        <div style={{ display: 'flex', gap: '0.5rem', background: '#090d16', padding: '0.25rem', borderRadius: '10px' }}>
          {['ALL', 'OPEN', 'RESOLVED'].map(tab => (
            <button
              key={tab}
              onClick={() => setFilter(tab)}
              style={{
                background: activeFilter === tab ? '#1e293b' : 'transparent',
                color: activeFilter === tab ? '#38bdf8' : '#94a3b8',
                border: 'none',
                padding: '0.35rem 0.75rem',
                borderRadius: '8px',
                fontSize: '0.75rem',
                fontWeight: '700',
                cursor: 'pointer'
              }}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Search Input */}
      <div style={{ position: 'relative', marginBottom: '1.25rem' }}>
        <Search size={16} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
        <input
          type="text"
          placeholder="Filter memory by service, endpoint, or error type..."
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          style={{
            width: '100%',
            padding: '0.65rem 1rem 0.65rem 2.5rem',
            background: '#090d16',
            border: '1px solid var(--border-color)',
            borderRadius: '10px',
            color: 'white',
            fontFamily: 'var(--font-sans)',
            fontSize: '0.85rem',
            outline: 'none'
          }}
        />
      </div>

      {/* Incident List Cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
        {filteredIncidents.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2.5rem', color: '#64748b' }}>
            No incidents matched your current filter criteria.
          </div>
        ) : (
          filteredIncidents.map(inc => (
            <div
              key={inc.id}
              className={`incident-card ${inc.status === 'OPEN' ? 'open-card' : 'resolved-card'}`}
              onClick={() => onSelectIncident(inc)}
            >
              <div className="incident-card-top">
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <span className="service-tag">{inc.service}</span>
                  <span className="endpoint-path">{inc.endpoint}</span>
                </div>
                <span className={inc.status === 'OPEN' ? 'tag-status-open' : 'tag-status-resolved'}>
                  {inc.status === 'OPEN' ? 'OPEN INCIDENT' : 'RESOLVED'}
                </span>
              </div>

              <div className="error-title">
                {inc.error_type}
              </div>

              <div className="error-msg">
                {inc.error_message}
              </div>

              <div className="incident-meta">
                <span>Category: <strong style={{ color: '#cbd5e1' }}>{inc.category}</strong></span>
                <span>ID: #{inc.id} • {new Date(inc.created_at).toLocaleString()}</span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: '#38bdf8', fontWeight: '600' }}>
                  View Past Matches & Solutions <ArrowRight size={14} />
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
