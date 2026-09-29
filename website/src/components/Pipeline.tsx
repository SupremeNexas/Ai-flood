"use client";

import React from "react";
import { PIPELINE_STAGES } from "@/data/projectData";
import {
  Satellite,
  Radio,
  Sliders,
  Grid,
  Cpu,
  Target,
  Activity,
  Shield,
  MapPin,
  ArrowRight,
  ArrowDown,
} from "lucide-react";

export default function Pipeline() {
  const getIcon = (iconName: string) => {
    switch (iconName) {
      case "Satellite":
        return <Satellite className="w-5 h-5 text-cyan-400" />;
      case "Radio":
        return <Radio className="w-5 h-5 text-blue-400" />;
      case "Sliders":
        return <Sliders className="w-5 h-5 text-indigo-400" />;
      case "Grid":
        return <Grid className="w-5 h-5 text-purple-400" />;
      case "Cpu":
        return <Cpu className="w-5 h-5 text-sky-400" />;
      case "Target":
        return <Target className="w-5 h-5 text-teal-400" />;
      case "Activity":
        return <Activity className="w-5 h-5 text-amber-400" />;
      case "Shield":
        return <Shield className="w-5 h-5 text-emerald-400" />;
      case "MapPin":
        return <MapPin className="w-5 h-5 text-rose-400" />;
      default:
        return <Cpu className="w-5 h-5 text-cyan-400" />;
    }
  };

  return (
    <section id="pipeline" className="py-16 sm:py-20 bg-[#070b14] relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800/50 text-cyan-400 text-xs font-semibold uppercase tracking-wider mb-3">
            <span>Modular Architecture</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
            End-to-End Processing Pipeline
          </h2>
          <p className="text-slate-300 text-base leading-relaxed">
            From raw radar orbital pulses to calibrated ground flood extents: every stage is verified with deterministic mathematical transformations.
          </p>
        </div>

        {/* Pipeline Grid / Flow */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative">
          {PIPELINE_STAGES.map((stage, idx) => (
            <div
              key={stage.step}
              className="glass-panel rounded-2xl p-6 relative group glow-border-hover flex flex-col justify-between"
            >
              {/* Top Row: Icon, Step Number, Badge */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-xl bg-slate-900/90 border border-slate-700/80 flex items-center justify-center shadow-inner">
                    {getIcon(stage.icon)}
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded-full bg-slate-800/80 text-slate-300 border border-slate-700">
                      {stage.badge}
                    </span>
                    <span className="text-xs font-mono font-bold text-slate-500">
                      0{stage.step}
                    </span>
                  </div>
                </div>

                {/* Title and Subtitle */}
                <h3 className="text-base font-bold text-white group-hover:text-cyan-400 transition-colors mb-1">
                  {stage.title}
                </h3>
                <div className="text-xs font-mono text-cyan-300/80 mb-2">
                  {stage.subtitle}
                </div>

                {/* Description */}
                <p className="text-xs text-slate-300 leading-relaxed">
                  {stage.desc}
                </p>
              </div>

              {/* Bottom Flow Indicator on Desktop */}
              {idx < PIPELINE_STAGES.length - 1 && (
                <div className="hidden lg:block absolute -right-3.5 top-1/2 -translate-y-1/2 z-10">
                  {(idx + 1) % 3 !== 0 && (
                    <div className="w-7 h-7 rounded-full bg-slate-900 border border-cyan-500/40 flex items-center justify-center text-cyan-400 shadow-sm shadow-cyan-950">
                      <ArrowRight className="w-3.5 h-3.5" />
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
