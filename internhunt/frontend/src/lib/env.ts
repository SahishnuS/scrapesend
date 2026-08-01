/**
 * Centralised frontend environment configuration.
 *
 * All env vars must be declared here — never access process.env directly
 * in components or hooks. NEXT_PUBLIC_ vars are safe for client bundles.
 */
export const env = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
} as const;
