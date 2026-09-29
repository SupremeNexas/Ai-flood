"use client";

import React from "react";
import { TECH_STACK } from "@/data/projectData";
import { Code2, Terminal } from "lucide-react";

export default function TechStack() {
  return (
    <section className="py-16 sm:py-20 bg-[#090e1a] border-t border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800/50 text-cyan-400 text-xs font-semibold uppercase tracking-wider mb-3">
            <Code2 className="w-3.5 h-3.5" />
            <span>Implementation Frameworks</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
            Production Technology Stack
          </h2>
          <p className="text-slate-300 text-base leading-relaxed">
            Built using industry-standard deep learning and geospatial remote sensing libraries, wrapped in modern reactive interfaces.
          </p>
        </div>

        {/* Tech Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {TECH_STACK.map((tech, idx) => (
            <div
              key={idx}
              className="glass-panel rounded-xl p-5 border border-slate-800/80 hover:border-cyan-500/50 transition-colors flex items-start space-x-3.5"
            >
              <div className="w-9 h-9 rounded-lg bg-slate-900 border border-slate-700/80 flex items-center justify-center shrink-0 font-mono text-cyan-400 font-bold text-xs">
                &gt;_
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h3 className="text-sm font-bold text-white">{tech.name}</h3>
                  <span className="text-[10px] font-mono text-cyan-400/90 bg-cyan-950/60 px-1.5 py-0.5 rounded border border-cyan-800/40">
                    {tech.category}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-1">{tech.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
