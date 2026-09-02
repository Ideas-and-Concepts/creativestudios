import type { Metadata, Viewport } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Creative Studios",
  description: "AEC Collaboration Platform",
  manifest: "/manifest.webmanifest",
  icons: {
    icon: "/assets/creative_studios.png",
    apple: "/assets/creative_studios.png",
  },
};

export const viewport: Viewport = {
  themeColor: "#05070B",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
