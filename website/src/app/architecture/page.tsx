"use client";

import React, { useState } from "react";
import Link from "next/link";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import {
  Layers,
  GitBranch,
  Cpu,
  Workflow,
  Server,
  ExternalLink,
  Maximize2,
  ShieldCheck,
  CheckCircle2,
  Sparkles,
  Info,
  ChevronRight,
  Terminal,
  Activity,
  ArrowUpRight
} from "lucide-react";

interface DiagramTab {
  id: string;
  label: string;
  shortLabel: string;
  badge: string;
  icon: React.ElementType;
  htmlPath: string;
  title: string;
  description: string;
  highlights: {
    title: string;
    description: string;
    tag: string;
  }[];
  specDetails: {
    label: string;
    value: string;
  }[];
}

const DIAGRAM_TABS: DiagramTab[] = [
  {
    id: "system-architecture",
    label: "System Architecture",
    shortLabel: "System",
    badge: "End-to-End",
    icon: Layers,
    htmlPath: "/architecture/system-architecture.html",
    title: "AI Flood Detection System Architecture",
    description:
      "Comprehensive end-to-end topology verifying SAR satellite data ingestion, preprocessing pipeline, PyTorch U-Net neural inference, probability thresholding, and the decoupled dual-cloud web presentation tier.",
    highlights: [
      {
        title: "All-Weather SAR Ingestion",
        description:
          "Sentinel-1 C-band Synthetic Aperture Radar operates day and night, penetrating heavy tropical cloud cover to capture flood events.",
        tag: "Sentinel-1 SAR",
      },
      {
        title: "Decoupled Web Hosting",
        description:
          "Next.js public website hosted globally on Vercel Edge Network while the PyTorch Streamlit showcase runs containerized on Render.",
        tag: "Dual-Tier Cloud",
      },
      {
        title: "Automated Flooded Area Mapping",
        description:
          "Sigmoid continuous flood probabilities thresholded at τ=0.50 and translated to nominal ground area (km²) at 10m Ground Sample Distance.",
        tag: "GIS Mapping",
      },
    ],
    specDetails: [
      { label: "Architecture Type", value: "Component Topology" },
      { label: "Verified Components", value: "14 Subsystems" },
      { label: "Quality Profile", value: "Archify Showcase" },
      { label: "Security & Regional Boundaries", value: "2 Boundaries" },
    ],
  },
  {
    id: "data-flow",
    label: "Data Flow Pipeline",
    shortLabel: "Data Flow",
    badge: "5 Stages",
    icon: GitBranch,
    htmlPath: "/architecture/data-flow.html",
    title: "Satellite SAR Ingestion, Segmentation & Evaluation Data Flow",
    description:
      "Strict linear data lineage separating production inference (radiometric dB calibration to nominal area calculation) from academic ground truth evaluation (QC filtering across 90 official Sen1Floods11 test chips).",
    highlights: [
      {
        title: "Radiometric dB Calibration",
        description:
          "SAR backscatter clipped to [-35.0, 5.0] dB and min-max scaled to [0.0, 1.0] across both VV and VH polarizations.",
        tag: "[-35, 5] dB",
      },
      {
        title: "Sensor QC & No-Data Masking",
        description:
          "Sensor no-data pixels and invalid cloud regions (-1) strictly masked out during evaluation to prevent metric distortion.",
        tag: "Mask Validator",
      },
      {
        title: "Official Benchmark Evaluation",
        description:
          "Evaluation core rigorously benchmarks predictions against hand-labeled ground truth (0.5548 IoU, 0.7137 Dice/F1 across 20.5M valid pixels).",
        tag: "Sen1Floods11",
      },
    ],
    specDetails: [
      { label: "Pipeline Stages", value: "5 Discrete Stages" },
      { label: "Input Tensor Shape", value: "[2, 256, 256] Float32" },
      { label: "Benchmark Test Chips", value: "90 Hand-Labeled" },
      { label: "Evaluated Pixels", value: "20,517,367 Valid" },
    ],
  },
  {
    id: "model-pipeline",
    label: "ML Model Pipeline",
    shortLabel: "U-Net",
    badge: "7.76M Params",
    icon: Cpu,
    htmlPath: "/architecture/model-pipeline.html",
    title: "PyTorch U-Net Neural Network Architecture",
    description:
      "Detailed neural network breakdown featuring a 4-stage contracting encoder (32 to 256 ch), 512-channel bottleneck with Spatial Dropout (0.10), 4-stage expanding decoder with bilinear upsampling, and multi-scale skip connections.",
    highlights: [
      {
        title: "Group Normalization (G=8)",
        description:
          "Channels divided into 8 groups per layer for stable normalization during small-batch SAR training without batch-size dependence.",
        tag: "GroupNorm G=8",
      },
      {
        title: "Bilinear 2x Upsampling",
        description:
          "Smooth bilinear interpolation eliminates checkerboard deconvolution artifacts common in transposed convolutions.",
        tag: "Bilinear 2x",
      },
      {
        title: "Multi-Scale Skip Connections",
        description:
          "Direct concatenation of high-resolution encoder feature maps preserves fine boundary delineation around floodplains.",
        tag: "Skip Concat",
      },
    ],
    specDetails: [
      { label: "Total Trainable Parameters", value: "7,760,257" },
      { label: "Encoder Stages", value: "4 (32, 64, 128, 256)" },
      { label: "Bottleneck Depth", value: "512 ch + Dropout 0.10" },
      { label: "Output Head", value: "1x1 Conv + Sigmoid" },
    ],
  },
  {
    id: "streamlit-workflow",
    label: "Streamlit Workflow",
    shortLabel: "Workflow",
    badge: "Dual-Path",
    icon: Workflow,
    htmlPath: "/architecture/streamlit-workflow.html",
    title: "Streamlit Dual-Mode Inference & Evaluation Workflow",
    description:
      "Interactive multi-swimlane workflow illustrating Path A (Sen1Floods11 Official Benchmark with ground truth metrics) and Path B (Custom GeoTIFF Upload with automated raster validation and nominal area calculation).",
    highlights: [
      {
        title: "Path A: Official Benchmark Mode",
        description:
          "Users select any of the 90 Sen1Floods11 test chips to view real-time side-by-side segmentation and confusion matrix statistics.",
        tag: "Path A: Benchmark",
      },
      {
        title: "Path B: Custom GeoTIFF Upload",
        description:
          "Accepts external 2-band or 1-band Sentinel-1 GeoTIFF rasters, validates spatial bounds and bands, and maps flooded area in km².",
        tag: "Path B: Upload",
      },
      {
        title: "Diagnostic Visual Panels",
        description:
          "Multi-panel diagnostic view: SAR False-Color Composite, Ground Truth, Predicted Mask, Flood Probability Heatmap, and Overlay.",
        tag: "5 Panels",
      },
    ],
    specDetails: [
      { label: "Swimlanes", value: "4 Execution Lanes" },
      { label: "Workflow Phases", value: "3 Phased Horizons" },
      { label: "Threshold Control", value: "Dynamic Slider (τ=0.10–0.90)" },
      { label: "Area Resolution", value: "100 m² per pixel" },
    ],
  },
  {
    id: "deployment",
    label: "Deployment Topology",
    shortLabel: "Deployment",
    badge: "Dual-Tier",
    icon: Server,
    htmlPath: "/architecture/deployment.html",
    title: "AI Flood Detection Dual-Tier Deployment Architecture",
    description:
      "Production deployment architecture illustrating developer workflow from GitHub monorepo to independent Vercel Edge Network (Next.js visual documentation) and Render Cloud (Streamlit Python ML Web Service).",
    highlights: [
      {
        title: "Zero Cross-Tier Coupling",
        description:
          "Presentation website and machine-learning demo operate on independent release cycles with zero shared runtime dependencies.",
        tag: "Decoupled",
      },
      {
        title: "Vercel Edge Network",
        description:
          "Next.js 16 + React 19 visual project website statically optimized and delivered globally with sub-millisecond edge latency.",
        tag: "Vercel Edge",
      },
      {
        title: "Render ML Container",
        description:
          "Python 3.11 web service with PyTorch CPU inference and Rasterio GIS stack running the live Streamlit interactive showcase.",
        tag: "Render Cloud",
      },
    ],
    specDetails: [
      { label: "Source Repository", value: "SupremeNexas/Ai-flood" },
      { label: "Website Runtime", value: "Next.js 16 / React 19" },
      { label: "ML Service Runtime", value: "Python 3.11 / PyTorch CPU" },
      { label: "Model Artifact", value: "checkpoints/best_s1.pt" },
    ],
  },
];

