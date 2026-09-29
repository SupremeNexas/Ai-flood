import React from "react";
import Navbar from "@/components/Navbar";
import TrainingCharts from "@/components/TrainingCharts";
import PreprocessingLoss from "@/components/PreprocessingLoss";
import Footer from "@/components/Footer";

export const metadata = {
  title: "Model Training & Loss Curves | AI Flood Detection",
  description: "AdamW optimization, cosine annealing learning rate, and BCE + Dice loss convergence.",
};

export default function TrainingPage() {
  return (
    <main className="min-h-screen flex flex-col bg-[#070b14] text-slate-100 pt-20">
      <Navbar />
      <TrainingCharts />
      <PreprocessingLoss />
      <Footer />
    </main>
  );
}
