"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { PROJECT_METADATA } from "@/data/projectData";
import { Waves, ExternalLink, Menu, X, ShieldCheck } from "lucide-react";

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const navLinks = [
    { name: "Overview", href: "#overview" },
    { name: "Pipeline", href: "#pipeline" },
    { name: "Dataset", href: "#dataset" },
    { name: "SAR Radar", href: "#sar" },
    { name: "U-Net", href: "#architecture" },
    { name: "Training", href: "#training" },
    { name: "Evaluation", href: "#evaluation" },
    { name: "Predictions", href: "#predictions" },
    { name: "Live Demo", href: "#demo" },
  ];

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-[#070b14]/90 backdrop-blur-md border-b border-slate-800/80 shadow-lg shadow-black/40 py-3"
          : "bg-transparent py-5"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between">
        {/* Brand Logo */}
        <Link href="/" className="flex items-center space-x-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-md shadow-cyan-500/20 group-hover:scale-105 transition-transform">
            <Waves className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg text-white tracking-tight group-hover:text-cyan-400 transition-colors">
                {PROJECT_METADATA.shortTitle}
              </span>
              <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full bg-cyan-950/80 text-cyan-400 border border-cyan-800/50">
                PyTorch SAR
              </span>
            </div>
            <p className="text-[11px] text-slate-400 hidden sm:block">
              Sen1Floods11 Semantic Segmentation
            </p>
          </div>
        </Link>

        {/* Desktop Nav Links */}
        <nav className="hidden lg:flex items-center space-x-1 xl:space-x-2">
          {navLinks.map((link) => (
            <Link
              key={link.name}
              href={link.href}
              className="text-xs xl:text-sm font-medium text-slate-300 hover:text-cyan-400 px-3 py-1.5 rounded-lg hover:bg-slate-800/50 transition-all"
            >
              {link.name}
            </Link>
          ))}
        </nav>

        {/* Action Buttons */}
        <div className="hidden sm:flex items-center space-x-3">
          <div className="flex items-center space-x-1.5 text-xs text-emerald-400 bg-emerald-950/40 border border-emerald-800/40 px-2.5 py-1.5 rounded-lg">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span className="font-semibold">39/39 Verified</span>
          </div>

          <a
            href={PROJECT_METADATA.streamlitUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-2 text-xs font-semibold text-white bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 px-4 py-2 rounded-lg shadow-md shadow-cyan-500/20 transition-all hover:scale-105"
          >
            <span>Launch Demo</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>

        {/* Mobile menu button */}
        <div className="flex items-center lg:hidden">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 focus:outline-none"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="lg:hidden bg-[#0a101d] border-b border-slate-800 px-4 pt-3 pb-6 space-y-2 mt-2">
          {navLinks.map((link) => (
            <Link
              key={link.name}
              href={link.href}
              onClick={() => setMobileMenuOpen(false)}
              className="block text-sm font-medium text-slate-300 hover:text-cyan-400 hover:bg-slate-800/60 px-3 py-2 rounded-md"
            >
              {link.name}
            </Link>
          ))}
          <div className="pt-4 border-t border-slate-800 flex flex-col space-y-3">
            <a
              href={PROJECT_METADATA.streamlitUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center space-x-2 text-sm font-semibold text-white bg-gradient-to-r from-cyan-500 to-blue-600 px-4 py-2.5 rounded-lg text-center"
            >
              <span>Launch Interactive Demo</span>
              <ExternalLink className="w-4 h-4" />
            </a>
          </div>
        </div>
      )}
    </header>
  );
}
