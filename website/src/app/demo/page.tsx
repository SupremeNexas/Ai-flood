import React from "react";
import Navbar from "@/components/Navbar";
import DemoSection from "@/components/DemoSection";
import Footer from "@/components/Footer";

export const metadata = {
  title: "Live Streamlit Demo | AI Flood Detection",
  description: "Connect to the interactive PyTorch U-Net inference application.",
};

export default function DemoPage() {
  return (
    <main className="min-h-screen flex flex-col bg-[#070b14] text-slate-100 pt-20">
      <Navbar />
      <DemoSection />
      <Footer />
    </main>
  );
}
