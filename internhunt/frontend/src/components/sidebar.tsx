"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Briefcase,
  Building2,
  FileText,
  Send,
  Bell,
  ScrollText,
  Bot,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useState } from "react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/jobs", label: "Jobs", icon: Briefcase },
  { href: "/dashboard/companies", label: "Companies", icon: Building2 },
  { href: "/dashboard/applications", label: "Applications", icon: Send },
  { href: "/dashboard/resumes", label: "Resumes", icon: FileText },
  { href: "/dashboard/notifications", label: "Notifications", icon: Bell },
  { href: "/dashboard/logs", label: "System Logs", icon: ScrollText },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-40 flex h-screen flex-col border-r border-white/[0.06] bg-surface-900 transition-all duration-300",
        collapsed ? "w-[68px]" : "w-[240px]"
      )}
    >
      {/* Logo */}
      <div className="flex h-16 items-center gap-3 border-b border-white/[0.06] px-4">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-gradient-brand shadow-glow-brand">
          <Bot size={20} className="text-white" />
        </div>
        {!collapsed && (
          <span className="text-gradient-brand text-lg font-bold tracking-tight whitespace-nowrap">
            InternHunt
          </span>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
        {navItems.map((item) => {
          const isActive =
            item.href === "/dashboard"
              ? pathname === "/dashboard"
              : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150",
                isActive
                  ? "bg-brand-500/15 text-brand-400 shadow-sm"
                  : "text-surface-200 hover:bg-white/[0.04] hover:text-surface-50"
              )}
            >
              <item.icon
                size={18}
                className={cn(
                  "shrink-0 transition-colors",
                  isActive
                    ? "text-brand-400"
                    : "text-surface-200/60 group-hover:text-surface-100"
                )}
              />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Collapse toggle */}
      <div className="border-t border-white/[0.06] p-3">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="btn-ghost w-full justify-center"
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>
    </aside>
  );
}
