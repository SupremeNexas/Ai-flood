"use client";

import React from "react";
import Link from "next/link";
import { PROJECT_METADATA } from "@/data/projectData";
import { Waves, ExternalLink, Code2, FileText } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-[#05080f] border-t border-slate-900 py-12 text-slate-400 text-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
          {/* Col 1: Brand & Project */}
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-white">
                <Waves className="w-4 h-4" />
              </div>
              <span className="text-white font-bold text-base tracking-tight">
                {PROJECT_METADATA.shortTitle}
              </span>
            </div>
            <p className="text-slate-300 text-xs leading-relaxed max-w-sm">
              {PROJECT_METADATA.title}
            </p>
            <div className="text-[11px] text-cyan-400/90 font-mono">
              {PROJECT_METADATA.subtitle}
            </div>
          </div>

          {/* Col 2: Navigation Links */}
          <div>
            <h4 className="text-white font-bold text-xs uppercase tracking-wider mb-3">
              Research Sections
            </h4>
            <ul className="space-y-2">
              <li>
                <a href="#overview" className="hover:text-cyan-400 transition-colors">Overview & KPIs</a>
              </li>
              <li>
                <a href="#pipeline" className="hover:text-cyan-400 transition-colors">End-to-End Pipeline</a>
              </li>
              <li>
                <a href="#dataset" className="hover:text-cyan-400 transition-colors">Sen1Floods11 Dataset</a>
              </li>
              <li>
                <a href="#architecture" className="hover:text-cyan-400 transition-colors">U-Net Architecture</a>
              </li>
              <li>
                <a href="#evaluation" className="hover:text-cyan-400 transition-colors">90-Chip Evaluation</a>
              </li>
              <li>
                <a href="#predictions" className="hover:text-cyan-400 transition-colors">Prediction Gallery</a>
              </li>
            </ul>
          </div>

          {/* Col 3: Academic & Project Links */}
          <div>
            <h4 className="text-white font-bold text-xs uppercase tracking-wider mb-3">
              Project Links
            </h4>
            <ul className="space-y-2">
              <li>
                <a
                  href={PROJECT_METADATA.streamlitUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center space-x-1.5 hover:text-cyan-400 transition-colors"
                >
                  <span>Streamlit Demo App</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </li>
              <li>
                <a
                  href={PROJECT_METADATA.githubUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center space-x-1.5 hover:text-cyan-400 transition-colors"
                >
                  <Code2 className="w-3 h-3" />
                  <span>GitHub Repository</span>
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-slate-900/80 flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-500 gap-4">
          <div>
            {PROJECT_METADATA.academicContext}
          </div>
          <div>
            Domain: {PROJECT_METADATA.domain}
          </div>
        </div>
      </div>
    </footer>
  );
}
