/**
 * React Query hooks for all API endpoints.
 * Each resource has a list hook, a detail hook, and mutation hooks.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";

// ── Types ────────────────────────────────────────────────────────────────────

export interface Category {
  id: string;
  name: string;
  description: string | null;
}

export interface Company {
  id: string;
  name: string;
  careers_url: string | null;
  ats_provider: string | null;
  is_active: boolean;
  last_crawled_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Job {
  id: string;
  company_id: string;
  category_id: string | null;
  title: string;
  job_url: string;
  location: string | null;
  description: string | null;
  job_hash: string;
  status: string;
  discovered_at: string;
  created_at: string;
  updated_at: string;
}

export interface Resume {
  id: string;
  filename: string;
  file_path: string;
  extracted_text: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Application {
  id: string;
  job_id: string;
  resume_id: string;
  status: string;
  match_score: number | null;
  ats_score: number | null;
  ats_keywords_matched: Record<string, unknown> | null;
  applied_at: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface Notification {
  id: string;
  job_id: string | null;
  platform: string;
  message: string;
  is_sent: boolean;
  sent_at: string | null;
  created_at: string;
}

export interface Log {
  id: string;
  level: string;
  module: string;
  message: string;
  details: Record<string, unknown> | null;
  timestamp: string;
}

// ── Query Hooks ──────────────────────────────────────────────────────────────

export function useCategories() {
  return useQuery<Category[]>({
    queryKey: ["categories"],
    queryFn: () => apiClient.get("/categories/").then((r) => r.data),
  });
}

export function useCompanies() {
  return useQuery<Company[]>({
    queryKey: ["companies"],
    queryFn: () => apiClient.get("/companies/").then((r) => r.data),
  });
}

export function useJobs(params?: { status?: string; limit?: number }) {
  return useQuery<Job[]>({
    queryKey: ["jobs", params],
    queryFn: () => apiClient.get("/jobs/", { params }).then((r) => r.data),
  });
}

export function useResumes() {
  return useQuery<Resume[]>({
    queryKey: ["resumes"],
    queryFn: () => apiClient.get("/resumes/").then((r) => r.data),
  });
}

export function useApplications(params?: { status?: string }) {
  return useQuery<Application[]>({
    queryKey: ["applications", params],
    queryFn: () => apiClient.get("/applications/", { params }).then((r) => r.data),
  });
}

export function useNotifications() {
  return useQuery<Notification[]>({
    queryKey: ["notifications"],
    queryFn: () => apiClient.get("/notifications/").then((r) => r.data),
  });
}

export function useLogs(params?: { level?: string; limit?: number }) {
  return useQuery<Log[]>({
    queryKey: ["logs", params],
    queryFn: () => apiClient.get("/logs/", { params }).then((r) => r.data),
  });
}

// ── Mutation Hooks ───────────────────────────────────────────────────────────

export function useCreateCompany() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Company>) =>
      apiClient.post("/companies/", data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["companies"] }),
  });
}

export function useCreateJob() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Job>) =>
      apiClient.post("/jobs/", data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["jobs"] }),
  });
}

export function useUpdateApplication() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...data }: { id: string } & Partial<Application>) =>
      apiClient.patch(`/applications/${id}`, data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["applications"] }),
  });
}

export function useUpdateJob() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...data }: { id: string } & Partial<Job>) =>
      apiClient.patch(`/jobs/${id}`, data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["jobs"] }),
  });
}
