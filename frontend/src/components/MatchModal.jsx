import React, { useState, useEffect } from 'react';
import { X, CheckCircle, ShieldAlert, GitPullRequest, ArrowRight, Lightbulb, Edit3, Send } from 'lucide-react';
import { api } from '../api/client';

export default function MatchModal({ incident, onClose, onResolved }) {
  const [matches, setMatches] = useState([]);
  const [loadingMatches, setLoadingMatches] = useState(true);
  const [showCustomForm, setShowCustomForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form State
  const [rootCause, setRootCause] = useState('');
  const [fixDescription, setFixDescription] = useState('');
  const [fixPrUrl, setFixPrUrl] = useState('');

  useEffect(() => {
    if (incident) {
      fetchMatches();
    }
  }, [incident]);

  const fetchMatches = async () => {
    setLoadingMatches(true);
    try {
      const res = await api.getMatches(incident.id);
      setMatches(res.matches || []);
    } catch (err) {
      console.error('Error fetching incident matches:', err);
    } finally {
      setLoadingMatches(false);
    }
  };

  const topMatch = matches.length > 0 ? matches[0] : null;

  // Handle "Use Previous Fix" button click
  const handleUsePreviousFix = async () => {
    if (!topMatch) return;
    setIsSubmitting(true);
    try {
      const prevInc = topMatch.incident;
      await api.resolveIncident(incident.id, {
        root_cause: `[Applied Memory Fix from Inc #${prevInc.id}] ${prevInc.root_cause}`,
        fix_description: prevInc.fix_description,
        fix_pr_url: prevInc.fix_pr_url || '',
        resolution_verified: true
      });
      onResolved();
      onClose();
    } catch (err) {
      alert(`Resolution failed: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle "Investigate New" submission
  const handleInvestigateNewSubmit = async (e) => {
    e.preventDefault();
    if (!rootCause || !fixDescription) {
      alert('Please fill in both Root Cause and Fix Description.');
      return;
    }
    setIsSubmitting(true);
    try {
      await api.resolveIncident(incident.id, {
        root_cause: rootCause,
        fix_description: fixDescription,
        fix_pr_url: fixPrUrl,
        resolution_verified: true
      });
      onResolved();
      onClose();
    } catch (err) {
      alert(`Resolution failed: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!incident) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="modal-header">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.35rem' }}>
              <span className="service-tag">{incident.service}</span>
              <span className="endpoint-path">{incident.endpoint}</span>
              <span className={incident.status === 'OPEN' ? 'tag-status-open' : 'tag-status-resolved'}>
                {incident.status}
              </span>
            </div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '800', color: 'white' }}>
              Incident #{incident.id}: {incident.error_type}
            </h2>
          </div>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {/* Current Incident Details */}
        <div style={{ marginBottom: '1.5rem', background: '#090d16', padding: '1rem', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <h4 style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.35rem' }}>ERROR MESSAGE</h4>
          <p style={{ fontSize: '0.9rem', color: '#f8fafc', marginBottom: '0.75rem' }}>{incident.error_message}</p>
          {incident.stack_trace && (
            <>
              <h4 style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.35rem' }}>STACK TRACE</h4>
              <div className="code-block">{incident.stack_trace}</div>
            </>
          )}
        </div>

        {/* If already resolved */}
        {incident.status === 'RESOLVED' ? (
          <div className="alert-box alert-success" style={{ flexDirection: 'column' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: '700' }}>
              <CheckCircle size={20} /> Verified Resolution Recorded
            </div>
            <p style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>
              <strong>Root Cause:</strong> {incident.root_cause}
            </p>
            <p style={{ fontSize: '0.85rem', marginTop: '0.25rem' }}>
              <strong>Fix Description:</strong> {incident.fix_description}
            </p>
            {incident.fix_pr_url && (
              <p style={{ fontSize: '0.85rem', marginTop: '0.25rem' }}>
                <strong>Pull Request:</strong> <a href={incident.fix_pr_url} target="_blank" rel="noreferrer" style={{ color: '#38bdf8' }}>{incident.fix_pr_url}</a>
              </p>
            )}
          </div>
        ) : (
          /* Memory Match Section for OPEN Incident */
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: '700', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Lightbulb color="#f59e0b" size={20} /> Historical Memory Match Engine
            </h3>

            {loadingMatches ? (
              <div style={{ padding: '2rem', textAlign: 'center', color: '#94a3b8' }}>
                Analyzing incident memory vector similarity...
              </div>
            ) : matches.length === 0 ? (
              <div className="alert-box alert-warning">
                No previous historical resolutions match this incident. You can investigate and enter a new fix below.
              </div>
            ) : (
              /* Display Top Memory Match */
              <div className="match-box">
                <div className="match-header">
                  <div>
                    <span style={{ fontSize: '0.8rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: '700' }}>
                      Top Historical Match (Incident #{topMatch.incident.id})
                    </span>
                    <div style={{ fontSize: '1rem', fontWeight: '700', color: 'white', marginTop: '0.2rem' }}>
                      {topMatch.incident.error_type} on {topMatch.incident.endpoint}
                    </div>
                  </div>
                  <div className="similarity-score-badge">
                    {topMatch.similarity_score}% SIMILARITY
                  </div>
                </div>

                {/* Evidence Breakdown */}
                <div style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: '600', marginBottom: '0.25rem' }}>
                  MATCH EVIDENCE BREAKDOWN:
                </div>
                <div className="evidence-grid">
                  <div className="evidence-item">
                    <div className="evidence-label">Endpoint</div>
                    <div className="evidence-val">{topMatch.evidence.endpoint_score}%</div>
                  </div>
                  <div className="evidence-item">
                    <div className="evidence-label">Error Type</div>
                    <div className="evidence-val">{topMatch.evidence.error_type_score}%</div>
                  </div>
                  <div className="evidence-item">
                    <div className="evidence-label">Msg TF-IDF</div>
                    <div className="evidence-val">{topMatch.evidence.message_tfidf_score}%</div>
                  </div>
                  <div className="evidence-item">
                    <div className="evidence-label">Stack TF-IDF</div>
                    <div className="evidence-val">{topMatch.evidence.stack_tfidf_score}%</div>
                  </div>
                </div>

                {/* Past Fix Memory Details */}
                <div style={{ marginTop: '1rem', padding: '0.85rem', background: '#090d16', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
                  <div style={{ fontSize: '0.8rem', color: '#38bdf8', fontWeight: '700', marginBottom: '0.35rem' }}>
                    KNOWN ROOT CAUSE:
                  </div>
                  <p style={{ fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '0.75rem' }}>
                    {topMatch.incident.root_cause}
                  </p>

                  <div style={{ fontSize: '0.8rem', color: '#10b981', fontWeight: '700', marginBottom: '0.35rem' }}>
                    VERIFIED PREVIOUS FIX:
                  </div>
                  <p style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>
                    {topMatch.incident.fix_description}
                  </p>
                  {topMatch.incident.fix_pr_url && (
                    <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: '#64748b' }}>
                      PR Link: <span style={{ color: '#38bdf8' }}>{topMatch.incident.fix_pr_url}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Action Bar with Mandatory Self-Test Buttons */}
            <div className="modal-actions-banner">
              <div style={{ fontSize: '0.85rem', fontWeight: '700', color: '#94a3b8' }}>
                HUMAN-IN-THE-LOOP ACTION REQUIRED (No fix is ever auto-applied):
              </div>

              <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                {topMatch && !showCustomForm && (
                  <button
                    id="btn-use-previous-fix"
                    className="btn btn-emerald"
                    onClick={handleUsePreviousFix}
                    disabled={isSubmitting}
                  >
                    <CheckCircle size={18} />
                    Use Previous Fix
                  </button>
                )}

                <button
                  id="btn-investigate-new"
                  className="btn btn-secondary"
                  onClick={() => setShowCustomForm(!showCustomForm)}
                  disabled={isSubmitting}
                >
                  <Edit3 size={18} />
                  {showCustomForm ? 'Cancel New Investigation' : 'Investigate New'}
                </button>
              </div>

              {/* Form for "Investigate New" */}
              {showCustomForm && (
                <form onSubmit={handleInvestigateNewSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem', marginTop: '0.5rem', background: '#090d16', padding: '1rem', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
                  <h4 style={{ fontSize: '0.9rem', color: 'white', fontWeight: '700' }}>Enter Novel Root Cause & Resolution</h4>
                  
                  <div>
                    <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.25rem' }}>ROOT CAUSE *</label>
                    <textarea
                      id="input-root-cause"
                      rows={2}
                      placeholder="Describe what caused this failure..."
                      value={rootCause}
                      onChange={e => setRootCause(e.target.value)}
                      required
                      style={{ width: '100%', padding: '0.5rem', background: '#111827', border: '1px solid var(--border-color)', borderRadius: '8px', color: 'white', fontFamily: 'var(--font-sans)', outline: 'none' }}
                    />
                  </div>

                  <div>
                    <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.25rem' }}>FIX DESCRIPTION *</label>
                    <textarea
                      id="input-fix-description"
                      rows={2}
                      placeholder="Describe the solution applied to fix this..."
                      value={fixDescription}
                      onChange={e => setFixDescription(e.target.value)}
                      required
                      style={{ width: '100%', padding: '0.5rem', background: '#111827', border: '1px solid var(--border-color)', borderRadius: '8px', color: 'white', fontFamily: 'var(--font-sans)', outline: 'none' }}
                    />
                  </div>

                  <div>
                    <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.25rem' }}>PULL REQUEST URL (OPTIONAL)</label>
                    <input
                      id="input-fix-pr-url"
                      type="url"
                      placeholder="https://github.com/org/repo/pull/123"
                      value={fixPrUrl}
                      onChange={e => setFixPrUrl(e.target.value)}
                      style={{ width: '100%', padding: '0.5rem', background: '#111827', border: '1px solid var(--border-color)', borderRadius: '8px', color: 'white', fontFamily: 'var(--font-sans)', outline: 'none' }}
                    />
                  </div>

                  <button
                    id="btn-submit-investigation"
                    type="submit"
                    className="btn btn-primary"
                    disabled={isSubmitting}
                    style={{ alignSelf: 'flex-start' }}
                  >
                    <Send size={16} />
                    Submit Verified Resolution
                  </button>
                </form>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
