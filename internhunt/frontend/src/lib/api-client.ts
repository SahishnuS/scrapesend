/**
 * Axios HTTP client pre-configured for the InternHunt backend.
 *
 * All API calls should use this client instance so:
 *  - The base URL is always correct
 *  - Auth headers can be added in one place
 *  - Error interceptors are consistently applied
 */

import axios from "axios";
import { env } from "@/lib/env";

export const apiClient = axios.create({
  baseURL: `${env.apiUrl}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30_000,
});

// ── Request interceptor ──────────────────────────────────────────────────────
apiClient.interceptors.request.use(
  (config) => {
    // Auth token injection will be added in the auth module
    return config;
  },
  (error) => Promise.reject(error),
);

// ── Response interceptor ─────────────────────────────────────────────────────
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const message =
        error.response.data?.detail ??
        error.response.data?.message ??
        `HTTP ${error.response.status}`;
      console.error("[API Error]", message);
    } else if (error.request) {
      console.error("[API Error] No response received — is the backend running?");
    } else {
      console.error("[API Error]", error.message);
    }
    return Promise.reject(error);
  },
);

export default apiClient;
