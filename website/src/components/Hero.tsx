"use client";

import React from "react";
import Image from "next/image";
import { PROJECT_METADATA } from "@/data/projectData";
import { ArrowRight, Play, Satellite, Cpu, ShieldCheck } from "lucide-react";

export default function Hero() {
  return (
    <section className="relative pt-32 pb-20 lg:pt-36 lg:pb-28 overflow-hidden">
      {/* Background Decorative Gradients & Grid */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-cyan-950/30 via-[#070b14] to-[#070b14] -z-10" />
      <div
        className="absolute inset-0 opacity-[0.03] -z-10"
        style={{
          backgroundImage: `radial-gradient(#38bdf8 1px, transparent 1px)`,
          backgroundSize: "32px 32px",
        }}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-12">
          {/* Badge */}
          <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-cyan-950/60 border border-cyan-800/60 text-cyan-400 text-xs font-semibold mb-6 shadow-sm shadow-cyan-950">
            <span className="flex h-2 w-2 rounded-full bg-cyan-400 animate-ping mr-1" />
            <span>Academic Minor Project • Sen1Floods11 Official Benchmark</span>
          </div>

          {/* Main Title */}
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white mb-5 leading-tight sm:leading-none">
            AI-Based <span className="text-gradient-cyan">Flood Detection</span>
            <br />
            and Mapping
          </h1>

          {/* Subtitle */}
          <div className="text-sm sm:text-base font-semibold text-cyan-300/90 tracking-wide uppercase mb-4 flex items-center justify-center space-x-2">
            <span>Satellite Imagery</span>
            <span>•</span>
            <span>Sentinel-1 SAR</span>
            <span>•</span>
            <span>PyTorch U-Net</span>
          </div>

          {/* Supporting Text */}
          <p className="text-base sm:text-lg text-slate-300 leading-relaxed max-w-2xl mx-auto mb-8">
            An AI-based semantic segmentation system for detecting and mapping flooded regions from all-weather satellite radar imagery across global benchmark events.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <a
              href="#overview"
              className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-6 py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold text-sm shadow-lg shadow-cyan-500/25 transition-all hover:scale-105"
            >
              <span>Explore the Project</span>
              <ArrowRight className="w-4 h-4" />
            </a>

            <a
              href={PROJECT_METADATA.streamlitUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-6 py-3.5 rounded-xl bg-slate-800/90 hover:bg-slate-700/90 border border-slate-700 text-slate-200 font-semibold text-sm transition-all hover:scale-105 hover:text-white"
            >
              <Play className="w-4 h-4 text-cyan-400 fill-cyan-400" />
              <span>View Live Demo</span>
            </a>
          </div>
        </div>

        {/* Hero Visual Showcase: Real Project Visualization Breakdown */}
        <div className="relative max-w-5xl mx-auto mt-6">
          <div className="glass-panel-glow rounded-2xl p-4 sm:p-6 lg:p-8">
            <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800 flex-wrap gap-2">
              <div className="flex items-center space-x-3">
                <div className="flex space-x-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-500/80" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                  <div className="w-3 h-3 rounded-full bg-green-500/80" />
                </div>
                <span className="text-xs font-mono text-slate-400">
                  Sentinel-1 SAR Radar Input ➔ U-Net Inundation Segmentation
                </span>
              </div>
              <div className="flex items-center space-x-2 text-xs text-cyan-400 font-mono bg-cyan-950/60 px-2.5 py-1 rounded-md border border-cyan-800/40">
                <span>USA_905409 • IoU: 0.9350</span>
              </div>
            </div>

            {/* Real Project Image Asset */}
            <div className="relative rounded-xl overflow-hidden bg-slate-950 border border-slate-800/80 aspect-[16/6] sm:aspect-[21/9]">
              <Image
                src="/images/final_test/1_good_prediction_USA_905409.png"
                alt="AI Flood Detection 5-Panel Showcase: SAR Input, Ground Truth, Predicted Flood, Prediction Overlay, Flood Probability Map"
                fill
                priority
                className="object-contain"
                sizes="(max-width: 1280px) 100vw, 1200px"
              />
            </div>

            {/* 3 Step Visual Legend */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-4 pt-4 border-t border-slate-800/80 text-xs">
              <div className="flex items-start space-x-2.5 p-2 rounded-lg bg-slate-900/50">
                <Satellite className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                <div>
                  <div className="font-semibold text-slate-200">1. Satellite SAR Input</div>
                  <div className="text-slate-400 text-[11px]">VV + VH dual-polarization penetrates rain & cloud cover</div>
                </div>
              </div>
              <div className="flex items-start space-x-2.5 p-2 rounded-lg bg-slate-900/50">
                <Cpu className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                <div>
                  <div className="font-semibold text-slate-200">2. PyTorch U-Net Inference</div>
                  <div className="text-slate-400 text-[11px]">7.76M parameters predict dense pixel probabilities</div>
                </div>
              </div>
              <div className="flex items-start space-x-2.5 p-2 rounded-lg bg-slate-900/50">
                <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <div>
                  <div className="font-semibold text-slate-200">3. Highlighted Flood Mask</div>
                  <div className="text-slate-400 text-[11px]">Clean binary overlay & nominal flooded area estimate</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
