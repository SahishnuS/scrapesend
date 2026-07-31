"use client";

import { Send, ArrowRight } from "lucide-react";
import { useApplications, useUpdateApplication } from "@/lib/hooks";
import { formatDate, statusBadgeClass, capitalize, cn } from "@/lib/utils";
import toast from "react-hot-toast";

const STAGES = ["matched", "applied", "interviewing", "offer", "rejected"] as const;

export default function ApplicationsPage() {
  const { data: applications = [], isLoading } = useApplications();
  const updateApp = useUpdateApplication();

  const handleStatusChange = async (id: string, newStatus: string) => {
    try {
      await updateApp.mutateAsync({ id, status: newStatus });
      toast.success(`Status updated to ${capitalize(newStatus)}`);
    } catch {
      toast.error("Failed to update status");
    }
  };

  const grouped = STAGES.map((stage) => ({
    stage,
    items: applications.filter((a) => a.status === stage),
  }));

  return (
    <div className="animate-fade-in space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Applications</h1>
        <p className="mt-1 text-sm text-surface-200/70">
          Track your application lifecycle
        </p>
      </div>

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-5">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="skeleton h-60 rounded-xl" />
          ))}
        </div>
      ) : applications.length === 0 ? (
        <div className="card flex flex-col items-center justify-center py-20 text-center">
          <Send size={48} className="text-surface-200/20" />
          <p className="mt-4 text-surface-200/60">
            No applications yet. When the AI matcher finds relevant jobs, they
            will appear here.
          </p>
        </div>
      ) : (
        /* Kanban Board */
        <div className="grid gap-4 md:grid-cols-5">
          {grouped.map(({ stage, items }) => (
            <div key={stage} className="space-y-3">
              <div className="flex items-center justify-between px-1">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-surface-200/70">
                  {capitalize(stage)}
                </h3>
                <span className="badge-neutral text-[10px]">{items.length}</span>
              </div>

              <div className="space-y-2">
                {items.map((app) => (
                  <div
                    key={app.id}
                    className="card-hover p-4 space-y-3"
                  >
                    {app.match_score !== null && (
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-surface-200/50">Match</span>
                        <span
                          className={cn(
                            "font-mono font-semibold",
                            app.match_score >= 0.7
                              ? "text-success"
                              : app.match_score >= 0.5
                              ? "text-warning"
                              : "text-surface-200/60"
                          )}
                        >
                          {(app.match_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    )}

                    {app.ats_score !== null && (
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-surface-200/50">ATS</span>
                        <span className="font-mono font-semibold text-brand-400">
                          {(app.ats_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    )}

                    <div className="text-xs text-surface-200/40">
                      {formatDate(app.applied_at ?? app.created_at)}
                    </div>

                    {app.notes && (
                      <p className="text-xs text-surface-200/50 line-clamp-2">
                        {app.notes}
                      </p>
                    )}

                    {/* Status actions */}
                    <div className="flex flex-wrap gap-1 pt-1">
                      {STAGES.filter((s) => s !== app.status).map((s) => (
                        <button
                          key={s}
                          onClick={() => handleStatusChange(app.id, s)}
                          className="btn-ghost text-[10px] px-1.5 py-0.5 rounded"
                          title={`Move to ${capitalize(s)}`}
                        >
                          <ArrowRight size={10} />
                          <span>{capitalize(s)}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
