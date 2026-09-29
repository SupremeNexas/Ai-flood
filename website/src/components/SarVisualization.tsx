"use client";

import React, { useState } from "react";
import Image from "next/image";
import { Radio, Eye, Layers, Compass, Sliders, Info } from "lucide-react";

export default function SarVisualization() {
  const [activeTab, setActiveTab] = useState<"composite" | "vv" | "vh">("composite");

  return (
    <section id="sar" className="py-16 sm:py-20 bg-[#070b14] relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800/50 text-cyan-400 text-xs font-semibold uppercase tracking-wider mb-3">
            <Radio className="w-3.5 h-3.5" />
            <span>Microwave Radar Physics</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
            Sentinel-1 SAR Polarization Channels
          </h2>
          <p className="text-slate-300 text-base leading-relaxed">
            Sentinel-1 operates in C-band (5.405 GHz). By measuring both co-polarization (VV) and cross-polarization (VH), the neural network decouples surface roughness from volume vegetation texture.
          </p>
        </div>

        {/* 3 Channel Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          {/* VV */}
          <div
            onClick={() => setActiveTab("vv")}
            className={`glass-panel rounded-2xl p-6 cursor-pointer transition-all ${
              activeTab === "vv" ? "border-cyan-400 shadow-lg shadow-cyan-500/10" : "hover:border-slate-700"
            }`}
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono font-bold text-cyan-400 bg-cyan-950/80 px-2.5 py-1 rounded-md border border-cyan-800/50">
                Channel 0 (VV)
              </span>
              <span className="text-[11px] text-slate-400">Co-Polarization</span>
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Vertical Transmit / Vertical Receive</h3>
            <p className="text-xs text-slate-300 leading-relaxed mb-4">
              Dominant surface scattering mode. Calibrated decibel range [-35 dB, +5 dB]. Extremely sensitive to smooth open water specular reflections which appear dark.
            </p>
            <div className="text-[11px] font-mono text-cyan-300">σ°_vv &lt; -18 dB ➔ Standing Water</div>
          </div>

          {/* VH */}
          <div
            onClick={() => setActiveTab("vh")}
            className={`glass-panel rounded-2xl p-6 cursor-pointer transition-all ${
              activeTab === "vh" ? "border-cyan-400 shadow-lg shadow-cyan-500/10" : "hover:border-slate-700"
            }`}
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono font-bold text-blue-400 bg-blue-950/80 px-2.5 py-1 rounded-md border border-blue-800/50">
                Channel 1 (VH)
              </span>
              <span className="text-[11px] text-slate-400">Cross-Polarization</span>
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Vertical Transmit / Horizontal Receive</h3>
            <p className="text-xs text-slate-300 leading-relaxed mb-4">
              Sensitive to volume scattering from vegetation canopies, urban structures, and surface roughness. Depolarized radar signals help prevent false alarms in dry soils.
            </p>
            <div className="text-[11px] font-mono text-blue-300">Volume Scattering & Canopy Texture</div>
          </div>

          {/* Ratio / Composite */}
          <div
            onClick={() => setActiveTab("composite")}
            className={`glass-panel rounded-2xl p-6 cursor-pointer transition-all ${
              activeTab === "composite" ? "border-cyan-400 shadow-lg shadow-cyan-500/10" : "hover:border-slate-700"
            }`}
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono font-bold text-teal-400 bg-teal-950/80 px-2.5 py-1 rounded-md border border-teal-800/50">
                SAR Composite
              </span>
              <span className="text-[11px] text-slate-400">R=VV, G=VH, B=VV/VH</span>
            </div>
            <h3 className="text-lg font-bold text-white mb-2">False-Color RGB Radar Composite</h3>
            <p className="text-xs text-slate-300 leading-relaxed mb-4">
              Combines both channels into an intuitive diagnostic image: Red is VV backscatter, Green is VH, and Blue represents the polarization ratio VV / (VH + ε).
            </p>
            <div className="text-[11px] font-mono text-teal-300">Normalized [0, 1] 3-Band View</div>
          </div>
        </div>

        {/* Visual Inspection Panel */}
        <div className="glass-panel-glow rounded-2xl p-6 sm:p-8">
          <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
            <div>
              <h3 className="text-base font-bold text-white flex items-center space-x-2">
                <Layers className="w-4 h-4 text-cyan-400" />
                <span>Multi-Spectral & Radar Verification Comparison (Ghana_1078550)</span>
              </h3>
              <p className="text-xs text-slate-400">
                Direct benchmark verification illustrating how dual-polarization SAR maps to flood labels.
              </p>
            </div>
            <div className="flex space-x-2">
              <span className="text-xs font-mono text-cyan-400 bg-cyan-950/80 px-3 py-1 rounded-lg border border-cyan-800/50">
                Active: {activeTab.toUpperCase()}
              </span>
            </div>
          </div>

          <div className="relative rounded-xl overflow-hidden bg-slate-950 border border-slate-800 aspect-[16/7]">
            <Image
              src="/images/dataset_samples/Ghana_1078550_verification.png"
              alt="Sentinel-1 SAR Radar Channel Breakdown and Ground Truth Alignment"
              fill
              className="object-contain"
              sizes="(max-width: 1280px) 100vw, 1200px"
            />
          </div>

          <div className="mt-4 p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-xs text-slate-300 flex items-start space-x-2">
            <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
            <div>
              <strong>Physics Note:</strong> VV and VH represent complementary microwave backscatter behaviors. Calm water appears dark in both, while wet soil retains moderate VH volume scattering, enabling the U-Net to differentiate shallow floodwater from saturated agricultural fields.
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
