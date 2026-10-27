// One central place for talking to the backend.
// Vite exposes variables starting with VITE_ through import.meta.env
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export async function apiRequest(path, options = {}) {
  const { headers, ...rest } = options;

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...rest,
    headers: {
      ...(rest.body ? { "Content-Type": "application/json" } : {}),
      ...(headers || {}),
    },
  });

  if (response.status === 204) return null; // 204 = success, no content

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    // Our backend always sends errors as { error: { status, type, message, details } }
    const error = new Error(data?.error?.message || `Request failed (status ${response.status})`);
    error.status = response.status;
    error.details = data?.error?.details;
    throw error;
  }

  return data;
}

export const checkHealth = () => apiRequest("/health");

export default API_BASE_URL;
