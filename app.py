"""
AI-Based Flood Detection and Mapping Using Satellite Imagery.

Interactive Streamlit Showcase Application for Sen1Floods11 Sentinel-1 SAR PyTorch U-Net.
Designed for Academic Presentations & College Viva.

Navigation:
1. Project Overview
2. Dataset
3. How the AI Works
4. Training
5. Evaluation
6. Flood Prediction
7. Live Demo
8. About / Limitations
"""

import os
import io
import sys
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List

# Ensure project root is in sys.path
PROJECT_ROOT = str(Path(__file__).resolve().parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import torch
import rasterio
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.patches as mpatches

from src.models.unet import build_unet, UNet
from src.data.preprocessing import FloodPreprocessor
from src.data.validation import discover_chips
from src.training.metrics import compute_confusion_matrix_elements
from src.utils.config_loader import get_device

# Color Maps for Visualizations
MASK_CMAP = ListedColormap(["#ECC94B", "#2D3748", "#3182CE"])  # -1: Invalid (Yellow), 0: Land (Dark Gray), 1: Water (Blue)
MASK_NORM = BoundaryNorm([-1.5, -0.5, 0.5, 1.5], MASK_CMAP.N)

PRED_CMAP = ListedColormap(["#2D3748", "#00D2FF"])  # 0: Land (Dark Gray), 1: Pred Water (Cyan)
PRED_NORM = BoundaryNorm([-0.5, 0.5, 1.5], PRED_CMAP.N)


@st.cache_resource
def load_cached_model(checkpoint_path: str = "checkpoints/best_s1.pt") -> Tuple[Optional[torch.nn.Module], str, Optional[str]]:
    """
    Loads and caches the trained U-Net checkpoint.
    Auto-detects MPS / CUDA / CPU.
    """
    device = get_device()
    if not os.path.exists(checkpoint_path):
        return None, device, f"Checkpoint not found at: `{checkpoint_path}`. Please verify the checkpoint file exists."

    try:
        checkpoint = torch.load(checkpoint_path, map_location=device)
        model = build_unet(modality="s1").to(device)
        model.load_state_dict(checkpoint["model_state_dict"])
        model.eval()
        return model, device, None
    except Exception as e:
        return None, device, f"Failed to load model from `{checkpoint_path}`: {str(e)}"


def create_sar_composite(vv_norm: np.ndarray, vh_norm: np.ndarray) -> np.ndarray:
    """
    Creates an RGB false-color SAR composite:
    Red = VV, Green = VH, Blue = VV / (VH + eps).
    """
    ratio = np.clip(vv_norm / (vh_norm + 1e-4), 0.0, 1.0)
    composite = np.stack([vv_norm, vh_norm, ratio], axis=-1)
    return composite


def render_prediction_figure(
    sar_composite: np.ndarray,
    pred_binary: np.ndarray,
    prob_map: np.ndarray,
    gt_mask: Optional[np.ndarray] = None,
    title: str = "Flood Segmentation Results",
) -> plt.Figure:
    """
    Renders side-by-side diagnostic panels:
    - Input SAR (VV, VH, Ratio)
    - Ground Truth (if available)
    - Predicted Flood
    - Prediction Overlay
    - Flood Probability Map
    """
    num_panels = 5 if gt_mask is not None else 4
    fig, axes = plt.subplots(1, num_panels, figsize=(4.2 * num_panels, 4.2), facecolor="#ffffff")
    if num_panels == 1:
        axes = [axes]

    # Panel 1: Input SAR
    axes[0].imshow(sar_composite)
    axes[0].set_title("Input SAR\n(VV, VH, Ratio)", fontsize=11, fontweight="bold", pad=8)
    axes[0].axis("off")

    idx = 1
    # Panel 2: Ground Truth (when available)
    if gt_mask is not None:
        axes[idx].imshow(gt_mask, cmap=MASK_CMAP, norm=MASK_NORM)
        axes[idx].set_title("Ground Truth\n(Hand-Labeled)", fontsize=11, fontweight="bold", pad=8)
        axes[idx].axis("off")
        gt_patches = [
            mpatches.Patch(color="#2D3748", label="Land (0)"),
            mpatches.Patch(color="#3182CE", label="Water (1)"),
            mpatches.Patch(color="#ECC94B", label="Invalid (-1)"),
        ]
        axes[idx].legend(handles=gt_patches, loc="lower right", fontsize=8, framealpha=0.85)
        idx += 1

    # Panel: Predicted Flood
    axes[idx].imshow(pred_binary, cmap=PRED_CMAP, norm=PRED_NORM)
    axes[idx].set_title("Predicted Flood\n(Binary Segmentation)", fontsize=11, fontweight="bold", pad=8)
    axes[idx].axis("off")
    pred_patches = [
        mpatches.Patch(color="#2D3748", label="Land (0)"),
        mpatches.Patch(color="#00D2FF", label="Pred Flood (1)"),
    ]
    axes[idx].legend(handles=pred_patches, loc="lower right", fontsize=8, framealpha=0.85)
    idx += 1

    # Panel: Prediction Overlay
    axes[idx].imshow(sar_composite)
    overlay = np.zeros((*sar_composite.shape[:2], 4), dtype=np.float32)
    overlay[pred_binary == 1] = [0.0, 0.85, 1.0, 0.65]  # Cyan overlay
    axes[idx].imshow(overlay)
    axes[idx].set_title("Prediction Overlay\n(SAR + AI Mask)", fontsize=11, fontweight="bold", pad=8)
    axes[idx].axis("off")
    idx += 1

    # Panel: Flood Probability Map
    im = axes[idx].imshow(prob_map, cmap="viridis", vmin=0.0, vmax=1.0)
    axes[idx].set_title("Flood Probability Map\n(Sigmoid Output)", fontsize=11, fontweight="bold", pad=8)
    axes[idx].axis("off")
    plt.colorbar(im, ax=axes[idx], fraction=0.046, pad=0.04)

    plt.tight_layout()
    return fig


def get_available_test_samples(data_dir: str = "data/samples", splits_dir: str = "data/raw/splits") -> Dict[str, Dict[str, str]]:
    """
    Discovers available test split samples with both S1 and Label GeoTIFFs.
    """
    all_discovered = discover_chips(data_dir)
    test_csv = os.path.join(splits_dir, "flood_test_data.csv")
    samples = {}

    if os.path.exists(test_csv):
        df = pd.read_csv(test_csv, header=None, names=["s1", "label"])
        for _, row in df.iterrows():
            stem = row["s1"].replace("_S1Hand.tif", "")
            if stem in all_discovered and "S1Hand" in all_discovered[stem] and "LabelHand" in all_discovered[stem]:
                samples[stem] = {
                    "s1": all_discovered[stem]["S1Hand"],
                    "label": all_discovered[stem]["LabelHand"],
                    "stem": stem,
                }

    # Fallback to all discovered S1 + Label pairs
    if not samples:
        for stem, layers in all_discovered.items():
            if "S1Hand" in layers and "LabelHand" in layers:
                samples[stem] = {
                    "s1": layers["S1Hand"],
                    "label": layers["LabelHand"],
                    "stem": stem,
                }

    return samples


def render_custom_css():
    """Injects high-quality academic theme styling for Streamlit."""
    st.markdown(
        """
        <style>
        /* Main background and font */
        .main {
            background-color: #F8FAFC;
        }

        /* Metric cards custom styling */
        div[data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 14px 18px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border-color: #CBD5E1;
        }
        div[data-testid="stMetricLabel"] {
            color: #475569 !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        div[data-testid="stMetricValue"] {
            color: #0F172A !important;
            font-weight: 700 !important;
            font-size: 26px !important;
        }

        /* Highlight cards */
        .card-box {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        .card-box-accent {
            background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
            border: 1px solid #BAE6FD;
            border-radius: 10px;
            padding: 18px 22px;
            margin-bottom: 16px;
        }
        .pipeline-card {
            background: #FFFFFF;
            border: 1px solid #CBD5E1;
            border-radius: 8px;
            padding: 12px 14px;
            text-align: center;
            font-weight: 600;
            font-size: 13px;
            color: #1E293B;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04);
            min-height: 70px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .pipeline-arrow {
            text-align: center;
            font-size: 20px;
            color: #0284C7;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .badge-pill {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 14px;
            font-size: 12px;
            font-weight: 600;
            margin-right: 6px;
        }
        .badge-blue { background: #DBEAFE; color: #1E40AF; }
        .badge-teal { background: #CCFBF1; color: #115E59; }
        .badge-green { background: #DCFCE7; color: #166534; }
        .badge-purple { background: #F3E8FF; color: #6B21A8; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_header():
    """Renders the top application header."""
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 50%, #0369A1 100%); padding: 24px 30px; border-radius: 12px; margin-bottom: 24px; color: white; box-shadow: 0 4px 16px rgba(15, 23, 42, 0.15);">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
                <div>
                    <span style="background: rgba(255,255,255,0.18); color: #E0F2FE; font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 20px; text-transform: uppercase; letter-spacing: 1px;">
                        Academic Research & Viva Showcase
                    </span>
                    <h1 style="margin: 8px 0 4px 0; font-size: 27px; color: #FFFFFF; font-weight: 800; letter-spacing: -0.5px;">
                        AI-Based Flood Detection and Mapping Using Satellite Imagery
                    </h1>
                    <p style="margin: 0; font-size: 15px; color: #BAE6FD; font-weight: 500;">
                        Sen1Floods11 • Sentinel-1 SAR • PyTorch U-Net • 90/90 Test Benchmark
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================================
# 1. PROJECT OVERVIEW PAGE
# =========================================================================
def render_page_overview():
    st.markdown("### 📌 Executive Summary & Verified Benchmarks")
    st.markdown(
        """
        This project implements an end-to-end Deep Learning semantic segmentation system for rapid, all-weather floodwater detection using **Sentinel-1 Synthetic Aperture Radar (SAR)** satellite imagery from the internationally recognized **Sen1Floods11** benchmark dataset.
        """
    )

    # Core KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Test IoU", "0.5548", help="Jaccard Index across all 90 official test chips (20,517,367 valid pixels)")
    with col2:
        st.metric("Test Dice / F1", "0.7137", help="Harmonic mean of precision and recall on the flood class")
    with col3:
        st.metric("Precision", "0.7717", help="True Positives / (True Positives + False Positives)")
    with col4:
        st.metric("Recall", "0.6637", help="True Positives / (True Positives + False Negatives)")

    # Additional cards
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric("Test Chips", "90 / 90", help="100% full official test split evaluated without omissions")
    with col6:
        st.metric("Valid Pixels", "20.5M", help="20,517,367 valid ground-truth hand-labeled pixels")
    with col7:
        st.metric("Model Parameters", "7.76M", help="7,760,257 trainable PyTorch U-Net parameters")
    with col8:
        st.metric("Unit Tests", "39 / 39", help="39/39 passing pytest test suite covering all modules")

    st.markdown("---")
    st.markdown("### 🛰️ End-to-End Processing Pipeline")
    st.markdown(
        "The automated pipeline processes raw satellite radar data through normalization, neural feature extraction, pixel segmentation, and nominal flooded area quantification:"
    )

    # Visual Pipeline Flow
    pipeline_steps = [
        ("🛰️ Satellite SAR", "Sentinel-1 Level-1 GRD C-Band Radar"),
        ("⚡ VV + VH Channels", "Dual-polarization dB backscatter"),
        ("📐 Normalization", "[-35, +5] dB clamped to [0, 1] range"),
        ("🔲 256×256 Tensor", "Spatial batch dimension (B, 2, 256, 256)"),
        ("🧠 PyTorch U-Net", "4-Stage Encoder-Decoder + GroupNorm"),
        ("🎯 Pixel Segmentation", "Dense pixel-level class assignment"),
        ("🗺️ Flood Probability Map", "Continuous Sigmoid probabilities [0.0, 1.0]"),
        ("🛡️ Flood Mask", "Binary thresholding at p ≥ 0.50"),
        ("📏 Nominal Flooded Area", "Approx. ~100 m² per detected pixel (EPSG:4326)"),
    ]

    # Display pipeline in 3 rows with arrows
    for i in range(0, len(pipeline_steps), 3):
        group = pipeline_steps[i:i+3]
        cols = st.columns(5)

        # Step 1
        with cols[0]:
            st.markdown(
                f"""
                <div class="pipeline-card">
                    <div><strong>{group[0][0]}</strong><br><span style="font-size:11px; color:#64748B;">{group[0][1]}</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Arrow 1
        with cols[1]:
            st.markdown('<div class="pipeline-arrow" style="height:70px;">➔</div>', unsafe_allow_html=True)

        # Step 2
        with cols[2]:
            st.markdown(
                f"""
                <div class="pipeline-card">
                    <div><strong>{group[1][0]}</strong><br><span style="font-size:11px; color:#64748B;">{group[1][1]}</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Arrow 2
        with cols[3]:
            st.markdown('<div class="pipeline-arrow" style="height:70px;">➔</div>', unsafe_allow_html=True)

        # Step 3
        with cols[4]:
            st.markdown(
                f"""
                <div class="pipeline-card">
                    <div><strong>{group[2][0]}</strong><br><span style="font-size:11px; color:#64748B;">{group[2][1]}</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if i + 3 < len(pipeline_steps):
            st.markdown('<div style="text-align:center; font-size:18px; color:#0284C7; margin: 4px 0;">⬇</div>', unsafe_allow_html=True)

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(
            """
            <div class="card-box">
                <h4 style="margin-top:0; color:#0F172A;">🌟 Why Synthetic Aperture Radar (SAR)?</h4>
                <ul style="color:#334155; font-size:14px; line-height:1.6;">
                    <li><strong>All-Weather Penetration:</strong> C-band microwaves (5.405 GHz) pass through dense monsoon clouds, storm fronts, and smoke.</li>
                    <li><strong>Day & Night Operational:</strong> Active sensor generates its own illumination, working 24/7 during emergency response.</li>
                    <li><strong>Physics of Water:</strong> Smooth open water acts as a specular reflector, bouncing radar pulses away from sensor, appearing dark in imagery (&lt; -18 dB).</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_b:
        st.markdown(
            """
            <div class="card-box">
                <h4 style="margin-top:0; color:#0F172A;">🔬 Deep Learning Semantic Segmentation</h4>
                <ul style="color:#334155; font-size:14px; line-height:1.6;">
                    <li><strong>Dense Pixel Delineation:</strong> Predicts land vs floodwater for every single 10m spatial pixel.</li>
                    <li><strong>Multi-Scale Context:</strong> Skip connections preserve crisp riverbanks, levees, and urban edges while deep bottleneck captures regional context.</li>
                    <li><strong>Group Normalization:</strong> Ensures training stability independent of batch size across diverse terrestrial biomes.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================================
# 2. DATASET PAGE
# =========================================================================
def render_page_dataset():
    st.markdown("### 🌐 Sen1Floods11 Benchmark Dataset")
    st.markdown(
        "Sen1Floods11 is an internationally recognized georeferenced dataset curated by Cloud to Street and published at IEEE CVPRW 2020. It covers **11 global flood events across 6 continents**."
    )

    # 1. Dataset Partition Breakdown
    col_s1, col_s2 = st.columns([1, 1])

    with col_s1:
        st.markdown("#### 📊 Hand-Labeled Benchmark Split Distribution")
        split_data = pd.DataFrame({
            "Split": ["Training Set", "Validation Set", "Official Test Set", "Bolivia Holdout"],
            "Chips": [252, 89, 90, 15],
            "GeoTIFF Files": [1008, 356, 360, 60],
            "Percentage": ["56.5%", "20.0%", "20.2%", "3.4%"],
        })
        st.dataframe(
            split_data,
            column_config={
                "Split": st.column_config.TextColumn("Split Partition"),
                "Chips": st.column_config.NumberColumn("Chip Count", format="%d chips"),
                "GeoTIFF Files": st.column_config.NumberColumn("GeoTIFF Files", format="%d files"),
                "Percentage": st.column_config.TextColumn("Proportion"),
            },
            hide_index=True,
            use_container_width=True,
        )

        # Horizontal Split Bar
        st.markdown(
            """
            <div style="background:#E2E8F0; height:24px; border-radius:12px; display:flex; overflow:hidden; margin: 10px 0;">
                <div style="background:#2563EB; width:56.5%; height:100%; display:flex; align-items:center; justify-content:center; color:white; font-size:11px; font-weight:bold;">Train (252)</div>
                <div style="background:#0D9488; width:20.0%; height:100%; display:flex; align-items:center; justify-content:center; color:white; font-size:11px; font-weight:bold;">Val (89)</div>
                <div style="background:#E11D48; width:20.2%; height:100%; display:flex; align-items:center; justify-content:center; color:white; font-size:11px; font-weight:bold;">Test (90)</div>
                <div style="background:#D97706; width:3.4%; height:100%; display:flex; align-items:center; justify-content:center; color:white; font-size:11px; font-weight:bold;">Bol (15)</div>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:11px; color:#64748B;">
                <span>🔵 Train: 252 (56.5%)</span>
                <span>🟢 Val: 89 (20.0%)</span>
                <span>🔴 Test: 90 (20.2%)</span>
                <span>🟡 Bolivia: 15 (3.4%)</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("🔒 Verified Mutual Exclusivity: **0 overlapping chips** between all dataset partitions.")

    with col_s2:
        st.markdown("#### ⚖️ Pixel Composition & Class Imbalance")
        pixel_data = pd.DataFrame({
            "Class": ["Water / Flood (1)", "Non-Water / Land (0)", "Invalid / No-Data (-1)"],
            "Pixel Count": [1828756, 8888253, 2128047],
            "Percentage of Total": ["14.24%", "69.19%", "16.57%"],
            "Role in Pipeline": ["Positive Training Class", "Negative Training Class", "Masked Out (Ignored in Loss)"]
        })
        st.dataframe(
            pixel_data,
            column_config={
                "Class": st.column_config.TextColumn("Class Label"),
                "Pixel Count": st.column_config.NumberColumn("Pixel Count", format="%d px"),
                "Percentage of Total": st.column_config.TextColumn("Total Share"),
                "Role in Pipeline": st.column_config.TextColumn("Handling"),
            },
            hide_index=True,
            use_container_width=True,
        )

        st.markdown(
            """
            <div class="card-box-accent">
                <div style="font-size:13px; color:#0369A1; font-weight:600;">CLASS IMBALANCE METRIC</div>
                <div style="font-size:22px; color:#0C4A6E; font-weight:800; margin: 4px 0;">4.86 : 1 (Land to Water Ratio)</div>
                <div style="font-size:12px; color:#0284C7;">Water represents only ~17.06% of valid pixels, necessitating Dice Loss to prevent standard background bias.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # 2. Satellite & Sensor Physics
    st.markdown("#### 🛰️ Satellite Sensor & Ground Truth Channels")
    col_sat1, col_sat2, col_sat3 = st.columns(3)

    with col_sat1:
        st.markdown(
            """
            <div class="card-box">
                <h5 style="color:#0F172A; margin-top:0;">⚡ Sentinel-1 SAR (VV Polarization)</h5>
                <p style="font-size:13px; color:#475569;">
                    <strong>Vertical Transmit / Vertical Receive</strong><br>
                    Dominant surface scattering mode. Calibrated decibel backscatter (dB) captures smooth water specular reflections.
                </p>
                <span class="badge-pill badge-blue">Input Channel 0</span>
                <span class="badge-pill badge-blue">[-35 dB, +5 dB]</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_sat2:
        st.markdown(
            """
            <div class="card-box">
                <h5 style="color:#0F172A; margin-top:0;">📡 Sentinel-1 SAR (VH Polarization)</h5>
                <p style="font-size:13px; color:#475569;">
                    <strong>Vertical Transmit / Horizontal Receive</strong><br>
                    Cross-polarization mode. Highly sensitive to volume scattering from vegetation, canopy textures, and rough surfaces.
                </p>
                <span class="badge-pill badge-teal">Input Channel 1</span>
                <span class="badge-pill badge-teal">[-35 dB, +5 dB]</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_sat3:
        st.markdown(
            """
            <div class="card-box">
                <h5 style="color:#0F172A; margin-top:0;">🏷️ Hand-Labeled Ground Truth</h5>
                <p style="font-size:13px; color:#475569;">
                    <strong>Human Expert Annotations</strong><br>
                    Tri-state masks created using high-resolution optical imagery and SAR validation:
                    <strong>0</strong>: Land, <strong>1</strong>: Water, <strong>-1</strong>: Invalid/Cloud.
                </p>
                <span class="badge-pill badge-green">Supervised Target</span>
                <span class="badge-pill badge-purple">Tri-State Mask</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Visual Example from Dataset
    st.markdown("#### 🖼️ Representative Dataset Chip Visualization (Ghana_103272)")
    example_path = "outputs/visualizations/dataset_samples/Ghana_103272_verification.png"
    if os.path.exists(example_path):
        st.image(example_path, caption="Sen1Floods11 Multi-Layer Alignment: SAR (VV, VH), Optical (RGB), JRC Baseline, and Hand-Labeled Ground Truth", use_container_width=True)
    else:
        st.info("Dataset sample visualization is available in outputs/visualizations/dataset_samples/.")


# =========================================================================
# 3. HOW THE AI WORKS PAGE
# =========================================================================
def render_page_ai_architecture():
    st.markdown("### 🧠 How the AI Works: U-Net Semantic Segmentation")
    st.markdown(
        """
        Unlike classification models that assign a single label to an entire image, our system performs **Dense Pixel-Level Semantic Segmentation**.
        The core neural network is a **PyTorch U-Net** featuring an encoder-decoder topology with skip connections and Group Normalization.
        """
    )

    # U-Net Architecture Block Diagram (SVG / Layout)
    st.markdown("#### 🏗️ Detailed U-Net Network Architecture")

    st.markdown(
        """
        <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:12px; padding:24px; margin-bottom:20px;">
            <div style="display:flex; justify-content:space-between; align-items:stretch; gap:12px; flex-wrap:nowrap; overflow-x:auto; padding-bottom:10px;">

                <!-- INPUT -->
                <div style="flex:1; min-width:130px; background:#F1F5F9; border-left:4px solid #3B82F6; padding:12px; border-radius:6px;">
                    <div style="font-size:11px; font-weight:700; color:#1E40AF; text-transform:uppercase;">Input Tensor</div>
                    <div style="font-size:15px; font-weight:800; color:#0F172A; margin:4px 0;">2 × 256 × 256</div>
                    <div style="font-size:11px; color:#64748B;">VV + VH SAR Normalized dB Backscatter</div>
                </div>

                <!-- ENCODER -->
                <div style="flex:2; min-width:200px; background:#EFF6FF; border-left:4px solid #2563EB; padding:12px; border-radius:6px;">
                    <div style="font-size:11px; font-weight:700; color:#1D4ED8; text-transform:uppercase;">Contracting Encoder</div>
                    <div style="font-size:12px; color:#1E293B; line-height:1.6; margin-top:4px;">
                        • <strong>Enc 1:</strong> 32 ch (256×256)<br>
                        • <strong>Enc 2:</strong> 64 ch (128×128)<br>
                        • <strong>Enc 3:</strong> 128 ch (64×64)<br>
                        • <strong>Enc 4:</strong> 256 ch (32×32)<br>
                        <span style="font-size:11px; color:#2563EB;">↓ MaxPool2d (2×2) + DoubleConv + GroupNorm</span>
                    </div>
                </div>

                <!-- SKIP CONNECTIONS -->
                <div style="flex:1; min-width:120px; background:#FAF5FF; border:1px dashed #A855F7; padding:12px; border-radius:6px; text-align:center; display:flex; flex-direction:column; justify-content:center;">
                    <div style="font-size:11px; font-weight:700; color:#7E22CE; text-transform:uppercase;">Skip Connections</div>
                    <div style="font-size:18px; color:#9333EA; font-weight:bold; margin:4px 0;">⇄</div>
                    <div style="font-size:10.5px; color:#6B21A8;">Transfers fine spatial boundaries to decoder</div>
                </div>

                <!-- BOTTLENECK -->
                <div style="flex:1.2; min-width:140px; background:#FEF3C7; border-left:4px solid #D97706; padding:12px; border-radius:6px;">
                    <div style="font-size:11px; font-weight:700; color:#B45309; text-transform:uppercase;">Bottleneck</div>
                    <div style="font-size:15px; font-weight:800; color:#92400E; margin:4px 0;">512 × 16 × 16</div>
                    <div style="font-size:11px; color:#78350F;">Deepest latent feature representation</div>
                </div>

                <!-- DECODER -->
                <div style="flex:2; min-width:200px; background:#F0FDF4; border-left:4px solid #16A34A; padding:12px; border-radius:6px;">
                    <div style="font-size:11px; font-weight:700; color:#15803D; text-transform:uppercase;">Expanding Decoder</div>
                    <div style="font-size:12px; color:#1E293B; line-height:1.6; margin-top:4px;">
                        • <strong>Dec 1:</strong> 256 ch (32×32)<br>
                        • <strong>Dec 2:</strong> 128 ch (64×64)<br>
                        • <strong>Dec 3:</strong> 64 ch (128×128)<br>
                        • <strong>Dec 4:</strong> 32 ch (256×256)<br>
                        <span style="font-size:11px; color:#16A34A;">↑ Bilinear Upsample + Concat Skip + DoubleConv</span>
                    </div>
                </div>

                <!-- OUTPUT -->
                <div style="flex:1; min-width:130px; background:#F8FAFC; border-left:4px solid #0EA5E9; padding:12px; border-radius:6px;">
                    <div style="font-size:11px; font-weight:700; color:#0369A1; text-transform:uppercase;">Output Mask</div>
                    <div style="font-size:15px; font-weight:800; color:#0F172A; margin:4px 0;">1 × 256 × 256</div>
                    <div style="font-size:11px; color:#64748B;">1×1 Conv → Sigmoid → [0, 1] Probability</div>
                </div>

            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4 Key Architectural Decisions
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        st.markdown(
            """
            <div class="card-box">
                <h5 style="color:#0F172A; margin-top:0;">🛡️ 1. Group Normalization (num_groups=8)</h5>
                <p style="font-size:13px; color:#475569;">
                    Standard BatchNorm computes statistics across batch dimensions, causing instability when training with small batch sizes ($B=2$ or $4$) due to GPU memory constraints. GroupNorm divides channels into 8 groups and normalizes within each sample independently of batch size.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="card-box">
                <h5 style="color:#0F172A; margin-top:0;">🔗 2. Direct Skip Connections</h5>
                <p style="font-size:13px; color:#475569;">
                    Deep convolutions downsample spatial dimensions, losing precise boundary locations. Skip connections concatenate early high-resolution feature maps directly with upsampled decoder layers, allowing the network to delineate narrow canals and road levees.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_k2:
        st.markdown(
            """
            <div class="card-box">
                <h5 style="color:#0F172A; margin-top:0;">📐 3. Bilinear Upsampling + Conv2d</h5>
                <p style="font-size:13px; color:#475569;">
                    Rather than using transposed convolutions (ConvTranspose2d) which frequently introduce checkerboard grid artifacts into geospatial masks, we employ bilinear upsampling followed by double convolutions with GELU activations.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="card-box">
                <h5 style="color:#0F172A; margin-top:0;">⚡ 4. 1×1 Output Projection Layer</h5>
                <p style="font-size:13px; color:#475569;">
                    The final expanding block's 32-channel representation is collapsed via a point-wise $1 \times 1$ convolution into a single continuous logit map per pixel, converted to probabilities through the element-wise Sigmoid function: $\\sigma(z) = \\frac{1}{1 + e^{-z}}$.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("#### 💡 In Simple Language: How the AI Decides")
    st.info(
        "**'The U-Net predicts a class for every single pixel.'** It does not just look at whether an individual pixel is dark. It evaluates multi-scale neighborhood patterns, comparing local texture contrast, radar polarization ratios (VV / VH), and geographic continuity before outputting a flood probability between 0.0 and 1.0."
    )


# =========================================================================
# 4. TRAINING PAGE
# =========================================================================
def render_page_training():
    st.markdown("### 📈 Training Process & Optimization")
    st.markdown(
        "The model was trained on the official Sen1Floods11 training split (252 chips) using a specialized loss formulation that handles class imbalance and invalid pixels."
    )

    # Compact Training Configuration Cards
    st.markdown("#### ⚙️ Training Hyperparameters")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Epochs", "5", help="Trained with early stopping patience = 8")
    with col2:
        st.metric("Batch Size", "2", help="Optimized for 256x256 multi-channel tensors")
    with col3:
        st.metric("Optimizer", "AdamW", help="Weight decay = 1e-4, Betas = (0.9, 0.999)")
    with col4:
        st.metric("Learning Rate", "0.0005", help="Cosine Annealing scheduler down to 1e-5")

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric("Loss Function", "BCE + Dice", help="0.5 * Masked BCE + 0.5 * Masked Dice")
    with col6:
        st.metric("Image Dimension", "256 × 256", help="Strided spatial subsampling")
    with col7:
        st.metric("Best Val IoU", "0.8255", help="Best validation split IoU at epoch 5")
    with col8:
        st.metric("Best Val Dice", "0.9044", help="Best validation split Dice / F1 at epoch 5")

    st.markdown("---")

    # Training Curves Visualizer
    st.markdown("#### 📊 Recorded Training & Validation Curves")
    col_tc1, col_tc2 = st.columns(2)

    loss_curve_path = "outputs/training/loss_curves/s1_loss_curve.png"
    metric_curve_path = "outputs/training/metric_curves/s1_metric_curve.png"

    with col_tc1:
        st.markdown("**📉 Loss Convergence (Train vs Validation Loss)**")
        if os.path.exists(loss_curve_path):
            st.image(loss_curve_path, caption="Combined BCE + Dice Loss convergence across training epochs", use_container_width=True)
        else:
            st.info("Loss curve artifact located in outputs/training/loss_curves/s1_loss_curve.png")

    with col_tc2:
        st.markdown("**📈 Metric Progression (Validation IoU & Dice)**")
        if os.path.exists(metric_curve_path):
            st.image(metric_curve_path, caption="Validation IoU and Dice metric progression across training epochs", use_container_width=True)
        else:
            st.info("Metric curve artifact located in outputs/training/metric_curves/s1_metric_curve.png")

    st.markdown("---")

    # Invalid Pixel Handling Explanation
    st.markdown("#### 🛡️ Domain-Specific Masked Loss Formulation")
    st.markdown(
        """
        <div class="card-box">
            <h5 style="color:#0F172A; margin-top:0;">🚫 'Invalid Pixels (-1) are dynamically ignored during training'</h5>
            <p style="font-size:13.5px; color:#334155; line-height:1.6;">
                In satellite remote sensing benchmarks, ground-truth rasters contain unverified areas, cloud shadows, or sensor edge artifacts coded as <code>-1</code>.
                Standard loss functions would treat these as active targets, corrupting weight gradients.
            </p>
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:12px; border-radius:6px; font-family:monospace; font-size:13px; color:#0F172A; margin: 8px 0;">
                valid_mask = (target != -1)<br>
                loss_bce = F.binary_cross_entropy_with_logits(logits[valid_mask], target[valid_mask])<br>
                loss_dice = 1.0 - (2 * (probs[valid_mask] * target[valid_mask]).sum() + eps) / ((probs[valid_mask] + target[valid_mask]).sum() + eps)<br>
                total_loss = 0.5 * loss_bce + 0.5 * loss_dice
            </div>
            <p style="font-size:13px; color:#64748B; margin-bottom:0;">
                ✅ <strong>Zero Gradient Leakage:</strong> Unannotated pixels contribute zero loss and zero backpropagation error.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================================
# 5. EVALUATION PAGE
# =========================================================================
def render_page_evaluation():
    st.markdown("### 🏆 Rigorous Evaluation on Official 90-Chip Test Partition")
    st.markdown(
        "The model was audited and evaluated across **100% of the official Sen1Floods11 test split** (`flood_test_data.csv`). A total of **20,517,367 valid hand-labeled pixels** were evaluated."
    )

    # 5 Verified Metric Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Test IoU", "0.5548", help="Intersection over Union (Jaccard Index) on the floodwater class")
    with col2:
        st.metric("Test Dice / F1", "0.7137", help="Harmonic mean of precision and recall on floodwater")
    with col3:
        st.metric("Precision", "0.7717", help="77.17% of predicted flood pixels are true standing water")
    with col4:
        st.metric("Recall", "0.6637", help="66.37% of all ground-truth floodwater was successfully detected")
    with col5:
        st.metric("Accuracy", "0.9334", help="93.34% overall pixel classification accuracy")

    st.markdown("---")

    # Confusion Matrix & Heatmap
    col_cm1, col_cm2 = st.columns([1.1, 0.9])

    with col_cm1:
        st.markdown("#### 🔢 Pixel-Level Confusion Matrix (20.5M Valid Pixels)")

        # Render clean visual confusion matrix table
        st.markdown(
            """
            <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:10px; padding:18px; margin-bottom:14px;">
                <div style="text-align:center; font-weight:700; color:#475569; font-size:13px; margin-bottom:8px;">
                    REFERENCE GROUND TRUTH
                </div>
                <div style="display:flex; gap:10px;">
                    <div style="writing-mode:vertical-rl; transform:rotate(180deg); text-align:center; font-weight:700; color:#475569; font-size:13px; display:flex; align-items:center; justify-content:center;">
                        PREDICTED AI
                    </div>
                    <div style="flex:1;">
                        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                            <!-- TP -->
                            <div style="background:#DCFCE7; border:2px solid #22C55E; border-radius:8px; padding:14px; text-align:center;">
                                <div style="font-size:11px; font-weight:700; color:#15803D;">TRUE POSITIVES (TP)</div>
                                <div style="font-size:22px; font-weight:800; color:#14532D; margin:4px 0;">1,703,186 px</div>
                                <div style="font-size:11px; color:#166534;">Correctly Identified Flood</div>
                            </div>
                            <!-- FP -->
                            <div style="background:#FEE2E2; border:2px solid #EF4444; border-radius:8px; padding:14px; text-align:center;">
                                <div style="font-size:11px; font-weight:700; color:#B91C1C;">FALSE POSITIVES (FP)</div>
                                <div style="font-size:22px; font-weight:800; color:#7F1D1D; margin:4px 0;">503,818 px</div>
                                <div style="font-size:11px; color:#991B1B;">Dry Land Misclassified as Flood</div>
                            </div>
                            <!-- FN -->
                            <div style="background:#FEF3C7; border:2px solid #F59E0B; border-radius:8px; padding:14px; text-align:center;">
                                <div style="font-size:11px; font-weight:700; color:#B45309;">FALSE NEGATIVES (FN)</div>
                                <div style="font-size:22px; font-weight:800; color:#78350F; margin:4px 0;">862,915 px</div>
                                <div style="font-size:11px; color:#92400E;">Unidentified Floodwater</div>
                            </div>
                            <!-- TN -->
                            <div style="background:#F1F5F9; border:2px solid #94A3B8; border-radius:8px; padding:14px; text-align:center;">
                                <div style="font-size:11px; font-weight:700; color:#475569;">TRUE NEGATIVES (TN)</div>
                                <div style="font-size:22px; font-weight:800; color:#0F172A; margin:4px 0;">17,447,448 px</div>
                                <div style="font-size:11px; color:#334155;">Correctly Identified Dry Land</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_cm2:
        st.markdown("#### 📊 Final Test Metric Breakdown")

        # Native Streamlit / Altair chart of the 5 metrics
        chart_df = pd.DataFrame({
            "Metric": ["Accuracy", "Precision", "Dice / F1", "Recall", "IoU (Jaccard)"],
            "Score": [0.9334, 0.7717, 0.7137, 0.6637, 0.5548]
        })
        st.bar_chart(chart_df.set_index("Metric"), color="#0284C7", use_container_width=True)

    st.markdown("---")

    # Mathematical Definitions & Viva Reference
    st.markdown("#### 📐 Mathematical Formulas & Metric Clarifications")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown(
            r"""
            **Intersection over Union (IoU / Jaccard Index):**
            $$\text{IoU} = \frac{\text{TP}}{\text{TP} + \text{FP} + \text{FN}} = \frac{1,703,186}{1,703,186 + 503,818 + 862,915} = \mathbf{0.5548}$$

            *Penalizes both false alarms and missed detections strictly without credit for true negative land.*
            """
        )
    with col_m2:
        st.markdown(
            r"""
            **Dice Coefficient / F1 Score:**
            $$\text{Dice} = \frac{2 \cdot \text{TP}}{2 \cdot \text{TP} + \text{FP} + \text{FN}} = \frac{2 \times 1,703,186}{3,406,372 + 503,818 + 862,915} = \mathbf{0.7137}$$

            *The harmonic mean of Precision ($0.7717$) and Recall ($0.6637$). Mathematically identical to pixel F1.*
            """
        )


# =========================================================================
# 6. FLOOD PREDICTION PAGE (Representative Gallery)
# =========================================================================
def render_page_prediction_gallery():
    st.markdown("### 🖼️ Representative Prediction Gallery")
    st.markdown(
        "To provide a transparent, scientifically honest assessment of model strengths and limitations across global biomes, we present three representative test cases from the official test split."
    )

    # 1. Good Prediction
    st.markdown(
        """
        <div class="card-box" style="border-left: 5px solid #22C55E;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                <h4 style="margin:0; color:#15803D;">🌟 Case 1: High-Performance Prediction — USA_905409</h4>
                <span class="badge-pill badge-green">IoU: 0.9350 | Dice: 0.9664</span>
            </div>
            <p style="margin:6px 0 0 0; font-size:13.5px; color:#334155;">
                <strong>Geographic Region:</strong> United States • Open agricultural floodplains with calm standing water.<br>
                <strong>Metrics:</strong> IoU = <strong>0.9350</strong> | Dice / F1 = <strong>0.9664</strong> | Precision = <strong>0.9720</strong> | Recall = <strong>0.9609</strong><br>
                <strong>Flood Extent:</strong> Ground Truth: 44,467 px (~4.447 km²) | AI Detected: 43,959 px (~4.396 km²)
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    good_img = "outputs/visualizations/final_test/1_good_prediction_USA_905409.png"
    if os.path.exists(good_img):
        st.image(good_img, caption="USA_905409: SAR (VV, VH, Ratio), Ground Truth, Predicted Mask, Prediction Overlay, Flood Probability Map", use_container_width=True)

    st.markdown("---")

    # 2. Average Prediction
    st.markdown(
        """
        <div class="card-box" style="border-left: 5px solid #0284C7;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                <h4 style="margin:0; color:#0369A1;">⚖️ Case 2: Average Prediction — Pakistan_694942</h4>
                <span class="badge-pill badge-blue">IoU: 0.3829 | Dice: 0.5538</span>
            </div>
            <p style="margin:6px 0 0 0; font-size:13.5px; color:#334155;">
                <strong>Geographic Region:</strong> Pakistan • Complex river delta with dense irrigation canals and saturated soil.<br>
                <strong>Metrics:</strong> IoU = <strong>0.3829</strong> | Dice / F1 = <strong>0.5538</strong> | Precision = <strong>0.4152</strong> | Recall = <strong>0.8313</strong><br>
                <strong>Flood Extent:</strong> Ground Truth: 18,481 px (~1.848 km²) | AI Detected: 37,006 px (~3.701 km²)
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    avg_img = "outputs/visualizations/final_test/2_average_prediction_Pakistan_694942.png"
    if os.path.exists(avg_img):
        st.image(avg_img, caption="Pakistan_694942: High recall (83.13%) captures primary floodwaters, with moderate false alarms from waterlogged soil", use_container_width=True)

    st.markdown("---")

    # 3. Difficult Prediction
    st.markdown(
        """
        <div class="card-box" style="border-left: 5px solid #E11D48;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                <h4 style="margin:0; color:#BE123C;">⚠️ Case 3: Difficult Challenge — Sri-Lanka_450918</h4>
                <span class="badge-pill badge-purple">IoU: 0.0086 | Dice: 0.0171</span>
            </div>
            <p style="margin:6px 0 0 0; font-size:13.5px; color:#334155;">
                <strong>Geographic Region:</strong> Sri Lanka • Dense tropical rainforest canopy and mountainous terrain.<br>
                <strong>Metrics:</strong> IoU = <strong>0.0086</strong> | Dice / F1 = <strong>0.0171</strong> | Precision = <strong>0.2317</strong> | Recall = <strong>0.0089</strong><br>
                <strong>Radar Physics Reason:</strong> Dense vegetation canopy prevents C-band radar from reaching sub-canopy floodwater, causing radar backscatter double-bounce.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    diff_img = "outputs/visualizations/final_test/3_difficult_prediction_Sri-Lanka_450918.png"
    if os.path.exists(diff_img):
        st.image(diff_img, caption="Sri-Lanka_450918: Documented limitation where thick vegetation attenuates microwave backscatter", use_container_width=True)


# =========================================================================
# 7. LIVE DEMO PAGE
# =========================================================================
def render_page_live_demo(model: torch.nn.Module, device: str):
    st.markdown("### 🧪 Interactive Live Inference & Area Quantification")
    st.markdown(
        "Run real-time forward inference using either an official benchmark test chip or your own uploaded dual-polarization Sentinel-1 GeoTIFF."
    )

    demo_mode = st.radio(
        "Choose Live Demo Source:",
        ["Mode A: Benchmark Test Sample (Official Split)", "Mode B: Upload Custom SAR GeoTIFF"],
        horizontal=True,
    )

    col_ctrl1, col_ctrl2 = st.columns([1, 1])
    with col_ctrl1:
        prob_threshold = st.slider(
            "Water Detection Threshold (Probability cutoff):",
            min_value=0.1,
            max_value=0.9,
            value=0.5,
            step=0.05,
            help="Threshold for classifying a pixel as floodwater (default: 0.50).",
        )
    with col_ctrl2:
        st.markdown(
            f"""
            <div style="background:#F1F5F9; border:1px solid #CBD5E1; padding:10px 14px; border-radius:8px; font-size:12.5px; margin-top:14px;">
                <strong>Runtime Engine:</strong> Device = <code>{device.upper()}</code> | Resolution = <code>256×256</code> | Model = <code>PyTorch U-Net (2→1)</code>
            </div>
            """,
            unsafe_allow_html=True,
        )

    preprocessor = FloodPreprocessor()

    # =========================================================================
    # MODE A: BENCHMARK TEST SAMPLE
    # =========================================================================
    if demo_mode == "Mode A: Benchmark Test Sample (Official Split)":
        st.markdown("#### 📂 Select Official Benchmark Test Chip")
        available_samples = get_available_test_samples()
        if not available_samples:
            st.error("No test samples found in `data/samples/` matching `data/raw/splits/flood_test_data.csv`.")
            return

        sample_keys = sorted(list(available_samples.keys()))
        selected_stem = st.selectbox(
            "Select an official test chip:",
            sample_keys,
            index=0,
            help="Choose from available official test chips.",
        )

        sample_info = available_samples[selected_stem]

        # Load GeoTIFF
        try:
            with rasterio.open(sample_info["s1"]) as src:
                raw_s1 = src.read()
            with rasterio.open(sample_info["label"]) as src:
                raw_mask = src.read()
        except Exception as e:
            st.error(f"Error reading GeoTIFF files for {selected_stem}: {str(e)}")
            return

        # Preprocess & Subsample to 256x256
        norm_s1 = preprocessor.normalize_s1(raw_s1)
        proc_mask = preprocessor.process_mask(raw_mask)

        stride_h = max(1, norm_s1.shape[1] // 256)
        stride_w = max(1, norm_s1.shape[2] // 256)
        input_s1 = norm_s1[:, ::stride_h, ::stride_w][:, :256, :256]
        input_mask = proc_mask[::stride_h, ::stride_w][:256, :256]

        # Forward Inference
        img_tensor = torch.from_numpy(input_s1).unsqueeze(0).float().to(device)
        with torch.no_grad():
            logits = model(img_tensor)
            probs = torch.sigmoid(logits).squeeze().cpu().numpy()
            pred_binary = (probs >= prob_threshold).astype(np.int64)

        # Quantitative Metrics (Valid Pixels Only)
        valid_mask = input_mask != -1
        valid_pixels = int(np.sum(valid_mask))
        water_gt_pixels = int(np.sum(input_mask == 1))
        pred_water_pixels = int(np.sum((pred_binary == 1) & valid_mask))

        tp = int(np.sum((pred_binary == 1) & (input_mask == 1) & valid_mask))
        fp = int(np.sum((pred_binary == 1) & (input_mask == 0) & valid_mask))
        fn = int(np.sum((pred_binary == 0) & (input_mask == 1) & valid_mask))
        tn = int(np.sum((pred_binary == 0) & (input_mask == 0) & valid_mask))

        chip_iou = tp / max(1, tp + fp + fn) if (tp + fp + fn) > 0 else (1.0 if water_gt_pixels == 0 else 0.0)
        chip_dice = (2.0 * tp) / max(1, 2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else (1.0 if water_gt_pixels == 0 else 0.0)
        chip_prec = tp / max(1, tp + fp) if (tp + fp) > 0 else 0.0
        chip_rec = tp / max(1, tp + fn) if (tp + fn) > 0 else 0.0

        # Nominal Geospatial Area Calculation
        nominal_area_km2 = pred_water_pixels * (10.0 * 10.0) / 1e6
        gt_area_km2 = water_gt_pixels * (10.0 * 10.0) / 1e6
        coverage_pct = (pred_water_pixels / max(1, valid_pixels)) * 100.0

        # Render Multi-Panel Diagnostic Figure
        st.markdown("#### 🖼️ Multi-Panel Diagnostic Visualization")
        sar_rgb = create_sar_composite(input_s1[0], input_s1[1])
        fig = render_prediction_figure(
            sar_composite=sar_rgb,
            pred_binary=pred_binary,
            prob_map=probs,
            gt_mask=input_mask,
            title=f"Sample: {selected_stem}",
        )
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

        # Nominal Flooded Area & Extent Quantification Card
        st.markdown("#### 📏 Flood Extent & Nominal Area Quantification")
        col_q1, col_q2, col_q3 = st.columns(3)
        with col_q1:
            st.metric("Detected Flood Pixels", f"{pred_water_pixels:,} px", f"GT: {water_gt_pixels:,} px")
        with col_q2:
            st.metric("Flood Coverage", f"{coverage_pct:.2f}%", f"GT: {(water_gt_pixels / max(1, valid_pixels))*100:.2f}%")
        with col_q3:
            st.metric("NOMINAL FLOODED AREA", f"~{nominal_area_km2:.3f} km²", f"GT: ~{gt_area_km2:.3f} km²")

        # Metric Details & Confusion Table
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("##### 🎯 Chip Segmentation Metrics")
            st.markdown(
                f"""
                | Metric | Score | Definition |
                | :--- | :---: | :--- |
                | **IoU (Jaccard)** | **{chip_iou:.4f}** | $\\text{{TP}} / (\\text{{TP}} + \\text{{FP}} + \\text{{FN}})$ |
                | **Dice / F1** | **{chip_dice:.4f}** | $2\\text{{TP}} / (2\\text{{TP}} + \\text{{FP}} + \\text{{FN}})$ |
                | **Precision** | **{chip_prec:.4f}** | $\\text{{TP}} / (\\text{{TP}} + \\text{{FP}})$ |
                | **Recall** | **{chip_rec:.4f}** | $\\text{{TP}} / (\\text{{TP}} + \\text{{FN}})$ |
                """
            )
        with col_t2:
            st.markdown("##### 🔢 Confusion Matrix Breakdown")
            st.markdown(
                f"""
                | Element | Count | Description |
                | :--- | :---: | :--- |
                | **True Positives (TP)** | `{tp:,}` px | Correctly identified floodwater |
                | **False Positives (FP)** | `{fp:,}` px | Dry land misclassified as water |
                | **False Negatives (FN)** | `{fn:,}` px | Unidentified floodwater pixels |
                | **True Negatives (TN)** | `{tn:,}` px | Correctly identified dry land |
                """
            )

    # =========================================================================
    # MODE B: UPLOAD SAR GEOTIFF
    # =========================================================================
    else:
        st.markdown("#### 📤 Upload Dual-Polarization Sentinel-1 SAR GeoTIFF")
        st.markdown(
            "Upload a custom Sentinel-1 GeoTIFF raster with at least 2 channels ($VV$ and $VH$ in calibrated decibels)."
        )

        uploaded_file = st.file_uploader(
            "Choose a GeoTIFF raster file (.tif, .tiff):",
            type=["tif", "tiff"],
            help="Upload a GeoTIFF image with channel 0 = VV dB and channel 1 = VH dB.",
        )

        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            try:
                with rasterio.open(io.BytesIO(file_bytes)) as src:
                    raw_data = src.read()
                    num_channels, height, width = raw_data.shape
            except Exception as e:
                st.error(f"❌ Corrupt or unreadable GeoTIFF file: {str(e)}")
                return

            if num_channels < 2:
                st.error(f"❌ Invalid Channel Count: Expected at least 2 channels (VV, VH), but found {num_channels}.")
                return

            st.success(f"✅ Loaded GeoTIFF: `{uploaded_file.name}` | Shape: `{raw_data.shape}` ({num_channels} bands, {height}×{width})")

            # Preprocess S1 (take first 2 channels: VV, VH)
            s1_raw = raw_data[:2]
            norm_s1 = preprocessor.normalize_s1(s1_raw)

            stride_h = max(1, height // 256)
            stride_w = max(1, width // 256)
            input_s1 = norm_s1[:, ::stride_h, ::stride_w][:, :256, :256]

            # Forward Inference
            img_tensor = torch.from_numpy(input_s1).unsqueeze(0).float().to(device)
            with torch.no_grad():
                logits = model(img_tensor)
                probs = torch.sigmoid(logits).squeeze().cpu().numpy()
                pred_binary = (probs >= prob_threshold).astype(np.int64)

            # Quantifications
            total_pixels = int(pred_binary.size)
            pred_water_pixels = int(np.sum(pred_binary == 1))
            coverage_pct = (pred_water_pixels / max(1, total_pixels)) * 100.0
            nominal_area_km2 = pred_water_pixels * (10.0 * 10.0) / 1e6

            # Visualizations
            st.markdown("#### 🖼️ Model Inference Diagnostics")
            sar_rgb = create_sar_composite(input_s1[0], input_s1[1])
            fig = render_prediction_figure(
                sar_composite=sar_rgb,
                pred_binary=pred_binary,
                prob_map=probs,
                gt_mask=None,
                title=f"Uploaded SAR: {uploaded_file.name}",
            )
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

            # Results Section
            st.markdown("#### 📏 Flood Extent & Nominal Area Quantification")
            col_u1, col_u2, col_u3 = st.columns(3)
            with col_u1:
                st.metric("Detected Flood Pixels", f"{pred_water_pixels:,} px")
            with col_u2:
                st.metric("Flood Coverage", f"{coverage_pct:.2f}%")
            with col_u3:
                st.metric("NOMINAL FLOODED AREA", f"~{nominal_area_km2:.3f} km²")

            st.info("ℹ️ **Scientific Notice:** Ground-truth metrics (IoU, Dice, Precision, Recall) are omitted because reference annotations are unavailable for user-uploaded rasters.")

    # Geospatial Caveat Box (Always Visible)
    st.markdown("---")
    st.markdown(
        """
        <div style="background:#FFFBEB; border-left:4px solid #F59E0B; padding:12px 16px; border-radius:6px;">
            <div style="font-size:13px; font-weight:700; color:#B45309;">🗺️ Geospatial Resolution Caveat for Nominal Area</div>
            <div style="font-size:12px; color:#78350F; margin-top:4px;">
                Raw coordinates are in WGS84 (<code>EPSG:4326</code>, ~8.98×10⁻⁵ degrees). Physical ground resolution varies with latitude as <code>10m × cos(latitude)</code>.
                Reported km² values are documented <strong>nominal approximations</strong> based on equatorial 100 m²/pixel scaling.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================================
# 8. ABOUT & LIMITATIONS PAGE
# =========================================================================
def render_page_about_limitations():
    st.markdown("### ℹ️ About the Project & Scientific Limitations")

    # 1. Scientific Limitations Panel
    st.markdown("#### ⚠️ Documented Scientific & Physical Limitations")

    col_l1, col_l2 = st.columns(2)
    with col_l1:
        st.markdown(
            """
            <div class="card-box">
                <h5 style="color:#0F172A; margin-top:0;">🏙️ 1. False Positives: Smooth Terrestrial Surfaces</h5>
                <p style="font-size:13px; color:#475569;">
                    Calm open water produces low radar backscatter due to specular reflection. However, dry smooth surfaces (airport runways, flat asphalt highways, dry playas/salt flats) also reflect radar signals away, occasionally generating false positive flood detections.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="card-box">
                <h5 style="color:#0F172A; margin-top:0;">🌲 2. False Negatives: Vegetation & Urban Double-Bounce</h5>
                <p style="font-size:13px; color:#475569;">
                    When floodwaters inundate dense forests or urban corridors, radar pulses experience double-bounce reflections between vertical tree trunks/buildings and water, returning high backscatter rather than dark pixels, causing false negatives.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_l2:
        st.markdown(
            """
            <div class="card-box">
                <h5 style="color:#0F172A; margin-top:0;">☁️ 3. Invalid/No-Data Masking</h5>
                <p style="font-size:13px; color:#475569;">
                    Optical ground truth labels in Sen1Floods11 contain cloud masks and unannotated regions (-1). While the training loss ignores them via dynamic masking, evaluating real-world scenes requires accounting for sensor boundaries.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="card-box">
                <h5 style="color:#0F172A; margin-top:0;">🌊 4. Baseline Reference (JRC Global Surface Water)</h5>
                <p style="font-size:13px; color:#475569;">
                    Sen1Floods11 does not contain separate pre-flood SAR acquisitions. Historical water baseline is derived from the JRC 30-year Global Surface Water permanence layer. Nominal flooded areas represent rapid assessments and should not be used as operational emergency commands.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # 2. Technology Stack & Software Engineering Quality
    st.markdown("#### 🛠️ Technology Stack & Verification Rigor")

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown(
            """
            <div class="card-box">
                <h5 style="color:#0F172A; margin-top:0;">💻 Core Technology Stack</h5>
                <ul style="font-size:13.5px; color:#334155; line-height:1.7;">
                    <li><strong>Language:</strong> Python 3.11</li>
                    <li><strong>Deep Learning:</strong> PyTorch 2.14, Torchvision</li>
                    <li><strong>Geospatial Processing:</strong> Rasterio, GDAL / Affine</li>
                    <li><strong>Scientific Computing:</strong> NumPy, Pandas, Scipy</li>
                    <li><strong>Computer Vision:</strong> OpenCV, Matplotlib</li>
                    <li><strong>Web Interface:</strong> Streamlit 1.64</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_t2:
        st.markdown(
            """
            <div class="card-box">
                <h5 style="color:#0F172A; margin-top:0;">🧪 Software Quality & Verification</h5>
                <ul style="font-size:13.5px; color:#334155; line-height:1.7;">
                    <li><strong>Test Suite:</strong> <code>39/39 Unit Tests Passing</code> (100%)</li>
                    <li><strong>Data Leakage:</strong> <code>0 overlapping chips</code> strictly verified</li>
                    <li><strong>Benchmark Coverage:</strong> <code>90/90 official test chips</code> (20.5M valid pixels)</li>
                    <li><strong>Model Checkpoint:</strong> <code>best_s1.pt</code> (7,760,257 parameters)</li>
                    <li><strong>Deterministic Seeding:</strong> Seed 42 across all training splits</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================================
# MAIN ROUTING
# =========================================================================
def main():
    st.set_page_config(
        page_title="AI Flood Detection & Mapping",
        page_icon="🛰️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    render_custom_css()
    show_header()

    # Load Model
    model, device, load_err = load_cached_model()
    if load_err:
        st.error(f"⚠️ {load_err}")
        st.stop()

    # Sidebar Navigation
    st.sidebar.markdown("### 🧭 Navigation")
    pages = [
        "1. Project Overview",
        "2. Dataset",
        "3. How the AI Works",
        "4. Training",
        "5. Evaluation",
        "6. Flood Prediction",
        "7. Live Demo",
        "8. About / Limitations",
    ]
    selected_page = st.sidebar.radio("Go to Page:", pages, index=0)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ System Specifications")
    st.sidebar.markdown(f"- **Device:** `{device.upper()}`")
    st.sidebar.markdown("- **Dataset:** `Sen1Floods11`")
    st.sidebar.markdown("- **Satellite:** `Sentinel-1 SAR`")
    st.sidebar.markdown("- **Model:** `PyTorch U-Net`")
    st.sidebar.markdown("- **Input Size:** `256 × 256`")
    st.sidebar.markdown("- **Parameters:** `7,760,257`")
    st.sidebar.markdown("- **Test IoU:** `0.5548`")
    st.sidebar.markdown("- **Test Dice/F1:** `0.7137`")
    st.sidebar.markdown("- **Unit Tests:** `39/39 Passing`")

    st.sidebar.markdown("---")
    st.sidebar.caption("© 2026 AI Flood Detection Project • Academic Showcase")

    # Route Pages
    if selected_page == "1. Project Overview":
        render_page_overview()
    elif selected_page == "2. Dataset":
        render_page_dataset()
    elif selected_page == "3. How the AI Works":
        render_page_ai_architecture()
    elif selected_page == "4. Training":
        render_page_training()
    elif selected_page == "5. Evaluation":
        render_page_evaluation()
    elif selected_page == "6. Flood Prediction":
        render_page_prediction_gallery()
    elif selected_page == "7. Live Demo":
        render_page_live_demo(model, device)
    elif selected_page == "8. About / Limitations":
        render_page_about_limitations()


if __name__ == "__main__":
    main()
