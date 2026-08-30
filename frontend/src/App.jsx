import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import DemoBar from './components/DemoBar';
import IncidentList from './components/IncidentList';
import MatchModal from './components/MatchModal';
import SilentPanel from './components/SilentPanel';
import DebtRadar from './components/DebtRadar';
import { api } from './api/client';

export default function App() {
  const [incidents, setIncidents] = useState([]);
  const [silentFailures, setSilentFailures] = useState([]);
  const [techDebtGroups, setTechDebtGroups] = useState([]);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [activeFilter, setActiveFilter] = useState('ALL');
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState(null);

  // Initial load
  useEffect(() => {
    refreshAllData();
  }, []);

  const refreshAllData = async () => {
    try {
      const [incRes, silentRes, debtRes] = await Promise.all([
        api.getIncidents(),
        api.getSilentFailures(),
        api.getTechnicalDebt(),
      ]);
      setIncidents(incRes || []);
      setSilentFailures(silentRes || []);
      setTechDebtGroups(debtRes || []);
    } catch (err) {
      console.error('Error loading dashboard data:', err);
    }
  };

  const showNotify = (msg, type = 'info') => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 4000);
  };

  // Demo Action 1: Reset & Seed
  const handleSeed = async () => {
    setLoading(true);
    try {
      const res = await api.seedDemoData();
      await refreshAllData();
      showNotify(res.message, 'success');
    } catch (err) {
      showNotify(`Reset failed: ${err.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  // Demo Action 2: Trigger Duplicate Incident
  const handleTriggerDuplicate = async () => {
    setLoading(true);
    try {
      const newInc = await api.triggerDuplicateIncident();
      await refreshAllData();
      setSelectedIncident(newInc); // Auto-open match modal for immediate verification!
      showNotify(`Triggered duplicate Incident #${newInc.id} on ${newInc.endpoint}! Match modal opened.`, 'success');
    } catch (err) {
      showNotify(`Trigger failed: ${err.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  // Demo Action 3: Simulate Silent Drop
  const handleSimulateDrop = async () => {
    setLoading(true);
    try {
      const res = await api.simulateSilentDrop();
      await refreshAllData();
      showNotify(res.message, 'warning');
    } catch (err) {
      showNotify(`Simulation failed: ${err.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const openCount = incidents.filter(i => i.status === 'OPEN').length;
  const resolvedCount = incidents.filter(i => i.status === 'RESOLVED').length;

  return (
    <div className="app-container">
      {/* Toast Notification Banner */}
      {notification && (
        <div
          style={{
            position: 'fixed',
            top: '1.5rem',
            right: '2.5rem',
            zIndex: 2000,
            background: notification.type === 'error' ? '#e11d48' : notification.type === 'warning' ? '#d97706' : '#0284c7',
            color: 'white',
            padding: '0.75rem 1.25rem',
            borderRadius: '12px',
            boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
            fontWeight: '600',
            fontSize: '0.9rem',
            animation: 'fadeIn 0.2s ease'
          }}
        >
          {notification.msg}
        </div>
      )}

      {/* Main Header */}
      <Header
        incidentsCount={incidents.length}
        openCount={openCount}
        resolvedCount={resolvedCount}
      />

      {/* Demo Controls Bar */}
      <DemoBar
        onSeed={handleSeed}
        onTriggerDuplicate={handleTriggerDuplicate}
        onSimulateDrop={handleSimulateDrop}
        loading={loading}
      />

      {/* Main Grid Content */}
      <div className="dashboard-grid">
        {/* Left Column: Incident Memory Stream */}
        <IncidentList
          incidents={incidents}
          onSelectIncident={setSelectedIncident}
          activeFilter={activeFilter}
          setFilter={setActiveFilter}
        />

        {/* Right Column: Silent Failures & Tech Debt Radar */}
        <div>
          <SilentPanel silentFailures={silentFailures} />
          <DebtRadar techDebtGroups={techDebtGroups} />
        </div>
      </div>

      {/* Incident Detail & Similarity Match Modal */}
      {selectedIncident && (
        <MatchModal
          incident={selectedIncident}
          onClose={() => setSelectedIncident(null)}
          onResolved={refreshAllData}
        />
      )}
    </div>
  );
}
