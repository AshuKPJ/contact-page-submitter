// src/services/api.js
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api",
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

// Attach token to every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle 401s, but DON'T redirect for /auth/* endpoints
api.interceptors.response.use(
  (res) => res,
  (error) => {
    // If there is no response (network error), just bubble it up
    const status = error?.response?.status;
    const cfg = error?.config || {};

    if (status === 401) {
      let pathname = "";
      try {
        pathname = new URL(cfg.url, api.defaults.baseURL).pathname;
      } catch {
        pathname = String(cfg.url || "");
      }

      const isAuthEndpoint =
        pathname.endsWith("/auth/login") ||
        pathname.endsWith("/auth/register") ||
        pathname.endsWith("/auth/me");

      // ✅ Do NOT clear token/redirect for auth endpoints, only for protected API calls
      if (!isAuthEndpoint) {
        localStorage.removeItem("access_token");
        // Prefer SPA navigation; fall back to hard reload
        if (window?.location) window.location.href = "/";
      }
    }
    return Promise.reject(error);
  }
);

// ---- Convenience auth calls ----
export const login = (email, password) =>
  api.post("/auth/login", { email, password });

export const me = () => api.get("/auth/me");

export default api;
