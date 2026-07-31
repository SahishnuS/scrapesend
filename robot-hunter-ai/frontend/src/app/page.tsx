import { redirect } from "next/navigation";

/**
 * Root page — redirects to the main dashboard.
 * The dashboard lives at /dashboard to keep routing clean.
 */
export default function RootPage() {
  redirect("/dashboard");
}
