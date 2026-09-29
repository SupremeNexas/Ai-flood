import React from "react";
import Navbar from "@/components/Navbar";
import DatasetSection from "@/components/DatasetSection";
import SarVisualization from "@/components/SarVisualization";
import Footer from "@/components/Footer";

export const metadata = {
  title: "Sen1Floods11 Dataset | AI Flood Detection",
  description: "Benchmark dataset details, splits, and Sentinel-1 SAR polarization analysis.",
};

export default function DatasetPage() {
  return (
    <main className="min-h-screen flex flex-col bg-[#070b14] text-slate-100 pt-20">
      <Navbar />
      <DatasetSection />
      <SarVisualization />
      <Footer />
    </main>
  );
}
