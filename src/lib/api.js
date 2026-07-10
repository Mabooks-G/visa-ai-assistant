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
  if (data.access_token) {
    localStorage.setItem('visa_access_token', data.access_token);
  }
  return data;
}

export async function register(email, password, name, userType = 'applicant') {
  const data = await request('POST', '/auth/register', {
    body: { email, password, name, user_type: userType },
  });
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
  const url = `${API_BASE}/documents/upload`;
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
  const path = applicationId ? `/documents?application_id=${applicationId}` : '/documents';
  return request('GET', path);
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

// ── Admin ───────────────────────────────────────────────────────────────

export async function adminListApplications() {
  return request('GET', '/admin/analyze/applications');
}

export async function adminReanalyze(applicationId) {
  return request('POST', `/admin/analyze/${applicationId}/reanalyze`);
}

// ── Health ──────────────────────────────────────────────────────────────

export async function healthCheck() {
  return request('GET', '/health');
}

export async function analysisHealth() {
  return request('GET', '/analyze/health');
}