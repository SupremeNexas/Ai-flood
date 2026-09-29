"""
Sen1Floods11 Multi-Modal Dataset Visualization Module.

Generates high-resolution multi-panel figures for visual inspection and quality verification,
displaying SAR VV/VH, Optical RGB, Pre-flood JRC Water Baseline, and Ground Truth Masks.
"""

import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import glob
import argparse
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.patches as mpatches
from typing import List, Optional

from src.data.preprocessing import FloodPreprocessor


# Publication-grade colormaps
MASK_CMAP = ListedColormap(["#f6e05e", "#2d3748", "#3182ce"])  # -1: Yellow (Invalid), 0: Dark Grey (Land), 1: Bright Blue (Water)
MASK_NORM = BoundaryNorm([-1.5, -0.5, 0.5, 1.5], MASK_CMAP.N)

JRC_CMAP = ListedColormap(["#2d3748", "#4299e1"])  # 0: Land, 1: Permanent Water
JRC_NORM = BoundaryNorm([-0.5, 0.5, 1.5], JRC_CMAP.N)


def plot_single_sample(
    stem: str,
    data_dir: str,
    output_path: str,
    preprocessor: Optional[FloodPreprocessor] = None,
) -> bool:
    """
    Renders a comprehensive 6-panel verification figure for a single chip stem.
    """
    pre = preprocessor or FloodPreprocessor()

    s1_path = os.path.join(data_dir, "S1Hand", f"{stem}_S1Hand.tif")
    s2_path = os.path.join(data_dir, "S2Hand", f"{stem}_S2Hand.tif")
    label_path = os.path.join(data_dir, "LabelHand", f"{stem}_LabelHand.tif")
    jrc_path = os.path.join(data_dir, "JRCWaterHand", f"{stem}_JRCWaterHand.tif")

    if not (os.path.exists(s1_path) and os.path.exists(label_path)):
        print(f"Skipping {stem}: missing required S1 or Label file.")
        return False

    # Load S1 SAR
    with rasterio.open(s1_path) as src:
        raw_s1 = src.read()
    norm_s1 = pre.normalize_s1(raw_s1)
    vv = norm_s1[0]
    vh = norm_s1[1]

    # Load S2 Optical
    has_s2 = os.path.exists(s2_path)
    if has_s2:
        with rasterio.open(s2_path) as src:
            raw_s2 = src.read()
        s2_rgb = pre.extract_s2_rgb(raw_s2)
        # Transpose to (H, W, 3) for matplotlib
        rgb_disp = np.transpose(s2_rgb, (1, 2, 0))
    else:
        rgb_disp = np.zeros((512, 512, 3), dtype=np.float32)

    # Load JRC Baseline
    has_jrc = os.path.exists(jrc_path)
    if has_jrc:
        with rasterio.open(jrc_path) as src:
            jrc_raw = src.read(1)
        jrc_mask = pre.normalize_jrc(jrc_raw)[0]
    else:
        jrc_mask = np.zeros((512, 512), dtype=np.float32)

    # Load Label
    with rasterio.open(label_path) as src:
        raw_label = src.read(1)
    label_mask = pre.process_mask(raw_label)

    # Calculate statistics
    valid_px = int((label_mask != -1).sum())
    water_px = int((label_mask == 1).sum())
    land_px = int((label_mask == 0).sum())
    invalid_px = int((label_mask == -1).sum())
    flood_ratio = (water_px / valid_px * 100) if valid_px > 0 else 0.0
    area_km2 = water_px * 0.0001  # 10m x 10m = 100 m2 = 0.0001 km2

    # Create figure
    fig, axes = plt.subplots(2, 3, figsize=(18, 12), facecolor="#ffffff")
    event_name = stem.split("_")[0]
    fig.suptitle(
        f"Sen1Floods11 Chip Verification: {stem} (Event: {event_name})\n"
        f"Water Extent: {water_px:,} px ({flood_ratio:.2f}% coverage | ~{area_km2:.2f} km²) | Valid Pixels: {valid_px:,} | Invalid: {invalid_px:,}",
        fontsize=15,
        fontweight="bold",
        y=0.98,
    )

    # Panel 1: S1 SAR VV
    im1 = axes[0, 0].imshow(vv, cmap="gray", vmin=0, vmax=1)
    axes[0, 0].set_title("Sentinel-1 SAR: VV Polarization", fontsize=12, fontweight="bold")
    axes[0, 0].axis("off")
    plt.colorbar(im1, ax=axes[0, 0], fraction=0.046, pad=0.04, label="Normalized Backscatter")

    # Panel 2: S1 SAR VH
    im2 = axes[0, 1].imshow(vh, cmap="gray", vmin=0, vmax=1)
    axes[0, 1].set_title("Sentinel-1 SAR: VH Polarization (Cross-Pol)", fontsize=12, fontweight="bold")
    axes[0, 1].axis("off")
    plt.colorbar(im2, ax=axes[0, 1], fraction=0.046, pad=0.04, label="Normalized Backscatter")

    # Panel 3: Sentinel-2 Optical RGB
    if has_s2:
        axes[0, 2].imshow(rgb_disp)
        axes[0, 2].set_title("Sentinel-2 Optical (True-Color RGB: B4-B3-B2)", fontsize=12, fontweight="bold")
    else:
        axes[0, 2].text(0.5, 0.5, "S2 Optical Not Available", ha="center", va="center", fontsize=12)
        axes[0, 2].set_title("Sentinel-2 Optical (N/A)", fontsize=12, fontweight="bold")
    axes[0, 2].axis("off")

    # Panel 4: Pre-Flood JRC Permanent Water Baseline
    axes[1, 0].imshow(jrc_mask, cmap=JRC_CMAP, norm=JRC_NORM)
    axes[1, 0].set_title("Pre-Flood Baseline: JRC Permanent Water", fontsize=12, fontweight="bold")
    axes[1, 0].axis("off")
    jrc_patches = [
        mpatches.Patch(color="#2d3748", label="Dry Land"),
        mpatches.Patch(color="#4299e1", label="Permanent Water"),
    ]
    axes[1, 0].legend(handles=jrc_patches, loc="lower right", framealpha=0.8)

    # Panel 5: Ground Truth Flood Mask
    axes[1, 1].imshow(label_mask, cmap=MASK_CMAP, norm=MASK_NORM)
    axes[1, 1].set_title("Ground Truth Mask (LabelHand)", fontsize=12, fontweight="bold")
    axes[1, 1].axis("off")
    mask_patches = [
        mpatches.Patch(color="#2d3748", label=f"Land ({land_px:,} px)"),
        mpatches.Patch(color="#3182ce", label=f"Water ({water_px:,} px)"),
        mpatches.Patch(color="#f6e05e", label=f"Invalid / Cloud ({invalid_px:,} px)"),
    ]
    axes[1, 1].legend(handles=mask_patches, loc="lower right", framealpha=0.8)

    # Panel 6: Multi-Modal Flood Overlay
    base_bg = rgb_disp if has_s2 else np.stack([vh, vh, vh], axis=-1)
    axes[1, 2].imshow(base_bg)
    # Highlight water in neon blue and invalid in semi-transparent yellow
    overlay_rgba = np.zeros((512, 512, 4), dtype=np.float32)
    overlay_rgba[label_mask == 1] = [0.0, 0.8, 1.0, 0.55]      # Bright Cyan for Flood Water
    overlay_rgba[label_mask == -1] = [0.95, 0.8, 0.2, 0.40]    # Soft Yellow for Invalid
    axes[1, 2].imshow(overlay_rgba)
    axes[1, 2].set_title("Satellite Image + Flood Overlay", fontsize=12, fontweight="bold")
    axes[1, 2].axis("off")

    overlay_patches = [
        mpatches.Patch(color=(0.0, 0.8, 1.0, 0.8), label="Detected Flood Extent"),
        mpatches.Patch(color=(0.95, 0.8, 0.2, 0.8), label="Cloud / Invalid Mask"),
    ]
    axes[1, 2].legend(handles=overlay_patches, loc="lower right", framealpha=0.8)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    return True


