import React from "react";
import Navbar from "@/components/Navbar";
import PredictionGallery from "@/components/PredictionGallery";
import AreaEstimator from "@/components/AreaEstimator";
import Footer from "@/components/Footer";

export const metadata = {
  title: "Prediction Gallery & Case Studies | AI Flood Detection",
  description: "Visual analysis of good, average, and difficult prediction cases across global biomes.",
};

export default function PredictionsPage() {
  return (
    <main className="min-h-screen flex flex-col bg-[#070b14] text-slate-100 pt-20">
      <Navbar />
      <PredictionGallery />
      <AreaEstimator />
      <Footer />
    </main>
  );
}
