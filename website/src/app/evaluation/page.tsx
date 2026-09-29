import React from "react";
import Navbar from "@/components/Navbar";
import Evaluation from "@/components/Evaluation";
import Metrics from "@/components/Metrics";
import Footer from "@/components/Footer";

export const metadata = {
  title: "90-Chip Evaluation & Confusion Matrix | AI Flood Detection",
  description: "Audited test benchmark results: IoU 0.5548, Dice 0.7137, 20.5M valid test pixels.",
};

export default function EvaluationPage() {
  return (
    <main className="min-h-screen flex flex-col bg-[#070b14] text-slate-100 pt-20">
      <Navbar />
      <Evaluation />
      <Metrics />
      <Footer />
    </main>
  );
}
