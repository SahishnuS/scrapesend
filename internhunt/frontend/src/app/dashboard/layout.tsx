import type { Metadata } from "next";
import "../globals.css";
import Providers from "../providers";
import Sidebar from "@/components/sidebar";

export const metadata: Metadata = {
  title: "Dashboard",
  description: "Overview of your internship monitoring activity",
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <Providers>
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="ml-[240px] flex-1 p-6 transition-all duration-300">
          {children}
        </main>
      </div>
    </Providers>
  );
}
