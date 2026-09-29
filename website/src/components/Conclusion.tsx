"use client";

import React from "react";
import { PROJECT_METADATA } from "@/data/projectData";
import { ArrowRight, Play, Satellite, Sparkles } from "lucide-react";

export default function Conclusion() {
  return (
    <section className="py-20 bg-[#090e1a] border-t border-slate-800/80 relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-cyan-950/20 via-transparent to-transparent -z-10" />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <div className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-full bg-cyan-950/80 border border-cyan-800/60 text-cyan-400 text-xs font-semibold uppercase tracking-wider mb-6">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Project Summary</span>
        </div>

        <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight mb-6">
          From Satellite Radar Imagery to a <br />
          <span className="text-gradient-cyan">Pixel-Level Flood Map</span>
        </h2>

        <p className="text-slate-300 text-base sm:text-lg leading-relaxed max-w-3xl mx-auto mb-10">
          This project proves that deep convolutional semantic segmentation with Group-Normalized U-Nets can reliably delineate surface inundations from all-weather Sentinel-1 Synthetic Aperture Radar data, providing rapid visual and spatial assessment across global flood events.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <a
            href={PROJECT_METADATA.streamlitUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-8 py-4 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold text-sm shadow-xl shadow-cyan-500/25 transition-all hover:scale-105"
          >
            <Play className="w-4 h-4 fill-white" />
            <span>Launch Live Streamlit Demo</span>
          </a>

          <a
            href="#overview"
            className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-8 py-4 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-700 text-slate-200 font-semibold text-sm transition-all hover:text-white"
          >
            <span>Back to Top</span>
            <ArrowRight className="w-4 h-4" />
          </a>
        </div>
      </div>
    </section>
  );
}
