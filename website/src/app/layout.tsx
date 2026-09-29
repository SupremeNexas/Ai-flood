import type { Metadata } from "next";
import "./globals.css";
import { PROJECT_METADATA } from "@/data/projectData";

export const metadata: Metadata = {
  title: "AI-Based Flood Detection & Mapping | Sen1Floods11 PyTorch U-Net",
  description:
    "An AI-based semantic segmentation system for detecting and mapping flooded regions from Sentinel-1 SAR satellite imagery using a PyTorch U-Net architecture on the Sen1Floods11 benchmark.",
  keywords: [
    "Flood Detection",
    "Satellite Imagery",
    "Sentinel-1 SAR",
    "PyTorch U-Net",
    "Sen1Floods11",
    "Semantic Segmentation",
    "Remote Sensing",
    "Disaster Response",
  ],
  authors: [{ name: "AI Flood Detection Research Team" }],
  openGraph: {
    title: "AI-Based Flood Detection and Mapping Using Satellite Imagery",
    description: "Sen1Floods11 • Sentinel-1 SAR • PyTorch U-Net Benchmark Showcase",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark scroll-smooth">
      <body className="bg-[#070b14] text-slate-100 antialiased min-h-screen selection:bg-cyan-500/30 selection:text-cyan-200">
        {children}
      </body>
    </html>
  );
}
