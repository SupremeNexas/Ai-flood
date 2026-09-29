import React from "react";
import Navbar from "@/components/Navbar";
import UnetDiagram from "@/components/UnetDiagram";
import PreprocessingLoss from "@/components/PreprocessingLoss";
import Footer from "@/components/Footer";

export const metadata = {
  title: "U-Net Neural Architecture | AI Flood Detection",
  description: "PyTorch 4-stage contracting and expanding U-Net with GroupNorm (G=8) and skip connections.",
};

export default function ArchitecturePage() {
  return (
    <main className="min-h-screen flex flex-col bg-[#070b14] text-slate-100 pt-20">
      <Navbar />
      <UnetDiagram />
      <PreprocessingLoss />
      <Footer />
    </main>
  );
}
