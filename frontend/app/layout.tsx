import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Journal AI Coach",
  description:
    "A long-term journaling app for personal growth, memory-aware analysis, and progress tracking."
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
