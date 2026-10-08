const TOKEN_KEY = "uptimewatch-token";

export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (t) => localStorage.setItem(TOKEN_KEY, t);
export const clearToken = () => localStorage.removeItem(TOKEN_KEY);

let onUnauthorized = () => {};
export const setUnauthorizedHandler = (fn) => (onUnauthorized = fn);

async function request(path, { method = "GET", body } = {}) {
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

 const res = await fetch(`${import.meta.env.VITE_API_URL}/api${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    // A 401 on an authenticated call means the token expired
    if (res.status === 401 && token) onUnauthorized();
    const detail = Array.isArray(data.detail)
      ? data.detail.map((d) => d.msg.replace("Value error, ", "")).join(", ")
      : data.detail;
    throw new Error(detail || "Something went wrong");
  }
  return data;
}

export const api = {
  register: (email, password) => request("/auth/register", { method: "POST", body: { email, password } }),
  login: (email, password) => request("/auth/login", { method: "POST", body: { email, password } }),
  me: () => request("/auth/me"),
  listMonitors: () => request("/monitors"),
  createMonitor: (data) => request("/monitors", { method: "POST", body: data }),
  updateMonitor: (id, data) => request(`/monitors/${id}`, { method: "PATCH", body: data }),
  deleteMonitor: (id) => request(`/monitors/${id}`, { method: "DELETE" }),
  checkNow: (id) => request(`/monitors/${id}/check`, { method: "POST" }),
  results: (id, limit = 50) => request(`/monitors/${id}/results?limit=${limit}`),
};
