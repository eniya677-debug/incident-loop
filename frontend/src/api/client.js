import { ENDPOINTS } from './config';

async function handleResponse(res) {
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API Error ${res.status}: ${errorText || res.statusText}`);
  }
  return res.json();
}

export const api = {
  // Incidents
  async getIncidents(status = null, service = null) {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (service) params.append('service', service);
    const url = params.toString() ? `${ENDPOINTS.INCIDENTS}?${params.toString()}` : ENDPOINTS.INCIDENTS;
    const res = await fetch(url);
    return handleResponse(res);
  },

  async getIncident(id) {
    const res = await fetch(ENDPOINTS.INCIDENT_DETAIL(id));
    return handleResponse(res);
  },

  async getMatches(id) {
    const res = await fetch(ENDPOINTS.INCIDENT_MATCHES(id));
    return handleResponse(res);
  },

  async resolveIncident(id, { root_cause, fix_description, fix_pr_url, resolution_verified = true }) {
    const res = await fetch(ENDPOINTS.INCIDENT_RESOLVE(id), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        root_cause,
        fix_description,
        fix_pr_url,
        resolution_verified,
      }),
    });
    return handleResponse(res);
  },

  // Silent Failures
  async getSilentFailures() {
    const res = await fetch(ENDPOINTS.SILENT_FAILURES);
    return handleResponse(res);
  },

  // Technical Debt
  async getTechnicalDebt() {
    const res = await fetch(ENDPOINTS.TECHNICAL_DEBT);
    return handleResponse(res);
  },

  // Demo Controls
  async seedDemoData() {
    const res = await fetch(ENDPOINTS.SEED, { method: 'POST' });
    return handleResponse(res);
  },

  async triggerDuplicateIncident() {
    const res = await fetch(ENDPOINTS.TRIGGER_DUPLICATE, { method: 'POST' });
    return handleResponse(res);
  },

  async simulateSilentDrop() {
    const res = await fetch(ENDPOINTS.SIMULATE_SILENT_DROP, { method: 'POST' });
    return handleResponse(res);
  },
};
