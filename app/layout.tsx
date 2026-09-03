import type { Metadata, Viewport } from "next";

import AecNavigation from "@/components/AecNavigation";
import "./globals.css";
import "./shell-overrides.css";

export const metadata: Metadata = {
  title: "Creative Studios",
  description: "AEC Collaboration Platform",
  manifest: "/manifest.webmanifest",
  icons: {
    icon: "/assets/creative-studios.png",
    apple: "/assets/creative-studios.png",
  },
};

export const viewport: Viewport = {
  themeColor: "#2563EB",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <AecNavigation />
        {children}
      </body>
    </html>
  );
}
