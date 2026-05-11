import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "IPO Trademark Dashboard",
  description: "Pakistan IPO Trademark Management Dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className="h-full antialiased"
    >
      <body className="min-h-full flex flex-col bg-background">{children}</body>
    </html>
  );
}
