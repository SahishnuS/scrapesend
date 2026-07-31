"use client";

import { Briefcase, ExternalLink, MapPin, Calendar, X } from "lucide-react";
import { useJobs, useUpdateJob } from "@/lib/hooks";
import { timeAgo, statusBadgeClass, capitalize } from "@/lib/utils";
import { useState } from "react";
import toast from "react-hot-toast";

export default function JobsPage() {
  const [statusFilter, setStatusFilter] = useState<string>("");
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

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Jobs</h1>
          <p className="mt-1 text-sm text-surface-200/70">
            All discovered internship openings
          </p>
        </div>
        <div className="flex items-center gap-2">
          {["", "open", "closed"].map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={
                statusFilter === s
                  ? "btn-primary btn-sm"
                  : "btn-secondary btn-sm"
              }
            >
              {s === "" ? "All" : capitalize(s)}
            </button>
          ))}
        </div>
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
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {jobs.map((job) => (
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
