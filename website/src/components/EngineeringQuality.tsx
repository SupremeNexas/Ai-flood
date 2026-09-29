"use client";

import React from "react";
import { VERIFIED_BENCHMARKS } from "@/data/projectData";
import { ShieldCheck, CheckCircle2, Lock, FileCheck2, Cpu } from "lucide-react";

export default function EngineeringQuality() {
  const qualityItems = [
    {
      title: "Unit Test Verification",
      value: "39 / 39 (100%)",
      desc: "Pytest test suite covering dataloaders, preprocessing, model forward passes, loss masking, metrics, and Streamlit UI components.",
      icon: <CheckCircle2 className="w-5 h-5 text-emerald-400" />,
      color: "border-emerald-500/50",
    },
    {
      title: "Data Leakage Audit",
      value: "0 Overlapping Chips",
      desc: "Strict pairwise set intersection checks verified zero data leakage between train (252), val (89), test (90), and holdout (15) splits.",
      icon: <Lock className="w-5 h-5 text-cyan-400" />,
      color: "border-cyan-500/50",
    },
    {
      title: "Official Test Coverage",
      value: "90 / 90 (100%)",
      desc: "Evaluated across every single chip in flood_test_data.csv without silent exclusions, calculating 20,517,367 valid pixels.",
      icon: <FileCheck2 className="w-5 h-5 text-blue-400" />,
      color: "border-blue-500/50",
    },
    {
      title: "Deterministic Execution",
      value: "Seed 42 Enforced",
      desc: "PyTorch, CUDA, and NumPy random seeds fixed at 42 across all dataset loaders, geometric augmentations, and evaluation pipelines.",
      icon: <Cpu className="w-5 h-5 text-purple-400" />,
      color: "border-purple-500/50",
    },
  ];

  return (
    <section className="py-16 sm:py-20 bg-[#070b14] border-t border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-emerald-950/80 border border-emerald-800/50 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-3">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Software Engineering & Verification</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
            Audited Engineering Quality
          </h2>
          <p className="text-slate-300 text-base leading-relaxed">
            Every software module undergoes automated testing, strict seed enforcement, and rigorous split mutual exclusivity verification.
          </p>
        </div>

        {/* 4 Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {qualityItems.map((item, idx) => (
            <div
              key={idx}
              className={`glass-panel rounded-2xl p-6 sm:p-7 border-l-4 ${item.color} glow-border-hover flex flex-col justify-between`}
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2.5">
                    {item.icon}
                    <h3 className="text-base font-bold text-white">{item.title}</h3>
                  </div>
                  <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-950/80 px-2.5 py-1 rounded-md border border-emerald-800/50">
                    {item.value}
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {item.desc}
                </p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80 text-[11px] font-mono text-slate-500">
                Verified in ./.venv/bin/pytest tests/ -v
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
