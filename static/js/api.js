// static/js/api.js
// Anvil Breaker™ Unified API Client with Authenticated Bearer Tokens

async function apiFetch(url, options = {}) {
  const token = localStorage.getItem('anvil_token');
  const headers = Object.assign({}, options.headers || {});

  // Automatically attach Bearer session token
  if (token && !headers['Authorization']) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Set default JSON Content-Type for mutating requests
  if (options.body && typeof options.body === 'string' && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  try {
    const response = await fetch(url, Object.assign({}, options, { headers }));

    // Global 401 Unauthorized Session Handler
    if (response.status === 401) {
      console.warn("Session unauthenticated or expired (401). Preserving local workspace view.");
      localStorage.removeItem('anvil_token');
      localStorage.removeItem('anvil_user');
    }

    return response;
  } catch (err) {
    console.error(`Network error calling ${url}:`, err);
    throw err;
  }
}

// Global API helper methods
const AnvilAPI = {
  get: (url) => apiFetch(url, { method: 'GET' }),
  post: (url, body) => apiFetch(url, { method: 'POST', body: JSON.stringify(body) }),
  del: (url) => apiFetch(url, { method: 'DELETE' }),
  getToken: () => localStorage.getItem('anvil_token'),
  getUser: () => {
    try {
      return JSON.parse(localStorage.getItem('anvil_user') || 'null');
    } catch {
      return null;
    }
  },
  setSession: (token, user) => {
    localStorage.setItem('anvil_token', token);
    localStorage.setItem('anvil_user', JSON.stringify(user));
  },
  clearSession: () => {
    localStorage.removeItem('anvil_token');
    localStorage.removeItem('anvil_user');
  }
};

