"use client";

import React from "react";
import { VERIFIED_BENCHMARKS, CONFUSION_MATRIX } from "@/data/projectData";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  CartesianGrid,
} from "recharts";
import { Trophy, CheckCircle2, ShieldCheck, HelpCircle, BarChart3 } from "lucide-react";

export default function Evaluation() {
  const chartData = [
    { name: "Accuracy", value: 0.9334, color: "#3b82f6" },
    { name: "Precision", value: 0.7717, color: "#06b6d4" },
    { name: "Dice / F1", value: 0.7137, color: "#10b981" },
    { name: "Recall", value: 0.6637, color: "#8b5cf6" },
    { name: "IoU (Jaccard)", value: 0.5548, color: "#f59e0b" },
  ];

  return (
    <section id="evaluation" className="py-16 sm:py-20 bg-[#070b14] border-t border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-emerald-950/80 border border-emerald-800/50 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-3">
            <Trophy className="w-3.5 h-3.5" />
            <span>Official 90-Chip Benchmark Audit</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
            Test Evaluation & Confusion Matrix
          </h2>
          <p className="text-slate-300 text-base leading-relaxed">
            Evaluated on all 90 test chips containing <strong>20,517,367 valid ground-truth pixels</strong> across 11 global flood disaster scenes.
          </p>
        </div>

        {/* 5 Main Metric Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 mb-12">
          <div className="glass-panel rounded-xl p-5 border-t-2 border-t-amber-500 glow-border-hover">
            <div className="text-xs font-bold uppercase text-slate-400">Test IoU</div>
            <div className="text-3xl font-extrabold text-amber-400 my-1">0.5548</div>
            <div className="text-[11px] text-slate-400">Jaccard Index</div>
          </div>
          <div className="glass-panel rounded-xl p-5 border-t-2 border-t-emerald-500 glow-border-hover">
            <div className="text-xs font-bold uppercase text-slate-400">Dice / F1</div>
            <div className="text-3xl font-extrabold text-emerald-400 my-1">0.7137</div>
            <div className="text-[11px] text-slate-400">Harmonic Mean</div>
          </div>
          <div className="glass-panel rounded-xl p-5 border-t-2 border-t-cyan-500 glow-border-hover">
            <div className="text-xs font-bold uppercase text-slate-400">Precision</div>
            <div className="text-3xl font-extrabold text-cyan-400 my-1">0.7717</div>
            <div className="text-[11px] text-slate-400">Low False Alarms</div>
          </div>
          <div className="glass-panel rounded-xl p-5 border-t-2 border-t-purple-500 glow-border-hover">
            <div className="text-xs font-bold uppercase text-slate-400">Recall</div>
            <div className="text-3xl font-extrabold text-purple-400 my-1">0.6637</div>
            <div className="text-[11px] text-slate-400">Flood Detection Rate</div>
          </div>
          <div className="glass-panel rounded-xl p-5 border-t-2 border-t-blue-500 glow-border-hover col-span-2 sm:col-span-1">
            <div className="text-xs font-bold uppercase text-slate-400">Accuracy</div>
            <div className="text-3xl font-extrabold text-blue-400 my-1">0.9334</div>
            <div className="text-[11px] text-slate-400">Overall Pixel Match</div>
          </div>
        </div>

        {/* Middle Grid: Confusion Matrix & Metric Bar Chart */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-12">
          {/* 2x2 Confusion Matrix (7 cols) */}
          <div className="lg:col-span-7 glass-panel rounded-2xl p-6 sm:p-8">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-base font-bold text-white">Pixel-Level Confusion Matrix</h3>
                <p className="text-xs text-slate-400">Evaluated on 20,517,367 valid pixels</p>
              </div>
              <span className="text-xs font-mono text-cyan-400 bg-cyan-950/80 px-2.5 py-1 rounded-md border border-cyan-800/50">
                100% Test Split
              </span>
            </div>

            {/* Matrix Grid */}
            <div className="relative">
              <div className="text-center text-xs font-bold uppercase text-slate-400 mb-2 tracking-wider">
                Reference Ground Truth
              </div>

              <div className="flex items-stretch gap-3">
                <div className="w-8 flex items-center justify-center">
                  <span className="-rotate-90 text-xs font-bold uppercase text-slate-400 tracking-wider whitespace-nowrap">
                    Predicted AI
                  </span>
                </div>

                <div className="flex-1 grid grid-cols-2 gap-3">
                  {/* True Positives (TP) */}
                  <div className="p-4 rounded-xl bg-emerald-950/40 border-2 border-emerald-500/80 text-center">
                    <div className="text-xs font-mono uppercase text-emerald-400 font-bold">True Positives (TP)</div>
                    <div className="text-2xl font-extrabold text-emerald-300 my-1">1,703,186 px</div>
                    <div className="text-[11px] text-emerald-400/80">Correctly Detected Floodwater</div>
                  </div>

                  {/* False Positives (FP) */}
                  <div className="p-4 rounded-xl bg-rose-950/40 border-2 border-rose-500/80 text-center">
                    <div className="text-xs font-mono uppercase text-rose-400 font-bold">False Positives (FP)</div>
                    <div className="text-2xl font-extrabold text-rose-300 my-1">503,818 px</div>
                    <div className="text-[11px] text-rose-400/80">Dry Land Classified as Flood</div>
                  </div>

                  {/* False Negatives (FN) */}
                  <div className="p-4 rounded-xl bg-amber-950/40 border-2 border-amber-500/80 text-center">
                    <div className="text-xs font-mono uppercase text-amber-400 font-bold">False Negatives (FN)</div>
                    <div className="text-2xl font-extrabold text-amber-300 my-1">862,915 px</div>
                    <div className="text-[11px] text-amber-400/80">Missed Floodwater Pixels</div>
                  </div>

                  {/* True Negatives (TN) */}
                  <div className="p-4 rounded-xl bg-slate-900/80 border-2 border-slate-700 text-center">
                    <div className="text-xs font-mono uppercase text-slate-400 font-bold">True Negatives (TN)</div>
                    <div className="text-2xl font-extrabold text-slate-200 my-1">17,447,448 px</div>
                    <div className="text-[11px] text-slate-400">Correctly Identified Dry Land</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Metric Bar Chart (5 cols) */}
          <div className="lg:col-span-5 glass-panel rounded-2xl p-6 sm:p-8 flex flex-col justify-between">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <BarChart3 className="w-4 h-4 text-cyan-400" />
                <h3 className="text-base font-bold text-white">Metric Score Comparison</h3>
              </div>
              <div className="h-60 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                    <XAxis type="number" domain={[0, 1]} stroke="#64748b" tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
                    <YAxis type="category" dataKey="name" stroke="#94a3b8" width={90} tick={{ fontSize: 11 }} />
                    <Tooltip
                      formatter={(value: any) => [`${(Number(value) * 100).toFixed(2)}% (${value})`, "Score"]}
                      contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "8px" }}
                    />
                    <Bar dataKey="value" radius={[0, 6, 6, 0]}>
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="text-[11px] text-slate-400 border-t border-slate-800 pt-3">
              Standard benchmark metrics computed across all 20.5M valid test pixels without class weighting biases.
            </div>
          </div>
        </div>

        {/* "What Does This Mean?" Explainer */}
        <div className="glass-panel rounded-2xl p-6 sm:p-8">
          <div className="flex items-center space-x-2 text-cyan-400 font-bold text-sm mb-4">
            <HelpCircle className="w-4 h-4" />
            <span>Metric Interpretations for Project Viva</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 text-xs">
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="font-bold text-amber-400 mb-1">IoU = 0.5548</div>
              <p className="text-slate-300 leading-relaxed">
                Formula: TP / (TP + FP + FN). Strictly measures spatial intersection over union without giving credit for correctly identified background land.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="font-bold text-emerald-400 mb-1">Dice / F1 = 0.7137</div>
              <p className="text-slate-300 leading-relaxed">
                Formula: 2×TP / (2×TP + FP + FN). Harmonic mean of precision and recall. Balances false alarms and missed flood detections across diverse terrain.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="font-bold text-cyan-400 mb-1">Precision = 0.7717</div>
              <p className="text-slate-300 leading-relaxed">
                Formula: TP / (TP + FP). High precision indicates that when the model flags a region as flooded, it is genuinely inundated 77.17% of the time.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="font-bold text-purple-400 mb-1">Recall = 0.6637</div>
              <p className="text-slate-300 leading-relaxed">
                Formula: TP / (TP + FN). Captures two-thirds of all ground-truth floodwaters, with misses occurring primarily under dense forest canopies.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
