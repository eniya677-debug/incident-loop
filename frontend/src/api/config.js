/**
 * Centralized Single Source of Truth for Frontend API Endpoint URLs.
 * Matches backend constants defined in `backend/app/constants.py`.
 */

export const API_BASE_URL = 'http://127.0.0.1:8000/api';

export const ENDPOINTS = {
  INCIDENTS: `${API_BASE_URL}/incidents`,
  INCIDENT_DETAIL: (id) => `${API_BASE_URL}/incidents/${id}`,
  INCIDENT_MATCHES: (id) => `${API_BASE_URL}/incidents/${id}/matches`,
  INCIDENT_RESOLVE: (id) => `${API_BASE_URL}/incidents/${id}/resolve`,

  HEARTBEAT: `${API_BASE_URL}/activity-heartbeat`,
  SILENT_FAILURES: `${API_BASE_URL}/silent-failures`,
  BASELINES: `${API_BASE_URL}/activity-baselines`,

  TECHNICAL_DEBT: `${API_BASE_URL}/technical-debt`,

  SEED: `${API_BASE_URL}/seed`,
  TRIGGER_DUPLICATE: `${API_BASE_URL}/trigger-duplicate`,
  SIMULATE_SILENT_DROP: `${API_BASE_URL}/simulate-silent-drop`,
};
