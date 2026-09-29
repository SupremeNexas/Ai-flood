"use client";

import React, { useState } from "react";
import Image from "next/image";
import { PREDICTION_CASES, PredictionCase } from "@/data/projectData";
import { Eye, CheckCircle2, AlertTriangle, ShieldAlert, Sparkles, MapPin } from "lucide-react";

export default function PredictionGallery() {
  const [selectedCase, setSelectedCase] = useState<PredictionCase>(PREDICTION_CASES[0]);

  const getCategoryBadge = (category: string) => {
    switch (category) {
      case "Good Prediction":
        return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-800/50 flex items-center space-x-1"><CheckCircle2 className="w-3.5 h-3.5 mr-1" />Good Prediction</span>;
      case "Average Prediction":
        return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-950/80 text-blue-400 border border-blue-800/50 flex items-center space-x-1"><Sparkles className="w-3.5 h-3.5 mr-1" />Average Prediction</span>;
      case "Difficult Challenge":
        return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-950/80 text-rose-400 border border-rose-800/50 flex items-center space-x-1"><AlertTriangle className="w-3.5 h-3.5 mr-1" />Difficult Challenge</span>;
      default:
        return null;
    }
  };

  return (
    <section id="predictions" className="py-16 sm:py-20 bg-[#090e1a] border-t border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800/50 text-cyan-400 text-xs font-semibold uppercase tracking-wider mb-3">
            <Eye className="w-3.5 h-3.5" />
            <span>Qualitative Visual Assessment</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
            Representative Prediction Gallery
          </h2>
          <p className="text-slate-300 text-base leading-relaxed">
            A transparent evaluation of high-performance, average, and edge-case challenge scenes illustrating radar specular reflection and vegetation canopy double-bounce scattering.
          </p>
        </div>

        {/* Case Selection Tabs */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
          {PREDICTION_CASES.map((item) => (
            <button
              key={item.id}
              onClick={() => setSelectedCase(item)}
              className={`text-left p-5 rounded-xl border transition-all ${
                selectedCase.id === item.id
                  ? "bg-slate-900 border-cyan-400 shadow-lg shadow-cyan-500/10"
                  : "glass-panel hover:border-slate-700"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono font-bold text-slate-300">{item.stem}</span>
                {getCategoryBadge(item.category)}
              </div>
              <div className="text-sm font-bold text-white mb-1">{item.event}</div>
              <div className="text-xs font-mono text-cyan-400">
                IoU: {item.iou.toFixed(4)} • Dice: {item.dice.toFixed(4)}
              </div>
            </button>
          ))}
        </div>

        {/* Selected Case Showcase Card */}
        <div className="glass-panel-glow rounded-2xl p-6 sm:p-8">
          {/* Top Case Title & Metrics Bar */}
          <div className="flex items-center justify-between pb-6 mb-6 border-b border-slate-800 flex-wrap gap-4">
            <div>
              <div className="flex items-center space-x-2 mb-1">
                <MapPin className="w-4 h-4 text-cyan-400" />
                <h3 className="text-lg font-bold text-white">{selectedCase.title} ({selectedCase.stem})</h3>
              </div>
              <p className="text-xs text-slate-400">{selectedCase.region} • {selectedCase.event}</p>
            </div>

            <div className="flex items-center space-x-3 flex-wrap gap-2 text-xs font-mono">
              <div className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-300">
                <span className="text-slate-400">IoU: </span>
                <span className="font-bold text-amber-400">{selectedCase.iou.toFixed(4)}</span>
              </div>
              <div className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-300">
                <span className="text-slate-400">Dice: </span>
                <span className="font-bold text-emerald-400">{selectedCase.dice.toFixed(4)}</span>
              </div>
              <div className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-300">
                <span className="text-slate-400">Precision: </span>
                <span className="font-bold text-cyan-400">{selectedCase.precision.toFixed(4)}</span>
              </div>
              <div className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-300">
                <span className="text-slate-400">Recall: </span>
                <span className="font-bold text-purple-400">{selectedCase.recall.toFixed(4)}</span>
              </div>
            </div>
          </div>

          {/* 5-Panel High-Resolution Prediction Image */}
          <div className="relative rounded-xl overflow-hidden bg-slate-950 border border-slate-800 aspect-[16/7] mb-6">
            <Image
              src={selectedCase.imagePath}
              alt={`${selectedCase.title}: Diagnostic 5-panel output`}
              fill
              className="object-contain"
              sizes="(max-width: 1280px) 100vw, 1200px"
            />
          </div>

          {/* Bottom Grid: Area Stats & Physical Radar Analysis */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pt-4 border-t border-slate-800/80">
            {/* Area & Pixel Quantification */}
            <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800">
              <h4 className="text-xs font-bold uppercase text-slate-300 mb-3 tracking-wider">
                Pixel & Nominal Extent Quantification
              </h4>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                  <div className="text-slate-400 text-[11px]">AI Detected Pixels:</div>
                  <div className="text-sm font-mono font-bold text-cyan-400">{selectedCase.predWaterPixels.toLocaleString()} px</div>
                  <div className="text-[10px] text-slate-400">Nominal: ~{selectedCase.nominalAreaKm2.toFixed(3)} km²</div>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                  <div className="text-slate-400 text-[11px]">Ground Truth Pixels:</div>
                  <div className="text-sm font-mono font-bold text-slate-200">{selectedCase.gtWaterPixels.toLocaleString()} px</div>
                  <div className="text-[10px] text-slate-400">Reference: ~{selectedCase.gtAreaKm2.toFixed(3)} km²</div>
                </div>
              </div>
              <ul className="mt-3 space-y-1 text-xs text-slate-300 list-disc list-inside">
                {selectedCase.highlights.map((h, idx) => (
                  <li key={idx}>{h}</li>
                ))}
              </ul>
            </div>

            {/* Scientific Radar Physics Explanation */}
            <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 flex flex-col justify-between">
              <div>
                <h4 className="text-xs font-bold uppercase text-slate-300 mb-2 tracking-wider">
                  Physical Radar Interaction Analysis
                </h4>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {selectedCase.physicsExplanation}
                </p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80 text-[11px] text-cyan-400/90 font-mono">
                5 Panels: [Input SAR] [Ground Truth] [Predicted Mask] [Overlay] [Probability Map]
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
