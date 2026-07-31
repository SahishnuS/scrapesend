"use client";

import { Bell } from "lucide-react";
import { useNotifications } from "@/lib/hooks";
import { timeAgo, cn } from "@/lib/utils";

export default function NotificationsPage() {
  const { data: notifications = [], isLoading } = useNotifications();

  return (
    <div className="animate-fade-in space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Notifications</h1>
        <p className="mt-1 text-sm text-surface-200/70">All notification history</p>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="skeleton h-16 rounded-xl" />
          ))}
        </div>
      ) : notifications.length === 0 ? (
        <div className="card flex flex-col items-center justify-center py-20 text-center">
          <Bell size={48} className="text-surface-200/20" />
          <p className="mt-4 text-surface-200/60">No notifications sent yet.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {notifications.map((n) => (
            <div key={n.id} className="card-hover flex items-start gap-4 p-4">
              <div className={cn("mt-1 h-2.5 w-2.5 shrink-0 rounded-full", n.is_sent ? "bg-success" : "bg-warning animate-pulse")} />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-surface-100">{n.message}</p>
                <div className="mt-1.5 flex items-center gap-3 text-xs text-surface-200/50">
                  <span className="badge-neutral capitalize text-[10px]">{n.platform}</span>
                  <span>{n.is_sent ? "Sent" : "Pending"}</span>
                  <span>·</span>
                  <span>{timeAgo(n.created_at)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
