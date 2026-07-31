import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "InternHunt — Internship Monitor",
    template: "%s | InternHunt",
  },
  description:
    "AI-powered internship monitoring and application management platform for Robotics, AI, Embedded Systems, Computer Vision, and more.",
  keywords: [
    "internship",
    "robotics",
    "AI",
    "job monitoring",
    "application tracker",
    "resume matching",
  ],
  authors: [{ name: "InternHunt" }],
  robots: "noindex, nofollow", // Private dashboard — do not index
};

export const viewport: Viewport = {
  themeColor: "#0a0f1e",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="antialiased">{children}</body>
    </html>
  );
}
