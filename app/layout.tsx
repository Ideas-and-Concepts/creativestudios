import type { Metadata, Viewport } from "next";
import "./globals.css";

const logoUrl = "https://raw.githubusercontent.com/Ideas-and-Concepts/creativestudios/main/assets/creative_studios.png";

export const metadata: Metadata = {
  title: "Creative Studios",
  description: "AEC Collaboration Platform",
  manifest: "/manifest.webmanifest",
  icons: {
    icon: logoUrl,
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
