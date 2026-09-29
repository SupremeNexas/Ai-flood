"use client";

import React from "react";
import Image from "next/image";
import { PROJECT_METADATA } from "@/data/projectData";
import { Play, ExternalLink, Sliders, UploadCloud, CheckCircle2, ShieldCheck, Terminal } from "lucide-react";

export default function DemoSection() {
  return (
    <section id="demo" className="py-16 sm:py-20 bg-[#090e1a] border-t border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800/50 text-cyan-400 text-xs font-semibold uppercase tracking-wider mb-3">
            <Play className="w-3.5 h-3.5 fill-cyan-400" />
            <span>Interactive Application Showcase</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
            Live Streamlit AI Inference Dashboard
          </h2>
          <p className="text-slate-300 text-base leading-relaxed">
            The Python Streamlit application provides a real-time testing harness for running live U-Net inference on official test chips and custom user-uploaded GeoTIFF rasters.
          </p>
        </div>

        {/* 2 Operating Modes Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
          {/* Mode A */}
          <div className="glass-panel rounded-2xl p-6 sm:p-8 glow-border-hover border-l-4 border-l-cyan-500">
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-2.5 rounded-xl bg-cyan-950/80 text-cyan-400 border border-cyan-800/50">
                <Sliders className="w-5 h-5" />
              </div>
              <div>
                <span className="text-xs font-mono uppercase text-cyan-400 font-bold">Mode A</span>
                <h3 className="text-lg font-bold text-white">Benchmark Test-Chip Prediction</h3>
              </div>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed mb-4">
              Select from the official Sen1Floods11 test chips. Adjust the probability threshold in real time and inspect all 5 diagnostic panels: Input SAR, Ground Truth, Predicted Mask, Overlay, and the Flood Probability Map.
            </p>
            <ul className="space-y-1.5 text-xs text-slate-300">
              <li className="flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Live computation of IoU, Dice, Precision, and Recall</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Nominal flooded area (100 m²/pixel) and confusion counts</span>
              </li>
            </ul>
          </div>

          {/* Mode B */}
          <div className="glass-panel rounded-2xl p-6 sm:p-8 glow-border-hover border-l-4 border-l-blue-500">
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-2.5 rounded-xl bg-blue-950/80 text-blue-400 border border-blue-800/50">
                <UploadCloud className="w-5 h-5" />
              </div>
              <div>
                <span className="text-xs font-mono uppercase text-blue-400 font-bold">Mode B</span>
                <h3 className="text-lg font-bold text-white">Custom SAR GeoTIFF Upload</h3>
              </div>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed mb-4">
              Upload any dual-polarization Sentinel-1 GeoTIFF raster (.tif / .tiff). The system automatically validates channel formats, applies radiometric normalization, and outputs flood segmentation in &lt;50ms.
            </p>
            <ul className="space-y-1.5 text-xs text-slate-300">
              <li className="flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Automatic 2-band ($VV$ & $VH$) validation & normalization</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Detected flood pixels, coverage percentage, and area estimate</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Big Launch Banner Box */}
        <div className="glass-panel-glow rounded-2xl p-8 text-center relative overflow-hidden">
          <div className="max-w-2xl mx-auto">
            <h3 className="text-2xl font-extrabold text-white mb-3">
              Ready to Test Live Inference?
            </h3>
            <p className="text-slate-300 text-sm mb-6 leading-relaxed">
              Launch the local Streamlit application to experiment with the model weights (<code className="text-cyan-400">checkpoints/best_s1.pt</code>), test arbitrary chips, or upload external radar scenes.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <a
                href={PROJECT_METADATA.streamlitUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center space-x-2 px-8 py-4 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold text-sm shadow-xl shadow-cyan-500/25 transition-all hover:scale-105"
              >
                <span>Launch Live Streamlit Application</span>
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>

            <div className="mt-6 flex items-center justify-center space-x-2 text-xs text-slate-400 font-mono">
              <Terminal className="w-3.5 h-3.5 text-cyan-400" />
              <span>CLI Launch Command: <code>./.venv/bin/streamlit run app.py</code></span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
