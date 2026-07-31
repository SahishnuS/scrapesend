"use client";

import {
  Briefcase,
  Building2,
  Send,
  TrendingUp,
  Bell,
  Clock,
  ExternalLink,
  Zap,
} from "lucide-react";
import { useJobs, useCompanies, useApplications, useNotifications } from "@/lib/hooks";
import { formatDate, timeAgo, statusBadgeClass, capitalize, cn } from "@/lib/utils";

function StatCard({
  label,
  value,
  icon: Icon,
  accent,
  subtitle,
}: {
  label: string;
  value: string | number;
  icon: React.ElementType;
  accent: string;
  subtitle?: string;
}) {
  return (
    <div className="card group relative overflow-hidden p-5 transition-all duration-200 hover:border-white/[0.12]">
      {/* Glow accent */}
      <div
        className={cn(
          "absolute -right-4 -top-4 h-24 w-24 rounded-full blur-3xl opacity-20 transition-opacity group-hover:opacity-30",
          accent
        )}
      />
      <div className="relative flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-surface-200/70">
            {label}
          </p>
          <p className="mt-1 text-3xl font-bold tracking-tight">{value}</p>
          {subtitle && (
            <p className="mt-1 text-xs text-surface-200/60">{subtitle}</p>
          )}
        </div>
        <div className={cn("rounded-lg p-2", accent.replace("bg-", "bg-") + "/10")}>
          <Icon size={20} className={accent.replace("bg-", "text-")} />
        </div>
      </div>
    </div>
  );
}

