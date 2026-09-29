"use client";

import React from "react";
import { Sliders, ShieldCheck, Scale, ArrowRight, Info } from "lucide-react";

export default function PreprocessingLoss() {
  return (
    <section className="py-16 sm:py-20 bg-[#070b14] border-t border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-blue-950/80 border border-blue-800/50 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-3">
            <Scale className="w-3.5 h-3.5" />
            <span>Mathematical Foundations</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
            Radiometric Normalization & Masked Loss
          </h2>
          <p className="text-slate-300 text-base leading-relaxed">
            Rigorous mathematical transformations ensure calibrated radar inputs and prevent gradient corruption from unannotated satellite pixels.
          </p>
        </div>

        {/* 2 Big Visual Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Card 1: Radiometric Normalization */}
          <div className="glass-panel rounded-2xl p-6 sm:p-8 flex flex-col justify-between">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2.5 rounded-xl bg-cyan-950/80 text-cyan-400 border border-cyan-800/50">
                  <Sliders className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Radiometric Decibel Normalization</h3>
                  <p className="text-xs text-slate-400">Sentinel-1 SAR Backscatter Scaling</p>
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed mb-4">
                Raw radar backscatter ranges from approximately -35 dB (deep calm water) to +5 dB (dense urban/rough surfaces). Outliers are clipped and linearly normalized into [0.0, 1.0]:
              </p>

              {/* Formula Block */}
              <div className="p-4 rounded-xl bg-slate-950/90 border border-slate-800 text-cyan-300 font-mono text-xs mb-6 overflow-x-auto">
                <div>x_norm = (clip(σ°, -35.0, 5.0) - (-35.0)) / (5.0 - (-35.0))</div>
                <div className="text-[11px] text-slate-500 mt-1"># Clamped linear scaling into [0.0, 1.0] range</div>
              </div>

              {/* Visual Scale Flow */}
              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                  <span className="text-slate-400">Raw SAR (dB):</span>
                  <span className="font-mono text-cyan-400 font-bold">-35 dB (Smooth Water) ➔ +5 dB (Urban/Rock)</span>
                </div>
                <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                  <span className="text-slate-400">Normalized Float:</span>
                  <span className="font-mono text-emerald-400 font-bold">0.0 (Dark Specular) ➔ 1.0 (Bright Backscatter)</span>
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-800 text-[11px] text-slate-400 flex items-center space-x-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Protects neural weights against exploding gradients from radar speckle extremes.</span>
            </div>
          </div>

          {/* Card 2: Masked BCE + Dice Loss */}
          <div className="glass-panel rounded-2xl p-6 sm:p-8 flex flex-col justify-between">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2.5 rounded-xl bg-purple-950/80 text-purple-400 border border-purple-800/50">
                  <Scale className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Masked BCE + Dice Loss</h3>
                  <p className="text-xs text-slate-400">Handling Severe Imbalance & Invalid Pixels</p>
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed mb-4">
                Combining Binary Cross-Entropy with Dice Loss optimizes both global classification entropy and local foreground intersection, dynamically masking out invalid pixels:
              </p>

              {/* Formula Block */}
              <div className="p-4 rounded-xl bg-slate-950/90 border border-slate-800 text-purple-300 font-mono text-xs mb-6 overflow-x-auto">
                <div>L_total = 0.5 * L_BCE(logits_valid, target_valid) + 0.5 * L_Dice(probs_valid, target_valid)</div>
                <div className="text-[11px] text-slate-500 mt-1"># Mask: valid_pixels = (target != -1)</div>
              </div>

              {/* Tri-State Handling Grid */}
              <div className="grid grid-cols-3 gap-2 text-center text-xs">
                <div className="p-3 rounded-lg bg-amber-950/40 border border-amber-800/50">
                  <div className="font-bold text-amber-400 font-mono">-1 (Invalid)</div>
                  <div className="text-[10px] text-slate-400 mt-1">Ignored in Loss</div>
                </div>
                <div className="p-3 rounded-lg bg-slate-900 border border-slate-700">
                  <div className="font-bold text-slate-200 font-mono">0 (Land)</div>
                  <div className="text-[10px] text-slate-400 mt-1">Negative Class</div>
                </div>
                <div className="p-3 rounded-lg bg-cyan-950/40 border border-cyan-800/50">
                  <div className="font-bold text-cyan-400 font-mono">1 (Flood)</div>
                  <div className="text-[10px] text-cyan-300 mt-1">Positive Target</div>
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-800 text-[11px] text-slate-400 flex items-center space-x-2">
              <Info className="w-4 h-4 text-cyan-400 shrink-0" />
              <span>Ensures 0 backpropagation error is generated from unannotated satellite regions.</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
