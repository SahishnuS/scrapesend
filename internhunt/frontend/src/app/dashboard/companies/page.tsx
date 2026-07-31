"use client";

import { Building2, Globe, Clock, Plus, Upload, Download, X, FileText } from "lucide-react";
import { useCompanies, useCreateCompany } from "@/lib/hooks";
import { timeAgo, capitalize } from "@/lib/utils";
import { useState, useRef } from "react";
import toast from "react-hot-toast";
import { useMutation, useQueryClient } from "@tanstack/react-query";

type AddMode = "form" | "csv";

export default function CompaniesPage() {
  const { data: companies = [], isLoading } = useCompanies();
  const createCompany = useCreateCompany();
  const queryClient = useQueryClient();

  const [showPanel, setShowPanel] = useState(false);
  const [addMode, setAddMode] = useState<AddMode>("form");

  // Form state
  const [name, setName] = useState("");
  const [careersUrl, setCareersUrl] = useState("");
  const [atsProvider, setAtsProvider] = useState("");

  // CSV state
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [csvResult, setCsvResult] = useState<null | {
    added: number;
    skipped_duplicates: number;
    errors: string[];
    added_companies: string[];
  }>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const bulkUpload = useMutation({
    mutationFn: async (file: File) => {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch("/api/v1/companies/bulk-upload", {
        method: "POST",
        body: form,
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Upload failed");
      }
      return res.json();
    },
    onSuccess: (data) => {
      setCsvResult(data);
      queryClient.invalidateQueries({ queryKey: ["companies"] });
      if (data.added > 0) toast.success(`Added ${data.added} companies!`);
      else toast("No new companies were added (all duplicates).");
    },
    onError: (err: Error) => {
      toast.error(err.message);
    },
  });

  const handleCreate = async () => {
    if (!name.trim()) return;
    try {
      await createCompany.mutateAsync({
        name: name.trim(),
        careers_url: careersUrl.trim() || null,
        ats_provider: atsProvider.trim() || null,
        is_active: true,
      });
      toast.success("Company added!");
      setName("");
      setCareersUrl("");
      setAtsProvider("");
      setShowPanel(false);
    } catch {
      toast.error("Failed to create company");
    }
  };

  const handleCsvUpload = () => {
    if (!csvFile) return;
    setCsvResult(null);
    bulkUpload.mutate(csvFile);
  };

  const handleDownloadTemplate = () => {
    window.open("/api/v1/companies/template/csv", "_blank");
  };

  return (
    <div className="animate-fade-in space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Companies</h1>
          <p className="mt-1 text-sm text-surface-200/70">
            {companies.length} companies being monitored for internship openings
          </p>
        </div>
        <button
          onClick={() => { setShowPanel(!showPanel); setCsvResult(null); }}
          className="btn-primary"
        >
          <Plus size={16} />
          Add Companies
        </button>
      </div>

      {/* Add Panel */}
      {showPanel && (
        <div className="card animate-slide-up p-5 space-y-4">
          {/* Tabs */}
          <div className="flex gap-1 rounded-lg bg-surface-700/50 p-1 w-fit">
            <button
              onClick={() => setAddMode("form")}
              className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${
                addMode === "form"
                  ? "bg-brand-500 text-white shadow-sm"
                  : "text-surface-200/60 hover:text-surface-200"
              }`}
            >
              Manual Entry
            </button>
            <button
              onClick={() => setAddMode("csv")}
              className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${
                addMode === "csv"
                  ? "bg-brand-500 text-white shadow-sm"
                  : "text-surface-200/60 hover:text-surface-200"
              }`}
            >
              CSV Upload
            </button>
          </div>

          {/* ── Manual Form ── */}
          {addMode === "form" && (
            <div className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-3">
                <div>
                  <label className="label">Company Name *</label>
                  <input
                    className="input"
                    placeholder="e.g. Niqo Robotics"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                  />
                </div>
                <div>
                  <label className="label">Careers URL</label>
                  <input
                    className="input"
                    placeholder="https://company.com/careers"
                    value={careersUrl}
                    onChange={(e) => setCareersUrl(e.target.value)}
                  />
                </div>
                <div>
                  <label className="label">ATS Provider</label>
                  <select
                    className="input"
                    value={atsProvider}
                    onChange={(e) => setAtsProvider(e.target.value)}
                  >
                    <option value="">Auto-detect / Other</option>
                    <option value="greenhouse">Greenhouse</option>
                    <option value="lever">Lever</option>
                    <option value="ashby">Ashby</option>
                    <option value="smartrecruiters">SmartRecruiters</option>
                    <option value="workable">Workable</option>
                    <option value="workday">Workday</option>
                  </select>
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleCreate}
                  className="btn-primary btn-sm"
                  disabled={createCompany.isPending || !name.trim()}
                >
                  {createCompany.isPending ? "Saving..." : "Save Company"}
                </button>
                <button onClick={() => setShowPanel(false)} className="btn-secondary btn-sm">
                  Cancel
                </button>
              </div>
            </div>
          )}

          {/* ── CSV Upload ── */}
          {addMode === "csv" && (
            <div className="space-y-4">
              {/* Format Guide */}
              <div className="rounded-lg border border-surface-600 bg-surface-700/30 p-4">
                <p className="text-xs font-semibold text-surface-200/70 mb-2">Required CSV format:</p>
                <code className="block text-xs text-brand-400 font-mono bg-surface-800 rounded p-2">
                  name,careers_url,ats_provider<br />
                  Ather Energy,https://atherenergy.com/careers,other<br />
                  GreyOrange,https://greyorange.com/careers,greenhouse<br />
                  Locus,https://locus.sh/careers,lever
                </code>
                <p className="text-xs text-surface-200/50 mt-2">
                  Only <code className="text-brand-400">name</code> is required.{" "}
                  <code className="text-brand-400">ats_provider</code> values:{" "}
                  greenhouse | lever | workable | ashby | smartrecruiters | workday | other
                </p>
                <button
                  onClick={handleDownloadTemplate}
                  className="btn-secondary btn-sm mt-3 gap-1"
                >
                  <Download size={13} />
                  Download Template
                </button>
              </div>

              {/* File Drop Zone */}
              <div
                onClick={() => fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
                  csvFile
                    ? "border-brand-500 bg-brand-500/5"
                    : "border-surface-600 hover:border-brand-500/50 hover:bg-surface-700/20"
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv"
                  className="hidden"
                  onChange={(e) => {
                    const f = e.target.files?.[0];
                    if (f) { setCsvFile(f); setCsvResult(null); }
                  }}
                />
                {csvFile ? (
                  <div className="flex items-center justify-center gap-3">
                    <FileText size={20} className="text-brand-400" />
                    <span className="text-sm font-medium text-surface-100">{csvFile.name}</span>
                    <button
                      onClick={(e) => { e.stopPropagation(); setCsvFile(null); setCsvResult(null); }}
                      className="text-surface-200/40 hover:text-red-400 transition-colors"
                    >
                      <X size={16} />
                    </button>
                  </div>
                ) : (
                  <div>
                    <Upload size={24} className="mx-auto text-surface-200/30 mb-2" />
                    <p className="text-sm text-surface-200/50">Click to select a <strong>.csv</strong> file</p>
                  </div>
                )}
              </div>

              {/* Upload Result */}
              {csvResult && (
                <div className="rounded-lg border border-surface-600 bg-surface-700/30 p-4 space-y-1 text-sm">
                  <p className="font-semibold text-surface-100">Upload complete</p>
                  <p className="text-success">✓ {csvResult.added} companies added</p>
                  {csvResult.skipped_duplicates > 0 && (
                    <p className="text-surface-200/50">~ {csvResult.skipped_duplicates} duplicates skipped</p>
                  )}
                  {csvResult.errors.map((e, i) => (
                    <p key={i} className="text-red-400 text-xs">{e}</p>
                  ))}
                </div>
              )}

              <div className="flex gap-2">
                <button
                  onClick={handleCsvUpload}
                  className="btn-primary btn-sm"
                  disabled={!csvFile || bulkUpload.isPending}
                >
                  {bulkUpload.isPending ? "Uploading..." : "Upload CSV"}
                </button>
                <button onClick={() => setShowPanel(false)} className="btn-secondary btn-sm">
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Company Grid */}
      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="skeleton h-36 rounded-xl" />
          ))}
        </div>
      ) : companies.length === 0 ? (
        <div className="card flex flex-col items-center justify-center py-20 text-center">
          <Building2 size={48} className="text-surface-200/20" />
          <p className="mt-4 text-surface-200/60">
            No companies added yet. Click &quot;Add Companies&quot; to start monitoring.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {companies.map((company) => (
            <div key={company.id} className="card-hover p-5">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-500/10 text-brand-400">
                    <Building2 size={18} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-surface-50">{company.name}</h3>
                    {company.ats_provider && (
                      <span className="badge-neutral text-[10px] mt-1">
                        {capitalize(company.ats_provider)}
                      </span>
                    )}
                  </div>
                </div>
                <div
                  className={`h-2.5 w-2.5 rounded-full ${
                    company.is_active ? "bg-success animate-pulse-slow" : "bg-surface-200/30"
                  }`}
                />
              </div>

              <div className="mt-4 space-y-1.5 text-xs text-surface-200/60">
                {company.careers_url && (
                  <div className="flex items-center gap-1.5">
                    <Globe size={12} />
                    <a
                      href={company.careers_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="truncate hover:text-brand-400 transition-colors"
                    >
                      {company.careers_url}
                    </a>
                  </div>
                )}
                <div className="flex items-center gap-1.5">
                  <Clock size={12} />
                  <span>
                    Last crawled: {company.last_crawled_at ? timeAgo(company.last_crawled_at) : "Never"}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
