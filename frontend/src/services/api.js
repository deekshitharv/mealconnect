// The only place that talks to the backend. Every page uses the `api` object below.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const TOKEN_KEY = "mealconnect_token";

// The token is kept in localStorage so a page refresh keeps you logged in.
export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (token) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

export class ApiError extends Error {
  constructor(message, status = 0, details = null) {
    super(message);
    this.status = status;
    this.details = details;
  }
}

export async function apiRequest(path, { method = "GET", body, auth = true } = {}) {
  const headers = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const token = tokenStore.get();
  if (auth && token) headers.Authorization = `Bearer ${token}`;

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError("Cannot reach the server. Check your connection and try again.");
  }

  if (response.status === 204) return null;
  const data = await response.json().catch(() => null);

  if (!response.ok) {
    // An expired token: tell the app to log the user out.
    if (response.status === 401 && auth && token) window.dispatchEvent(new Event("auth:expired"));
    const err = data?.error;
    let message = err?.message || `Request failed (status ${response.status})`;
    if (Array.isArray(err?.details) && err.details.length) {
      message = err.details.map((d) => (d.field ? `${d.field}: ${d.message}` : d.message)).join(". ");
    }
    throw new ApiError(message, response.status, err?.details || null);
  }
  return data;
}

// Builds "?a=1&b=2" and skips empty values.
function qs(params = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") query.set(key, value);
  });
  const text = query.toString();
  return text ? `?${text}` : "";
}

const json = (method, body) => ({ method, body });

export const api = {
  // auth
  register: (payload) => apiRequest("/api/v1/auth/register", { ...json("POST", payload), auth: false }),
  login: (email, password) =>
    apiRequest("/api/v1/auth/login", { ...json("POST", { email, password }), auth: false }),
  me: () => apiRequest("/api/v1/auth/me"),

  // public data
  getMeals: (params) => apiRequest(`/api/v1/meals${qs(params)}`, { auth: false }),
  getMeal: (id) => apiRequest(`/api/v1/meals/${id}`, { auth: false }),
  getCategories: () => apiRequest("/api/v1/categories", { auth: false }),
  getLocations: () => apiRequest("/api/v1/locations", { auth: false }),

  // provider
  createLocation: (payload) => apiRequest("/api/v1/locations", json("POST", payload)),
  createMeal: (payload) => apiRequest("/api/v1/meals", json("POST", payload)),
  updateMeal: (id, payload) => apiRequest(`/api/v1/meals/${id}`, json("PUT", payload)),
  deleteMeal: (id) => apiRequest(`/api/v1/meals/${id}`, { method: "DELETE" }),
  providerStats: () => apiRequest("/api/v1/provider/stats"),
  providerReservations: (params) => apiRequest(`/api/v1/reservations/provider${qs(params)}`),
  collectReservation: (id) => apiRequest(`/api/v1/reservations/${id}/collect`, { method: "PUT" }),

  // reservations
  reserve: (meal_id, quantity) => apiRequest("/api/v1/reservations", json("POST", { meal_id, quantity })),
  myReservations: (params) => apiRequest(`/api/v1/reservations/my${qs(params)}`),
  getReservation: (id) => apiRequest(`/api/v1/reservations/${id}`),
  cancelReservation: (id) => apiRequest(`/api/v1/reservations/${id}/cancel`, { method: "PUT" }),

  // admin
  adminStats: () => apiRequest("/api/v1/admin/stats"),
  adminUsers: (params) => apiRequest(`/api/v1/admin/users${qs(params)}`),
  adminDeleteUser: (id) => apiRequest(`/api/v1/admin/users/${id}`, { method: "DELETE" }),
};

export default API_BASE_URL;