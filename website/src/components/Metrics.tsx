"use client";

import React from "react";
import { CORE_KPIS, AUX_STATS } from "@/data/projectData";
import { AlertCircle, CheckCircle2, Layers, ShieldCheck, Activity } from "lucide-react";

export default function Metrics() {
  return (
    <section id="overview" className="py-16 sm:py-20 border-t border-slate-800/80 bg-[#090e1a]/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-blue-950/80 border border-blue-800/50 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-3">
            <Activity className="w-3.5 h-3.5" />
            <span>Research Overview & Verified Benchmarks</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
            Audited System Performance
          </h2>
          <p className="text-slate-300 text-base leading-relaxed">
            All metrics represent the complete, un-truncated official Sen1Floods11 test partition (90 chips, 20.5M valid pixels) evaluated without data leakage or silent omissions.
          </p>
        </div>

        {/* 3 Overview Pillars */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {/* Problem */}
          <div className="glass-panel rounded-xl p-6 border-l-4 border-l-rose-500 glow-border-hover">
            <div className="flex items-center space-x-3 mb-3">
              <div className="p-2 rounded-lg bg-rose-950/60 text-rose-400 border border-rose-800/40">
                <AlertCircle className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-white">The Problem</h3>
            </div>
            <p className="text-sm text-slate-300 leading-relaxed">
              Catastrophic floods require rapid, all-weather surface water delineation. Optical satellites (Sentinel-2, Landsat) fail under heavy monsoon storms and cloud cover.
            </p>
          </div>

          {/* Approach */}
          <div className="glass-panel rounded-xl p-6 border-l-4 border-l-cyan-500 glow-border-hover">
            <div className="flex items-center space-x-3 mb-3">
              <div className="p-2 rounded-lg bg-cyan-950/60 text-cyan-400 border border-cyan-800/40">
                <Layers className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-white">Our Approach</h3>
            </div>
            <p className="text-sm text-slate-300 leading-relaxed">
              We leverage cloud-penetrating <strong>Sentinel-1 SAR</strong> microwave radar with a customized PyTorch <strong>U-Net</strong> using GroupNorm and hybrid BCE + Dice loss.
            </p>
          </div>

          {/* Output */}
          <div className="glass-panel rounded-xl p-6 border-l-4 border-l-emerald-500 glow-border-hover">
            <div className="flex items-center space-x-3 mb-3">
              <div className="p-2 rounded-lg bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-white">The Output</h3>
            </div>
            <p className="text-sm text-slate-300 leading-relaxed">
              Dense pixel-level <strong>Binary Flood Masks</strong>, continuous <strong>Flood Probability Maps</strong>, and rapid <strong>Nominal Flooded Area</strong> calculations.
            </p>
          </div>
        </div>

        {/* 4 Core Primary KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
          {CORE_KPIS.map((kpi, idx) => (
            <div
              key={idx}
              className="glass-panel rounded-xl p-6 relative overflow-hidden group glow-border-hover"
            >
              <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-cyan-500 to-blue-600 opacity-80" />
              <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">
                {kpi.label}
              </div>
              <div className="text-4xl font-extrabold text-white tracking-tight mb-2 group-hover:text-cyan-400 transition-colors">
                {kpi.value}
              </div>
              <div className="text-xs font-semibold text-cyan-400/90 mb-2">
                {kpi.subtext}
              </div>
              <p className="text-xs text-slate-400 leading-normal">
                {kpi.description}
              </p>
            </div>
          ))}
        </div>

        {/* 4 Auxiliary Benchmark Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {AUX_STATS.map((stat, idx) => (
            <div
              key={idx}
              className="glass-panel rounded-xl p-4 text-center border border-slate-800/80 hover:border-slate-700 transition-colors"
            >
              <div className="text-2xl font-bold text-slate-100">{stat.value}</div>
              <div className="text-xs font-semibold text-slate-300 mt-0.5">{stat.label}</div>
              <div className="text-[11px] text-cyan-400/80 mt-1 font-mono">{stat.subtext}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
