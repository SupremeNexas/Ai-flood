"use client";

import React from "react";
import Image from "next/image";
import { DATASET_SPLITS, PIXEL_COMPOSITION } from "@/data/projectData";
import { Database, ShieldCheck, Info, Check, Globe } from "lucide-react";

export default function DatasetSection() {
  return (
    <section id="dataset" className="py-16 sm:py-20 bg-[#090e1a] border-t border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-indigo-950/80 border border-indigo-800/50 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-3">
            <Database className="w-3.5 h-3.5" />
            <span>Benchmark Data Foundation</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
            Sen1Floods11 Benchmark Dataset
          </h2>
          <p className="text-slate-300 text-base leading-relaxed">
            Curated by Cloud to Street and published at IEEE CVPRW 2020. Spanning 11 global flood events across 6 continents with hand-labeled reference ground truth.
          </p>
        </div>

        {/* Top Grid: Splits and Pixel Composition */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {/* 1. Dataset Splits */}
          <div className="glass-panel rounded-2xl p-6 sm:p-8">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-bold text-white">Split Distribution</h3>
                <p className="text-xs text-slate-400">446 total hand-labeled chips (1,784 GeoTIFF files)</p>
              </div>
              <div className="flex items-center space-x-1 text-xs text-emerald-400 bg-emerald-950/60 border border-emerald-800/40 px-2.5 py-1 rounded-full font-mono">
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>0 Overlap / No Leakage</span>
              </div>
            </div>

            {/* Split Bar */}
            <div className="h-6 w-full bg-slate-800 rounded-full overflow-hidden flex mb-6 shadow-inner">
              {DATASET_SPLITS.map((split) => (
                <div
                  key={split.name}
                  style={{ width: `${split.percentage}%`, backgroundColor: split.color }}
                  className="h-full relative group transition-all duration-300"
                  title={`${split.name}: ${split.chips} chips (${split.percentage}%)`}
                />
              ))}
            </div>

            {/* Split Items */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {DATASET_SPLITS.map((split) => (
                <div key={split.name} className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div className="flex items-center space-x-1.5 mb-1">
                    <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: split.color }} />
                    <span className="text-[11px] font-semibold text-slate-300">{split.name}</span>
                  </div>
                  <div className="text-xl font-extrabold text-white">{split.chips}</div>
                  <div className="text-[10px] text-slate-400">{split.percentage}% ({split.files} files)</div>
                </div>
              ))}
            </div>
          </div>

          {/* 2. Pixel Composition */}
          <div className="glass-panel rounded-2xl p-6 sm:p-8">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-bold text-white">Pixel Composition & Classes</h3>
                <p className="text-xs text-slate-400">Class imbalance ratio: 4.86 : 1 (Land to Water)</p>
              </div>
              <span className="text-xs font-mono text-cyan-400 bg-cyan-950/60 border border-cyan-800/40 px-2.5 py-1 rounded-full">
                Tri-State (-1, 0, 1)
              </span>
            </div>

            <div className="space-y-3.5">
              {PIXEL_COMPOSITION.map((item) => (
                <div key={item.label} className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
                    <div>
                      <div className="text-xs font-bold text-slate-200">{item.label}</div>
                      <div className="text-[11px] text-slate-400">{item.role}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs font-mono font-bold text-slate-200">{item.formatted}</div>
                    <div className="text-[10px] text-cyan-400 font-mono">{item.percentage}% of total</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Real Sample Visualization from Dataset */}
        <div className="glass-panel rounded-2xl p-6 sm:p-8 mb-10">
          <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
            <div>
              <h3 className="text-base font-bold text-white flex items-center space-x-2">
                <Globe className="w-4 h-4 text-cyan-400" />
                <span>Multi-Layer Benchmark Alignment (Ghana_103272)</span>
              </h3>
              <p className="text-xs text-slate-400">
                Multi-sensor GeoTIFF stacks in Sen1Floods11: SAR (VV, VH), Optical (RGB), JRC Baseline, and Hand-Labeled Target.
              </p>
            </div>
            <span className="text-[11px] font-mono text-slate-400 bg-slate-800/80 px-2.5 py-1 rounded-md">
              EPSG:4326 • 10m Pixel Scale
            </span>
          </div>

          <div className="relative rounded-xl overflow-hidden bg-slate-950 border border-slate-800/80 aspect-[16/7]">
            <Image
              src="/images/dataset_samples/Ghana_103272_verification.png"
              alt="Multi-Modal Satellite Layer Verification: SAR VV/VH, Optical RGB, JRC Baseline, and Ground Truth Mask"
              fill
              className="object-contain"
              sizes="(max-width: 1280px) 100vw, 1200px"
            />
          </div>
        </div>

        {/* 2 Critical Scientific Context Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="glass-panel rounded-xl p-6 border-l-4 border-l-cyan-500">
            <h4 className="text-sm font-bold text-white mb-2 flex items-center space-x-2">
              <Check className="w-4 h-4 text-cyan-400" />
              <span>Why Sentinel-1 SAR?</span>
            </h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              Synthetic Aperture Radar provides all-weather flood observation capabilities when optical satellites are blinded by storm clouds and precipitation. Smooth water specularly reflects radar microwaves away from the sensor, producing characteristically dark backscatter values.
            </p>
          </div>

          <div className="glass-panel rounded-xl p-6 border-l-4 border-l-amber-500">
            <h4 className="text-sm font-bold text-white mb-2 flex items-center space-x-2">
              <Info className="w-4 h-4 text-amber-400" />
              <span>Temporal Baseline Clarification</span>
            </h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              Sen1Floods11 does <strong>NOT</strong> contain separate pre-flood SAR acquisitions as files in this benchmark. Instead, the European Commission Joint Research Centre (JRC) 30-year Global Surface Water permanence layer is used as the historical reference baseline.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
