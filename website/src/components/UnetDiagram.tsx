"use client";

import React, { useState } from "react";
import { UNET_ARCHITECTURE_SPECS } from "@/data/projectData";
import { Cpu, ShieldCheck, Zap, Layers, RefreshCw, GitFork } from "lucide-react";

export default function UnetDiagram() {
  const [selectedBlock, setSelectedBlock] = useState<string | null>("bottleneck");

  return (
    <section id="architecture" className="py-16 sm:py-20 bg-[#090e1a] border-t border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800/50 text-cyan-400 text-xs font-semibold uppercase tracking-wider mb-3">
            <Cpu className="w-3.5 h-3.5" />
            <span>Neural Network Topology</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
            PyTorch U-Net Architecture
          </h2>
          <p className="text-slate-300 text-base leading-relaxed">
            Customized 4-stage encoder-decoder semantic segmentation network equipped with Group Normalization ($G=8$) and direct spatial skip connections.
          </p>
        </div>

        {/* Big Interactive Architecture Diagram */}
        <div className="glass-panel-glow rounded-2xl p-6 sm:p-8 mb-10 overflow-hidden">
          {/* Top Info Bar */}
          <div className="flex items-center justify-between pb-6 mb-6 border-b border-slate-800 flex-wrap gap-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-xl bg-cyan-950/80 text-cyan-400 border border-cyan-800/50">
                <Layers className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">4-Stage Contracting & Expanding U-Net</h3>
                <p className="text-xs text-slate-400">Total Trainable Parameters: <span className="text-cyan-400 font-mono font-bold">7,760,257</span></p>
              </div>
            </div>

            <div className="flex items-center space-x-2 flex-wrap gap-2 text-xs font-mono">
              <span className="px-2.5 py-1 rounded-md bg-slate-900 border border-slate-700 text-slate-300">
                Input: 2 × 256 × 256
              </span>
              <span className="px-2.5 py-1 rounded-md bg-cyan-950/80 border border-cyan-800/60 text-cyan-400">
                GroupNorm: G=8
              </span>
              <span className="px-2.5 py-1 rounded-md bg-blue-950/80 border border-blue-800/60 text-blue-400">
                Output: 1 × 256 × 256
              </span>
            </div>
          </div>

          {/* SVG / Visual Flow Representation */}
          <div className="relative py-6 px-2 sm:px-6">
            <div className="grid grid-cols-1 md:grid-cols-9 gap-3 items-center text-center">
              {/* 1. Input Tensor */}
              <div
                onClick={() => setSelectedBlock("input")}
                className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                  selectedBlock === "input"
                    ? "bg-cyan-950/80 border-cyan-400 shadow-md shadow-cyan-500/20"
                    : "bg-slate-900/80 border-slate-800 hover:border-slate-700"
                }`}
              >
                <div className="text-[10px] font-mono uppercase text-slate-400">Input</div>
                <div className="text-sm font-extrabold text-white my-1">2 × 256²</div>
                <div className="text-[10px] text-cyan-400">VV + VH SAR</div>
              </div>

              {/* 2. Encoder 1 */}
              <div
                onClick={() => setSelectedBlock("enc1")}
                className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                  selectedBlock === "enc1"
                    ? "bg-blue-950/80 border-blue-400 shadow-md shadow-blue-500/20"
                    : "bg-slate-900/80 border-slate-800 hover:border-slate-700"
                }`}
              >
                <div className="text-[10px] font-mono text-blue-400">Enc 1</div>
                <div className="text-sm font-extrabold text-white my-1">32 ch</div>
                <div className="text-[10px] text-slate-400">256 × 256</div>
              </div>

              {/* 3. Encoder 2 */}
              <div
                onClick={() => setSelectedBlock("enc2")}
                className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                  selectedBlock === "enc2"
                    ? "bg-blue-950/80 border-blue-400 shadow-md shadow-blue-500/20"
                    : "bg-slate-900/80 border-slate-800 hover:border-slate-700"
                }`}
              >
                <div className="text-[10px] font-mono text-blue-400">Enc 2</div>
                <div className="text-sm font-extrabold text-white my-1">64 ch</div>
                <div className="text-[10px] text-slate-400">128 × 128</div>
              </div>

              {/* 4. Encoder 3 & 4 */}
              <div
                onClick={() => setSelectedBlock("enc34")}
                className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                  selectedBlock === "enc34"
                    ? "bg-blue-950/80 border-blue-400 shadow-md shadow-blue-500/20"
                    : "bg-slate-900/80 border-slate-800 hover:border-slate-700"
                }`}
              >
                <div className="text-[10px] font-mono text-blue-400">Enc 3 / 4</div>
                <div className="text-sm font-extrabold text-white my-1">128 / 256</div>
                <div className="text-[10px] text-slate-400">64² ➔ 32²</div>
              </div>

              {/* 5. Bottleneck (Center) */}
              <div
                onClick={() => setSelectedBlock("bottleneck")}
                className={`p-4 rounded-xl border-2 transition-all cursor-pointer ${
                  selectedBlock === "bottleneck"
                    ? "bg-amber-950/80 border-amber-400 shadow-lg shadow-amber-500/20"
                    : "bg-amber-950/30 border-amber-800/60 hover:border-amber-700"
                }`}
              >
                <div className="text-[10px] font-mono uppercase text-amber-400 font-bold">Bottleneck</div>
                <div className="text-base font-extrabold text-amber-300 my-1">512 ch</div>
                <div className="text-[10px] text-amber-400/80">16 × 16 px</div>
              </div>

              {/* 6. Decoder 1 & 2 */}
              <div
                onClick={() => setSelectedBlock("dec12")}
                className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                  selectedBlock === "dec12"
                    ? "bg-emerald-950/80 border-emerald-400 shadow-md shadow-emerald-500/20"
                    : "bg-slate-900/80 border-slate-800 hover:border-slate-700"
                }`}
              >
                <div className="text-[10px] font-mono text-emerald-400">Dec 1 / 2</div>
                <div className="text-sm font-extrabold text-white my-1">256 / 128</div>
                <div className="text-[10px] text-slate-400">32² ➔ 64²</div>
              </div>

              {/* 7. Decoder 3 */}
              <div
                onClick={() => setSelectedBlock("dec3")}
                className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                  selectedBlock === "dec3"
                    ? "bg-emerald-950/80 border-emerald-400 shadow-md shadow-emerald-500/20"
                    : "bg-slate-900/80 border-slate-800 hover:border-slate-700"
                }`}
              >
                <div className="text-[10px] font-mono text-emerald-400">Dec 3</div>
                <div className="text-sm font-extrabold text-white my-1">64 ch</div>
                <div className="text-[10px] text-slate-400">128 × 128</div>
              </div>

              {/* 8. Decoder 4 */}
              <div
                onClick={() => setSelectedBlock("dec4")}
                className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                  selectedBlock === "dec4"
                    ? "bg-emerald-950/80 border-emerald-400 shadow-md shadow-emerald-500/20"
                    : "bg-slate-900/80 border-slate-800 hover:border-slate-700"
                }`}
              >
                <div className="text-[10px] font-mono text-emerald-400">Dec 4</div>
                <div className="text-sm font-extrabold text-white my-1">32 ch</div>
                <div className="text-[10px] text-slate-400">256 × 256</div>
              </div>

              {/* 9. Output Mask */}
              <div
                onClick={() => setSelectedBlock("output")}
                className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                  selectedBlock === "output"
                    ? "bg-cyan-950/80 border-cyan-400 shadow-md shadow-cyan-500/20"
                    : "bg-slate-900/80 border-slate-800 hover:border-slate-700"
                }`}
              >
                <div className="text-[10px] font-mono uppercase text-slate-400">Output</div>
                <div className="text-sm font-extrabold text-white my-1">1 × 256²</div>
                <div className="text-[10px] text-cyan-400">Sigmoid [0, 1]</div>
              </div>
            </div>

            {/* Visual Skip Connection Indicator */}
            <div className="mt-4 pt-3 border-t border-dashed border-purple-800/60 flex items-center justify-between text-xs text-purple-400 font-mono px-4">
              <div className="flex items-center space-x-2">
                <GitFork className="w-4 h-4" />
                <span>Direct Skip Connections (Channel Concatenation)</span>
              </div>
              <span className="hidden sm:inline">Preserves sharp spatial boundaries (canals, levees, roads)</span>
            </div>
          </div>
        </div>

        {/* 4 Deep Dive Architecture Pillars */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          <div className="glass-panel rounded-xl p-5 border-l-4 border-l-cyan-500">
            <div className="flex items-center space-x-2 text-cyan-400 font-bold text-xs uppercase mb-2">
              <ShieldCheck className="w-4 h-4" />
              <span>Group Normalization (G=8)</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Batch-size independent normalization dividing 32–512 channels into 8 groups. Avoids batch statistics distortion during small-batch training.
            </p>
          </div>

          <div className="glass-panel rounded-xl p-5 border-l-4 border-l-emerald-500">
            <div className="flex items-center space-x-2 text-emerald-400 font-bold text-xs uppercase mb-2">
              <RefreshCw className="w-4 h-4" />
              <span>Bilinear Upsampling</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Replaces standard ConvTranspose2d to eliminate checkerboard deconvolution artifacts across continuous water surfaces.
            </p>
          </div>

          <div className="glass-panel rounded-xl p-5 border-l-4 border-l-purple-500">
            <div className="flex items-center space-x-2 text-purple-400 font-bold text-xs uppercase mb-2">
              <GitFork className="w-4 h-4" />
              <span>Skip Connections</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Connects shallow high-resolution encoder features directly to decoder blocks, preventing loss of fine spatial boundary detail.
            </p>
          </div>

          <div className="glass-panel rounded-xl p-5 border-l-4 border-l-amber-500">
            <div className="flex items-center space-x-2 text-amber-400 font-bold text-xs uppercase mb-2">
              <Zap className="w-4 h-4" />
              <span>1×1 Output Conv</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Projects the final 32-channel spatial representation into a single logit map, converted to flood probability via the element-wise Sigmoid function.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