def generate_dataset_visualizations(
    data_dir: str = "data/samples",
    output_dir: str = "outputs/visualizations/dataset_samples",
    max_samples: int = 15,
) -> List[str]:
    """
    Generates multi-modal sample visualization figures for development chips.
    """
    os.makedirs(output_dir, exist_ok=True)
    s1_files = sorted(glob.glob(os.path.join(data_dir, "S1Hand", "*_S1Hand.tif")))
    stems = [os.path.basename(f).replace("_S1Hand.tif", "") for f in s1_files]

    print(f"Generating sample visualizations for {min(len(stems), max_samples)} chips to {output_dir}...")
    saved_paths = []

    for stem in stems[:max_samples]:
        out_path = os.path.join(output_dir, f"{stem}_verification.png")
        success = plot_single_sample(stem, data_dir, out_path)
        if success:
            saved_paths.append(out_path)
            print(f"  [SAVED] {os.path.basename(out_path)}")

    print(f"Total visualizations generated: {len(saved_paths)}")
    return saved_paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Visual Verification Figures for Sen1Floods11")
    parser.add_argument("--data_dir", type=str, default="data/samples", help="Path to data directory")
    parser.add_argument("--output_dir", type=str, default="outputs/visualizations/dataset_samples", help="Target output directory")
    parser.add_argument("--max_samples", type=int, default=12, help="Number of sample figures to generate")
    args = parser.parse_args()

    generate_dataset_visualizations(args.data_dir, args.output_dir, args.max_samples)
