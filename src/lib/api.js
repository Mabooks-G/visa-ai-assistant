/**
 * API client for the Visa AI Assistant backend.
 * All requests are routed through the FastAPI backend, not directly to Supabase.
 */

/**
 * Use the same hostname the page was loaded from, on port 8000.
 * This works both locally and when accessing the server over the network.
 * Set VITE_API_URL to override (e.g. in production).
 */
const API_HOST = window.location.hostname;
const API_BASE = import.meta.env.VITE_API_URL || `http://${API_HOST}:8000/api`;

async function request(method, path, options = {}) {
  const url = `${API_BASE}${path}`;
  const token = localStorage.getItem('visa_access_token');

  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const config = {
    method,
    headers,
  };

  if (options.body) {
    config.body = JSON.stringify(options.body);
  }

  const response = await fetch(url, config);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(errorData.detail || `Request failed: ${response.status}`);
  }

  return response.json();
}

// ── Auth ─────────────────────────────────────────────────────────────────

export async function login(email, password) {
  const data = await request('POST', '/auth/login', { body: { email, password } });
  if (data.token) {
    localStorage.setItem('visa_access_token', data.token);
  }
  return data;
}

export async function register(email, password, name, userType = 'applicant') {
  const data = await request('POST', '/auth/register', {
    body: { email, password, name, user_type: userType },
  });
  if (data.token) {
    localStorage.setItem('visa_access_token', data.token);
  }
  return data;
}

export async function logout() {
  localStorage.removeItem('visa_access_token');
}

export async function getCurrentUser() {
  return request('GET', '/auth/me');
}

// ── Applications ────────────────────────────────────────────────────────

export async function createApplication(applicationData) {
  return request('POST', '/applications', { body: applicationData });
}

export async function getApplications() {
  return request('GET', '/applications');
}

export async function getApplication(id) {
  return request('GET', `/applications/${id}`);
}

export async function updateApplication(id, data) {
  return request('PUT', `/applications/${id}`, { body: data });
}

export async function deleteApplication(id) {
  return request('DELETE', `/applications/${id}`);
}

// ── Documents ───────────────────────────────────────────────────────────

export async function uploadDocument(formData) {
  const token = localStorage.getItem('visa_access_token');
  const appId = formData.get('application_id');
  if (!appId) throw new Error('application_id is required in FormData');
  const url = `${API_BASE}/applications/${appId}/documents/upload`;
  const response = await fetch(url, {
    method: 'POST',
    headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    body: formData,
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(errorData.detail || 'Upload failed');
  }
  return response.json();
}

export async function getDocuments(applicationId = null) {
  if (!applicationId) throw new Error('applicationId is required');
  const data = await request('GET', `/applications/${applicationId}/documents`);
  return data.documents;
}

export async function getDocument(id) {
  return request('GET', `/documents/${id}`);
}

export async function deleteDocument(id) {
  return request('DELETE', `/documents/${id}`);
}

// ── Analysis ────────────────────────────────────────────────────────────

export async function runFullAnalysis(applicationId) {
  return request('POST', `/analyze/${applicationId}`);
}

export async function getAnalysisReport(applicationId) {
  return request('GET', `/analyze/${applicationId}`);
}

export async function runOcrOnDocument(docId) {
  return request('POST', `/analyze/${docId}/ocr`);
}

export async function getAvailableRequirements() {
  return request('GET', '/analyze/requirements');
}

export async function getRequirementsFor(country, visaType) {
  return request('GET', `/analyze/requirements/${country}/${visaType}`);
}

// ── Queries (User-to-Admin Q&A) ─────────────────────────────────────────

export async function createQuery(applicationId, message) {
  return request('POST', '/queries', { body: { application_id: applicationId, message } });
}

export async function getQueries(applicationId) {
  return request('GET', `/queries/${applicationId}`);
}

export async function replyToQuery(queryId, reply) {
  return request('PUT', `/queries/${queryId}`, { body: { reply } });
}

// ── Admin ───────────────────────────────────────────────────────────────

export async function adminListApplications() {
  return request('GET', '/admin/analyze/applications');
}

export async function adminReanalyze(applicationId) {
  return request('POST', `/admin/analyze/${applicationId}/reanalyze`);
}

export async function adminGetRequirements() {
  return request('GET', '/admin/requirements');
}

export async function adminUpsertRequirement(country, visaType, requirements) {
  return request('PUT', '/admin/requirements', { body: { country, visa_type: visaType, requirements } });
}

export async function adminDeleteRequirement(overrideId) {
  return request('DELETE', `/admin/requirements/${overrideId}`);
}

export async function adminListQueries(statusFilter) {
  const query = statusFilter ? `?status=${statusFilter}` : '';
  return request('GET', `/admin/queries${query}`);
}

export async function adminGetDemoData() {
  return request('GET', '/admin/demo-data');
}

export async function adminSeedDemoData() {
  return request('POST', '/admin/seed-demo');
}

// ── Health ──────────────────────────────────────────────────────────────

export async function healthCheck() {
  return request('GET', '/health');
}

export async function analysisHealth() {
  return request('GET', '/analyze/health');
}