function RecentJobsTable({ jobs }: { jobs: { id: string; title: string; location: string | null; discovered_at: string; status: string; job_url: string }[] }) {
  if (jobs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <Briefcase size={40} className="text-surface-200/30" />
        <p className="mt-3 text-sm text-surface-200/60">
          No jobs discovered yet. Start a crawl to populate this list.
        </p>
      </div>
    );
  }

  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>Title</th>
          <th>Location</th>
          <th>Discovered</th>
          <th>Status</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {jobs.slice(0, 8).map((job) => (
          <tr key={job.id}>
            <td className="font-medium">{job.title}</td>
            <td className="text-surface-200/70">{job.location ?? "Remote"}</td>
            <td className="text-surface-200/70">{timeAgo(job.discovered_at)}</td>
            <td>
              <span className={statusBadgeClass(job.status)}>
                {capitalize(job.status)}
              </span>
            </td>
            <td>
              <a
                href={job.job_url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-ghost btn-sm"
              >
                <ExternalLink size={14} />
              </a>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function ApplicationPipeline({ applications }: { applications: { id: string; status: string; match_score: number | null }[] }) {
  const stages = ["matched", "applied", "interviewing", "offer", "rejected"];
  const counts = stages.map((s) => ({
    stage: s,
    count: applications.filter((a) => a.status === s).length,
  }));
  const total = Math.max(applications.length, 1);

  return (
    <div className="space-y-3">
      {counts.map(({ stage, count }) => (
        <div key={stage} className="group">
          <div className="mb-1 flex items-center justify-between text-xs">
            <span className="font-medium text-surface-100">{capitalize(stage)}</span>
            <span className="text-surface-200/60">{count}</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-surface-700">
            <div
              className={cn(
                "h-full rounded-full transition-all duration-500",
                stage === "offer"
                  ? "bg-success"
                  : stage === "rejected"
                  ? "bg-danger"
                  : stage === "applied"
                  ? "bg-warning"
                  : "bg-brand-500"
              )}
              style={{ width: `${(count / total) * 100}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

function NotificationFeed({ notifications }: { notifications: { id: string; platform: string; message: string; is_sent: boolean; created_at: string }[] }) {
  if (notifications.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center">
        <Bell size={32} className="text-surface-200/30" />
        <p className="mt-2 text-sm text-surface-200/60">No notifications yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
      {notifications.slice(0, 10).map((n) => (
        <div
          key={n.id}
          className="flex items-start gap-3 rounded-lg p-3 transition-colors hover:bg-white/[0.02]"
        >
          <div
            className={cn(
              "mt-0.5 h-2 w-2 shrink-0 rounded-full",
              n.is_sent ? "bg-success" : "bg-warning animate-pulse"
            )}
          />
          <div className="flex-1 min-w-0">
            <p className="text-sm text-surface-100 truncate">{n.message}</p>
            <div className="mt-1 flex items-center gap-2 text-xs text-surface-200/50">
              <span className="capitalize">{n.platform}</span>
              <span>·</span>
              <span>{timeAgo(n.created_at)}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default function DashboardPage() {
  const { data: jobs = [], isLoading: jobsLoading } = useJobs({ limit: 20 });
  const { data: companies = [], isLoading: companiesLoading } = useCompanies();
  const { data: applications = [], isLoading: appsLoading } = useApplications();
  const { data: notifications = [] } = useNotifications();

  const todayJobs = jobs.filter((j) => {
    const d = new Date(j.discovered_at);
    const today = new Date();
    return d.toDateString() === today.toDateString();
  });

  const isLoading = jobsLoading || companiesLoading || appsLoading;

  return (
    <div className="animate-fade-in space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
          <p className="mt-1 text-sm text-surface-200/70">
            Your internship monitoring overview
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="dot-online" />
          <span className="text-xs text-surface-200/60">System Online</span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Companies"
          value={isLoading ? "—" : companies.length}
          icon={Building2}
          accent="bg-brand-500"
          subtitle={`${companies.filter((c) => c.is_active).length} active`}
        />
        <StatCard
          label="Jobs Found"
          value={isLoading ? "—" : jobs.length}
          icon={Briefcase}
          accent="bg-success"
          subtitle={`${jobs.filter((j) => j.status === "open").length} open`}
        />
        <StatCard
          label="New Today"
          value={isLoading ? "—" : todayJobs.length}
          icon={Zap}
          accent="bg-warning"
        />
        <StatCard
          label="Applications"
          value={isLoading ? "—" : applications.length}
          icon={Send}
          accent="bg-info"
          subtitle={`${applications.filter((a) => a.status === "offer").length} offers`}
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Recent Jobs — 2 cols */}
        <div className="card lg:col-span-2 overflow-hidden">
          <div className="flex items-center justify-between border-b border-white/[0.06] px-5 py-4">
            <h2 className="flex items-center gap-2 text-sm font-semibold">
              <Clock size={16} className="text-brand-400" />
              Recent Jobs
            </h2>
            <span className="text-xs text-surface-200/50">{jobs.length} total</span>
          </div>
          <div className="p-1">
            {isLoading ? (
              <div className="space-y-3 p-4">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="skeleton h-10 w-full rounded-lg" />
                ))}
              </div>
            ) : (
              <RecentJobsTable jobs={jobs} />
            )}
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Application Pipeline */}
          <div className="card overflow-hidden">
            <div className="flex items-center gap-2 border-b border-white/[0.06] px-5 py-4">
              <TrendingUp size={16} className="text-brand-400" />
              <h2 className="text-sm font-semibold">Application Pipeline</h2>
            </div>
            <div className="p-5">
              {isLoading ? (
                <div className="space-y-4">
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="skeleton h-6 w-full rounded" />
                  ))}
                </div>
              ) : (
                <ApplicationPipeline applications={applications} />
              )}
            </div>
          </div>

          {/* Notifications */}
          <div className="card overflow-hidden">
            <div className="flex items-center gap-2 border-b border-white/[0.06] px-5 py-4">
              <Bell size={16} className="text-brand-400" />
              <h2 className="text-sm font-semibold">Notifications</h2>
            </div>
            <div className="p-3">
              <NotificationFeed notifications={notifications} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
