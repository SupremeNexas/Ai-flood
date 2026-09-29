"use client";

import React, { useState } from "react";
import Image from "next/image";
import { TRAINING_CONFIG, TRAINING_HISTORY } from "@/data/projectData";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from "recharts";
import { Activity, Sliders, TrendingDown, TrendingUp, CheckCircle } from "lucide-react";

export default function TrainingCharts() {
  const [viewMode, setViewMode] = useState<"interactive" | "artifacts">("interactive");

  return (
    <section id="training" className="py-16 sm:py-20 bg-[#090e1a] border-t border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800/50 text-cyan-400 text-xs font-semibold uppercase tracking-wider mb-3">
            <Activity className="w-3.5 h-3.5" />
            <span>Optimization Dynamics</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
            Model Training & Convergence
          </h2>
          <p className="text-slate-300 text-base leading-relaxed">
            Trained on the official 252-chip Sen1Floods11 training split with AdamW optimizer, cosine learning rate annealing, and early stopping.
          </p>
        </div>

        {/* Hyperparameter Config Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3 mb-10 text-center">
          <div className="glass-panel p-3.5 rounded-xl">
            <div className="text-[10px] text-slate-400 uppercase font-mono">Epochs</div>
            <div className="text-lg font-bold text-white">{TRAINING_CONFIG.epochs}</div>
          </div>
          <div className="glass-panel p-3.5 rounded-xl">
            <div className="text-[10px] text-slate-400 uppercase font-mono">Batch Size</div>
            <div className="text-lg font-bold text-white">{TRAINING_CONFIG.batchSize}</div>
          </div>
          <div className="glass-panel p-3.5 rounded-xl">
            <div className="text-[10px] text-slate-400 uppercase font-mono">Image Dim</div>
            <div className="text-sm font-bold text-white mt-1">{TRAINING_CONFIG.imageDimension}</div>
          </div>
          <div className="glass-panel p-3.5 rounded-xl">
            <div className="text-[10px] text-slate-400 uppercase font-mono">Optimizer</div>
            <div className="text-sm font-bold text-cyan-400 mt-1">AdamW</div>
          </div>
          <div className="glass-panel p-3.5 rounded-xl">
            <div className="text-[10px] text-slate-400 uppercase font-mono">Learning Rate</div>
            <div className="text-sm font-bold text-white mt-1">{TRAINING_CONFIG.learningRate}</div>
          </div>
          <div className="glass-panel p-3.5 rounded-xl">
            <div className="text-[10px] text-slate-400 uppercase font-mono">Scheduler</div>
            <div className="text-xs font-bold text-blue-400 mt-1">Cosine</div>
          </div>
          <div className="glass-panel p-3.5 rounded-xl">
            <div className="text-[10px] text-slate-400 uppercase font-mono">Best Val IoU</div>
            <div className="text-lg font-bold text-emerald-400">{TRAINING_CONFIG.bestValIoU}</div>
          </div>
          <div className="glass-panel p-3.5 rounded-xl">
            <div className="text-[10px] text-slate-400 uppercase font-mono">Best Val Dice</div>
            <div className="text-lg font-bold text-cyan-400">{TRAINING_CONFIG.bestValDice}</div>
          </div>
        </div>

        {/* View Toggle */}
        <div className="flex justify-center mb-8">
          <div className="p-1 bg-slate-900/90 rounded-xl border border-slate-800 flex space-x-1 text-xs">
            <button
              onClick={() => setViewMode("interactive")}
              className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                viewMode === "interactive"
                  ? "bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Interactive Convergence Curves
            </button>
            <button
              onClick={() => setViewMode("artifacts")}
              className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                viewMode === "artifacts"
                  ? "bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Official Saved Artifact Plots
            </button>
          </div>
        </div>

        {/* Chart View */}
        {viewMode === "interactive" ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Loss Convergence */}
            <div className="glass-panel rounded-2xl p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <TrendingDown className="w-4 h-4 text-cyan-400" />
                  <h3 className="text-sm font-bold text-white">Loss Convergence (BCE + Dice)</h3>
                </div>
                <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/80 px-2 py-0.5 rounded">
                  Epoch 1 ➔ 5
                </span>
              </div>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={TRAINING_HISTORY}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="epoch" stroke="#64748b" tickFormatter={(v) => `Ep ${v}`} />
                    <YAxis stroke="#64748b" domain={[0.3, 0.65]} />
                    <Tooltip
                      contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "8px" }}
                      labelStyle={{ color: "#f8fafc", fontWeight: "bold" }}
                    />
                    <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} />
                    <Line type="monotone" dataKey="trainLoss" stroke="#38bdf8" strokeWidth={2.5} name="Training Loss" dot={{ r: 4 }} />
                    <Line type="monotone" dataKey="valLoss" stroke="#f43f5e" strokeWidth={2.5} name="Validation Loss" dot={{ r: 4 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Metric Progression */}
            <div className="glass-panel rounded-2xl p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <TrendingUp className="w-4 h-4 text-emerald-400" />
                  <h3 className="text-sm font-bold text-white">Validation IoU & Dice Progression</h3>
                </div>
                <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded">
                  Best Dice: 0.9044
                </span>
              </div>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={TRAINING_HISTORY}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="epoch" stroke="#64748b" tickFormatter={(v) => `Ep ${v}`} />
                    <YAxis stroke="#64748b" domain={[0.5, 0.95]} />
                    <Tooltip
                      contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "8px" }}
                      labelStyle={{ color: "#f8fafc", fontWeight: "bold" }}
                    />
                    <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} />
                    <Line type="monotone" dataKey="valIoU" stroke="#10b981" strokeWidth={2.5} name="Validation IoU" dot={{ r: 4 }} />
                    <Line type="monotone" dataKey="valDice" stroke="#8b5cf6" strokeWidth={2.5} name="Validation Dice (F1)" dot={{ r: 4 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="glass-panel rounded-2xl p-6">
              <h3 className="text-sm font-bold text-white mb-3">Saved Loss Curve (s1_loss_curve.png)</h3>
              <div className="relative rounded-xl overflow-hidden bg-slate-950 border border-slate-800 aspect-[16/10]">
                <Image src="/images/loss_curves/s1_loss_curve.png" alt="Training Loss Curve" fill className="object-contain" />
              </div>
            </div>

            <div className="glass-panel rounded-2xl p-6">
              <h3 className="text-sm font-bold text-white mb-3">Saved Metric Curve (s1_metric_curve.png)</h3>
              <div className="relative rounded-xl overflow-hidden bg-slate-950 border border-slate-800 aspect-[16/10]">
                <Image src="/images/metric_curves/s1_metric_curve.png" alt="Validation Metric Curve" fill className="object-contain" />
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
