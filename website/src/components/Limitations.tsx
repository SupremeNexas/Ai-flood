"use client";

import React from "react";
import { LIMITATIONS_DATA } from "@/data/projectData";
import {
  AlertTriangle,
  Trees,
  CloudOff,
  Database,
  Globe,
  GraduationCap,
  ShieldAlert,
} from "lucide-react";

export default function Limitations() {
  const getIcon = (iconName: string) => {
    switch (iconName) {
      case "AlertTriangle":
        return <AlertTriangle className="w-5 h-5 text-amber-400" />;
      case "Trees":
        return <Trees className="w-5 h-5 text-emerald-400" />;
      case "CloudOff":
        return <CloudOff className="w-5 h-5 text-blue-400" />;
      case "Database":
        return <Database className="w-5 h-5 text-purple-400" />;
      case "Globe":
        return <Globe className="w-5 h-5 text-cyan-400" />;
      case "GraduationCap":
        return <GraduationCap className="w-5 h-5 text-rose-400" />;
      default:
        return <AlertTriangle className="w-5 h-5 text-amber-400" />;
    }
  };

  return (
    <section className="py-16 sm:py-20 bg-[#070b14] border-t border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-rose-950/80 border border-rose-800/50 text-rose-400 text-xs font-semibold uppercase tracking-wider mb-3">
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>Academic Rigor & Transparency</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
            Documented Physical & System Limitations
          </h2>
          <p className="text-slate-300 text-base leading-relaxed">
            In accordance with scientific engineering practices, all physical radar interactions, dataset constraints, and operational bounds are explicitly documented.
          </p>
        </div>

        {/* 6 Limitations Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {LIMITATIONS_DATA.map((item, idx) => (
            <div
              key={idx}
              className="glass-panel rounded-2xl p-6 relative group glow-border-hover flex flex-col justify-between"
            >
              <div>
                <div className="w-10 h-10 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center mb-4">
                  {getIcon(item.icon)}
                </div>
                <h3 className="text-base font-bold text-white mb-2 group-hover:text-cyan-400 transition-colors">
                  {item.title}
                </h3>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {item.description}
                </p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] font-mono text-slate-500">
                Scientific Caveat #{idx + 1}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
