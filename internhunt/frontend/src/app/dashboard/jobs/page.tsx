"use client";

import { Briefcase, ExternalLink, MapPin, Calendar, X, Search } from "lucide-react";
import { useJobs, useUpdateJob } from "@/lib/hooks";
import { timeAgo, statusBadgeClass, capitalize } from "@/lib/utils";
import { useState } from "react";
import toast from "react-hot-toast";

export default function JobsPage() {
  const [statusFilter, setStatusFilter] = useState<string>("open");
  const [search, setSearch] = useState("");
  const { data: jobs = [], isLoading } = useJobs(
    statusFilter ? { status: statusFilter } : undefined
  );
  const updateJob = useUpdateJob();

  const handleClose = async (id: string, title: string) => {
    try {
      await updateJob.mutateAsync({ id, status: "closed" });
      toast.success(`Closed: ${title}`);
    } catch {
      toast.error("Failed to close job");
    }
  };

  const filtered = jobs.filter((job) => {
    const q = search.toLowerCase();
    return (
      job.title.toLowerCase().includes(q) ||
      (job.location ?? "").toLowerCase().includes(q)
    );
  });

  return (
    <div className="animate-fade-in space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Jobs</h1>
          <p className="mt-1 text-sm text-surface-200/70">
            {search
              ? `${filtered.length} of ${jobs.length} jobs match "${search}"`
              : `${jobs.length} internship openings`}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {(["open", "closed", ""] as const).map((s) => (
            <button
              key={s}
              onClick={() => { setStatusFilter(s); setSearch(""); }}
              className={statusFilter === s ? "btn-primary btn-sm" : "btn-secondary btn-sm"}
            >
              {s === "" ? "All" : capitalize(s)}
            </button>
          ))}
        </div>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-200/40 pointer-events-none" />
        <input
          className="input pl-9 w-full sm:max-w-sm"
          placeholder="Search by title or location..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        {search && (
          <button
            onClick={() => setSearch("")}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-surface-200/40 hover:text-surface-200 transition-colors"
          >
            <X size={14} />
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="skeleton h-44 rounded-xl" />
          ))}
        </div>
      ) : jobs.length === 0 ? (
        <div className="card flex flex-col items-center justify-center py-20 text-center">
          <Briefcase size={48} className="text-surface-200/20" />
          <p className="mt-4 text-surface-200/60">
            No jobs found. Run the crawler to discover openings.
          </p>
        </div>
      ) : filtered.length === 0 ? (
        <div className="card flex flex-col items-center justify-center py-20 text-center">
          <Search size={40} className="text-surface-200/20" />
          <p className="mt-4 text-surface-200/60">
            No jobs found matching &quot;{search}&quot;
          </p>
          <button onClick={() => setSearch("")} className="btn-secondary btn-sm mt-4">
            Clear search
          </button>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filtered.map((job) => (
            <div key={job.id} className="card-hover group p-5">
              <div className="flex items-start justify-between">
                <h3 className="font-semibold text-surface-50 group-hover:text-brand-400 transition-colors line-clamp-2">
                  {job.title}
                </h3>
                <div className="flex gap-1">
                  <a
                    href={job.job_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="shrink-0 rounded-lg p-1.5 text-surface-200/40 transition-colors hover:bg-white/5 hover:text-brand-400"
                    title="Open in new tab"
                  >
                    <ExternalLink size={14} />
                  </a>
                  {job.status !== "closed" && (
                    <button
                      onClick={() => handleClose(job.id, job.title)}
                      className="shrink-0 rounded-lg p-1.5 text-surface-200/40 transition-colors hover:bg-white/5 hover:text-red-400"
                      title="Close job"
                    >
                      <X size={14} />
                    </button>
                  )}
                </div>
              </div>

              <div className="mt-3 space-y-2 text-xs text-surface-200/60">
                <div className="flex items-center gap-1.5">
                  <MapPin size={12} />
                  <span>{job.location ?? "Remote"}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Calendar size={12} />
                  <span>{timeAgo(job.discovered_at)}</span>
                </div>
              </div>

              {job.description && (
                <p className="mt-3 text-xs text-surface-200/50 line-clamp-2">
                  {job.description}
                </p>
              )}

              <div className="mt-4 flex items-center justify-between">
                <span className={statusBadgeClass(job.status)}>
                  {capitalize(job.status)}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