export default function ArchitecturePage() {
  const [activeTabId, setActiveTabId] = useState<string>("system-architecture");
  const activeTab = DIAGRAM_TABS.find((tab) => tab.id === activeTabId) || DIAGRAM_TABS[0];

  return (
    <main className="min-h-screen flex flex-col bg-[#070b14] text-slate-100 pt-20">
      <Navbar />

      {/* Header Banner */}
      <section className="relative overflow-hidden py-12 border-b border-slate-800/80 bg-gradient-to-b from-[#0b1220] to-[#070b14]">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,rgba(6,182,212,0.15),rgba(255,255,255,0))] pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          {/* Breadcrumb */}
          <div className="flex items-center space-x-2 text-xs text-slate-400 mb-4 font-mono">
            <Link href="/" className="hover:text-cyan-400 transition-colors">
              Home
            </Link>
            <ChevronRight className="w-3.5 h-3.5 text-slate-600" />
            <span className="text-cyan-400 font-semibold">Architecture & Workflows</span>
          </div>

          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div>
              <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-700/50 text-cyan-400 text-xs font-mono font-medium mb-3">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Verified Visual Architecture Specifications</span>
              </div>
              <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
                System Architecture & Deep Learning Pipelines
              </h1>
              <p className="mt-2 text-base text-slate-300 max-w-3xl leading-relaxed">
                Explore the complete verified technical architecture of the AI Flood Detection platform — from
                Sentinel-1 SAR radiometric preprocessing to PyTorch U-Net inference, interactive evaluation workflows,
                and production cloud deployment.
              </p>
            </div>

            {/* Quick Stats Pill */}
            <div className="flex flex-wrap md:flex-col gap-2 shrink-0 bg-slate-900/90 border border-slate-800 rounded-xl p-3 text-xs font-mono">
              <div className="flex items-center justify-between gap-4">
                <span className="text-slate-400">Total Diagrams:</span>
                <span className="text-cyan-400 font-bold">5 Showcase Visuals</span>
              </div>
              <div className="flex items-center justify-between gap-4">
                <span className="text-slate-400">Model Weights:</span>
                <span className="text-emerald-400 font-bold">7.76M Parameters</span>
              </div>
              <div className="flex items-center justify-between gap-4">
                <span className="text-slate-400">Test Validation:</span>
                <span className="text-violet-400 font-bold">90/90 Chips (0.5548 IoU)</span>
              </div>
            </div>
          </div>

          {/* Navigation Tabs Bar */}
          <div className="mt-8 flex items-center space-x-2 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-slate-800">
            {DIAGRAM_TABS.map((tab) => {
              const Icon = tab.icon;
              const isActive = tab.id === activeTabId;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTabId(tab.id)}
                  className={`flex items-center space-x-2.5 px-4 py-2.5 rounded-lg font-medium text-xs sm:text-sm transition-all whitespace-nowrap cursor-pointer ${
                    isActive
                      ? "bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-300 border border-cyan-500/50 shadow-lg shadow-cyan-950/50"
                      : "bg-slate-900/60 text-slate-400 border border-slate-800/80 hover:bg-slate-800/80 hover:text-slate-200"
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? "text-cyan-400" : "text-slate-400"}`} />
                  <span>{tab.label}</span>
                  <span
                    className={`px-1.5 py-0.5 rounded text-[10px] font-mono ${
                      isActive
                        ? "bg-cyan-500/30 text-cyan-200 border border-cyan-400/30"
                        : "bg-slate-800 text-slate-400"
                    }`}
                  >
                    {tab.badge}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </section>

      {/* Main Content Area */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex-1 w-full">
        {/* Active Diagram Header Info */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 mb-8 backdrop-blur-sm">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div className="space-y-2">
              <div className="flex items-center space-x-3">
                <span className="px-2.5 py-1 rounded-md bg-cyan-950 border border-cyan-800 text-cyan-400 text-xs font-mono font-medium">
                  {activeTab.badge}
                </span>
                <span className="text-xs text-slate-400 font-mono">
                  Schema: Archify Showcase Profile (100% Geometry Passed)
                </span>
              </div>
              <h2 className="text-2xl font-bold text-white tracking-tight">{activeTab.title}</h2>
              <p className="text-slate-300 text-sm max-w-4xl leading-relaxed">{activeTab.description}</p>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap sm:flex-nowrap items-center gap-3 shrink-0">
              <a
                href={activeTab.htmlPath}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs sm:text-sm font-semibold transition-all shadow-md shadow-cyan-600/30 hover:scale-[1.02]"
              >
                <Maximize2 className="w-4 h-4" />
                <span>Open Interactive Viewer</span>
                <ArrowUpRight className="w-3.5 h-3.5 ml-0.5 opacity-80" />
              </a>
            </div>
          </div>

          {/* Quick Spec Details Grid */}
          <div className="mt-6 pt-6 border-t border-slate-800/80 grid grid-cols-2 sm:grid-cols-4 gap-4">
            {activeTab.specDetails.map((spec, idx) => (
              <div key={idx} className="bg-slate-950/60 border border-slate-800/60 rounded-lg p-3">
                <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">{spec.label}</div>
                <div className="text-sm font-semibold text-white font-mono mt-1">{spec.value}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Embedded Interactive Viewer Frame */}
        <div className="relative rounded-2xl border border-slate-800 overflow-hidden bg-slate-950 shadow-2xl shadow-black/80 mb-10 group">
          {/* Frame Top Toolbar */}
          <div className="flex items-center justify-between px-4 py-3 bg-slate-900 border-b border-slate-800 text-xs font-mono">
            <div className="flex items-center space-x-2">
              <div className="flex space-x-1.5">
                <div className="w-3 h-3 rounded-full bg-red-500/80" />
                <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                <div className="w-3 h-3 rounded-full bg-green-500/80" />
              </div>
              <span className="text-slate-400 ml-2 hidden sm:inline">Archify Interactive Runtime</span>
              <span className="text-slate-600 hidden sm:inline">•</span>
              <span className="text-cyan-400 truncate max-w-xs">{activeTab.htmlPath}</span>
            </div>

            <div className="flex items-center space-x-3 text-slate-400">
              <span className="hidden md:inline text-[11px] text-slate-400">
                Interactive: Pan, Zoom, Focus Views & Search
              </span>
              <a
                href={activeTab.htmlPath}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-1 text-cyan-400 hover:text-cyan-300 font-medium"
              >
                <span>Fullscreen</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>

          {/* Iframe */}
          <div className="w-full h-[650px] sm:h-[720px] lg:h-[780px] bg-[#0b1220]">
            <iframe
              key={activeTab.htmlPath}
              src={activeTab.htmlPath}
              title={activeTab.title}
              className="w-full h-full border-0"
              loading="lazy"
            />
          </div>
        </div>

        {/* Architectural Highlights Cards */}
        <div className="mb-12">
          <div className="flex items-center space-x-2 mb-6">
            <Activity className="w-5 h-5 text-cyan-400" />
            <h3 className="text-xl font-bold text-white tracking-tight">Key Architectural Decisions & Rationale</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {activeTab.highlights.map((highlight, idx) => (
              <div
                key={idx}
                className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 hover:border-slate-700 transition-colors"
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="px-2 py-0.5 rounded bg-cyan-950/80 border border-cyan-800/60 text-cyan-400 text-xs font-mono font-medium">
                    {highlight.tag}
                  </span>
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                </div>
                <h4 className="text-base font-semibold text-white mb-2">{highlight.title}</h4>
                <p className="text-slate-300 text-sm leading-relaxed">{highlight.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom Technical Verification Notice */}
        <div className="bg-gradient-to-r from-slate-900 to-[#0c1527] border border-cyan-900/40 rounded-2xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex items-start space-x-4">
            <div className="p-3 rounded-xl bg-cyan-950/80 border border-cyan-800/60 text-cyan-400 shrink-0">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-base font-semibold text-white">100% Grounded in Production Codebase</h4>
              <p className="text-slate-300 text-xs sm:text-sm mt-1 max-w-2xl leading-relaxed">
                All diagrams are deterministically generated from verified repository sources (<code className="text-cyan-400 font-mono">src/models/unet.py</code>,{" "}
                <code className="text-cyan-400 font-mono">src/data/preprocessing.py</code>,{" "}
                <code className="text-cyan-400 font-mono">app.py</code>, and{" "}
                <code className="text-cyan-400 font-mono">configs/config.yaml</code>). Zero simulated components or fictional services.
              </p>
            </div>
          </div>

          <Link
            href="/#demo"
            className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-xs sm:text-sm font-medium transition-colors shrink-0"
          >
            <span>Launch Live ML Demo</span>
            <ExternalLink className="w-4 h-4 text-slate-400" />
          </Link>
        </div>
      </section>

      <Footer />
    </main>
  );
}
