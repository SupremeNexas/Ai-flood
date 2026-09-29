"use client";

import React from "react";
import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import Metrics from "@/components/Metrics";
import Pipeline from "@/components/Pipeline";
import DatasetSection from "@/components/DatasetSection";
import SarVisualization from "@/components/SarVisualization";
import UnetDiagram from "@/components/UnetDiagram";
import PreprocessingLoss from "@/components/PreprocessingLoss";
import TrainingCharts from "@/components/TrainingCharts";
import Evaluation from "@/components/Evaluation";
import PredictionGallery from "@/components/PredictionGallery";
import AreaEstimator from "@/components/AreaEstimator";
import DemoSection from "@/components/DemoSection";
import Limitations from "@/components/Limitations";
import TechStack from "@/components/TechStack";
import EngineeringQuality from "@/components/EngineeringQuality";
import Conclusion from "@/components/Conclusion";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col bg-[#070b14] text-slate-100 overflow-x-hidden">
      {/* Fixed Navigation Bar */}
      <Navbar />

      {/* 1. Hero Section */}
      <Hero />

      {/* 2. Research Overview & Metric Cards */}
      <Metrics />

      {/* 3. End-to-End Processing Pipeline */}
      <Pipeline />

      {/* 4. Sen1Floods11 Dataset Section */}
      <DatasetSection />

      {/* 5. Satellite SAR & Polarization Section */}
      <SarVisualization />

      {/* 6. U-Net Neural Network Architecture */}
      <UnetDiagram />

      {/* 7. Radiometric Normalization & Masked BCE + Dice Loss */}
      <PreprocessingLoss />

      {/* 8. Training Optimization & Loss Convergence */}
      <TrainingCharts />

      {/* 9. Evaluation & 20.5M Pixel Confusion Matrix */}
      <Evaluation />

      {/* 10. Qualitative Prediction Gallery (Good, Average, Difficult) */}
      <PredictionGallery />

      {/* 11. Flood Mapping & Nominal Flooded Area Quantification */}
      <AreaEstimator />

      {/* 12. Live Streamlit Demonstration Interface */}
      <DemoSection />

      {/* 13. Documented Physical & System Limitations */}
      <Limitations />

      {/* 14. Technology Stack */}
      <TechStack />

      {/* 15. Software Engineering Quality & Unit Tests */}
      <EngineeringQuality />

      {/* 16. Final Conclusion Banner */}
      <Conclusion />

      {/* 17. Research Footer */}
      <Footer />
    </main>
  );
}
