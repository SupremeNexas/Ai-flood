import React from "react";
import Navbar from "@/components/Navbar";
import Limitations from "@/components/Limitations";
import TechStack from "@/components/TechStack";
import EngineeringQuality from "@/components/EngineeringQuality";
import Footer from "@/components/Footer";

export const metadata = {
  title: "About & Scientific Limitations | AI Flood Detection",
  description: "Academic prototype scope, radar physics, JRC water baseline, and engineering verification.",
};

export default function AboutPage() {
  return (
    <main className="min-h-screen flex flex-col bg-[#070b14] text-slate-100 pt-20">
      <Navbar />
      <Limitations />
      <TechStack />
      <EngineeringQuality />
      <Footer />
    </main>
  );
}
