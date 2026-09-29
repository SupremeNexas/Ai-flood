"use client";

import React, { useState } from "react";
import { MapPin, Globe, AlertTriangle, ArrowRight, Gauge, Layers } from "lucide-react";

export default function AreaEstimator() {
  const [pixelInput, setPixelInput] = useState<number>(43959); // default from USA_905409

  // 10m x 10m nominal pixel = 100 m² = 0.0001 km²
  const nominalKm2 = (pixelInput * 100) / 1e6;
  const coveragePercent = Math.min(100, (pixelInput / (256 * 256)) * 100);

  return (
    <section className="py-16 sm:py-20 bg-[#070b14] border-t border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800/50 text-cyan-400 text-xs font-semibold uppercase tracking-wider mb-3">
            <Gauge className="w-3.5 h-3.5" />
            <span>Geospatial Quantification</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
            Flood Mapping & Nominal Area Estimation
          </h2>
          <p className="text-slate-300 text-base leading-relaxed">
            Translating neural pixel activations into rapid geospatial flood extent metrics with documented geographic resolution caveats.
          </p>
        </div>

        {/* 3 Step Area Flow */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          <div className="glass-panel rounded-xl p-6 text-center glow-border-hover">
            <div className="text-xs font-mono uppercase text-slate-400 mb-1">Step 1: AI Inundation Detection</div>
            <div className="text-2xl font-extrabold text-white my-1">Detected Flood Pixels</div>
            <div className="text-xs text-cyan-400 font-mono mt-2">Binary Mask Sum (p ≥ 0.50)</div>
          </div>

          <div className="glass-panel rounded-xl p-6 text-center glow-border-hover">
            <div className="text-xs font-mono uppercase text-slate-400 mb-1">Step 2: Scene Ratio</div>
            <div className="text-2xl font-extrabold text-white my-1">Flood Coverage %</div>
            <div className="text-xs text-blue-400 font-mono mt-2">Detected / Valid Valid Pixels</div>
          </div>

          <div className="glass-panel rounded-xl p-6 text-center border-2 border-cyan-500/50 glow-border-hover">
            <div className="text-xs font-mono uppercase text-cyan-400 font-bold mb-1">Step 3: Rapid Assessment</div>
            <div className="text-2xl font-extrabold text-cyan-300 my-1">NOMINAL FLOODED AREA</div>
            <div className="text-xs text-emerald-400 font-mono mt-2">Pixels × 100 m² (Nominal)</div>
          </div>
        </div>

        {/* Interactive Estimator Demonstration Box */}
        <div className="glass-panel-glow rounded-2xl p-6 sm:p-8 mb-8">
          <div className="flex items-center justify-between mb-6 flex-wrap gap-2">
            <h3 className="text-base font-bold text-white flex items-center space-x-2">
              <Layers className="w-4 h-4 text-cyan-400" />
              <span>Interactive Nominal Area Calculator (256×256 Scene)</span>
            </h3>
            <span className="text-xs font-mono text-cyan-400 bg-cyan-950/80 px-2.5 py-1 rounded-md border border-cyan-800/50">
              Simulation Sandbox
            </span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            {/* Input Slider (7 cols) */}
            <div className="lg:col-span-7 space-y-4">
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-300 font-medium">Simulated Positive Flood Pixels:</span>
                <span className="font-mono text-cyan-400 font-bold text-sm">{pixelInput.toLocaleString()} px</span>
              </div>
              <input
                type="range"
                min="0"
                max={256 * 256}
                step="500"
                value={pixelInput}
                onChange={(e) => setPixelInput(Number(e.target.value))}
                className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
              />
              <div className="flex justify-between text-[10px] font-mono text-slate-500">
                <span>0 px (0%)</span>
                <span>32,768 px (50%)</span>
                <span>65,536 px (100%)</span>
              </div>
            </div>

            {/* Metric Displays (5 cols) */}
            <div className="lg:col-span-5 grid grid-cols-2 gap-3">
              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
                <div className="text-[10px] uppercase text-slate-400 font-bold">Flood Coverage</div>
                <div className="text-2xl font-extrabold text-white my-1">{coveragePercent.toFixed(2)}%</div>
                <div className="text-[10px] text-slate-400">of 65,536 scene px</div>
              </div>

              <div className="p-4 rounded-xl bg-cyan-950/40 border border-cyan-800/60 text-center">
                <div className="text-[10px] uppercase text-cyan-400 font-bold">NOMINAL FLOODED AREA</div>
                <div className="text-2xl font-extrabold text-cyan-300 my-1">~{nominalKm2.toFixed(3)} km²</div>
                <div className="text-[10px] text-cyan-400/80">Nominal 10m Ground Scale</div>
              </div>
            </div>
          </div>
        </div>

        {/* Geospatial Latitude Variation Caveat */}
        <div className="p-4 sm:p-5 rounded-xl bg-amber-950/30 border border-amber-800/60 flex items-start space-x-3 text-xs">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div className="text-slate-300 leading-relaxed">
            <strong className="text-amber-300 font-semibold">Geospatial Caveat on Nominal Area:</strong> Sen1Floods11 rasters are projected in WGS84 (<code className="text-amber-200">EPSG:4326</code>). Physical ground pixel dimensions vary with latitude according to <code className="text-amber-200">10m × cos(latitude)</code>. Stated square kilometer values are documented nominal equatorial approximations (100 m²/pixel) intended for rapid visual damage assessment rather than exact physical surveying.
          </div>
        </div>
      </div>
    </section>
  );
}
