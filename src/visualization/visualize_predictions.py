"""
Representative 3-Image Test Visualization Module for Sen1Floods11.

Generates exactly 3 representative 5-panel diagnostic test figures:
1. Good Prediction (High IoU / Dice)
2. Average Prediction (Median IoU / Dice)
3. Difficult Prediction (Challenging / Low Recall or High FP)

Saves them directly into outputs/visualizations/final_test/.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Any

PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import torch
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.patches as mpatches

from src.models.unet import build_unet
from src.data.dataset import Sen1Floods11Dataset
from src.training.metrics import compute_confusion_matrix_elements
from src.utils.config_loader import get_device

# Color Maps
MASK_CMAP = ListedColormap(["#f6e05e", "#2d3748", "#3182ce"])  # -1: Cloud/Invalid (Yellow), 0: Land, 1: Water (Blue)
MASK_NORM = BoundaryNorm([-1.5, -0.5, 0.5, 1.5], MASK_CMAP.N)

PRED_CMAP = ListedColormap(["#2d3748", "#00d2ff"])  # 0: Land, 1: Pred Flood (Bright Cyan)
PRED_NORM = BoundaryNorm([-0.5, 0.5, 1.5], PRED_CMAP.N)


@torch.no_grad()
def render_5panel_figure(
    model: torch.nn.Module,
    sample: Dict[str, Any],
    output_path: str,
    device: str = "cpu",
    threshold: float = 0.0,
    category_label: str = "Test Sample",
) -> Dict[str, Any]:
    """Renders and saves a 5-panel diagnostic figure for a single satellite chip."""
    image = sample["image"].unsqueeze(0).to(device)
    target_mask = sample["mask"].numpy()
    meta = sample.get("metadata", {})
    stem = meta.get("stem", "unknown")
    event = meta.get("event", "unknown")

    logits = model(image).squeeze(0)
    pred_binary = (logits > threshold).cpu().numpy().astype(np.int64)

    # Compute metrics over valid pixels only
    tp, fp, fn, tn, valid_px, water_px = compute_confusion_matrix_elements(
        logits.unsqueeze(0), sample["mask"].unsqueeze(0).to(device), threshold=threshold, ignore_index=-1
    )

    iou = tp / max(1, tp + fp + fn) if (tp + fp + fn) > 0 else (1.0 if water_px == 0 else 0.0)
    dice = (2.0 * tp) / max(1, 2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else (1.0 if water_px == 0 else 0.0)
    prec = tp / max(1, tp + fp) if (tp + fp) > 0 else 0.0
    rec = tp / max(1, tp + fn) if (tp + fn) > 0 else 0.0

    valid_mask = (target_mask != -1)
    pred_water_px = int(np.sum((pred_binary == 1) & valid_mask))
    gt_coverage_pct = (water_px / max(1, valid_px)) * 100.0
    pred_coverage_pct = (pred_water_px / max(1, valid_px)) * 100.0

    # SAR false-color background
    img_np = sample["image"].numpy()
    vv_ch = img_np[0]
    vh_ch = img_np[1] if img_np.shape[0] >= 2 else img_np[0]
    ratio_ch = np.clip(vv_ch / (vh_ch + 1e-4), 0.0, 1.0)
    bg_img = np.stack([vv_ch, vh_ch, ratio_ch], axis=-1)

    fig, axes = plt.subplots(1, 5, figsize=(25, 5.5), facecolor="#ffffff")
    fig.suptitle(
        f"[{category_label.upper()}] Chip: {stem} (Event: {event})\n"
        f"Metrics: IoU: {iou:.4f} | Dice (F1): {dice:.4f} | Precision: {prec:.4f} | Recall: {rec:.4f} | "
        f"Water Pixels: GT={water_px:,} ({gt_coverage_pct:.2f}%) vs Pred={pred_water_px:,} ({pred_coverage_pct:.2f}%)",
        fontsize=13,
        fontweight="bold",
        y=0.98,
    )

    # Panel 1: Satellite Input
    axes[0].imshow(bg_img)
    axes[0].set_title("1. S1 SAR Composite (VV, VH, Ratio)", fontsize=10, fontweight="bold")
    axes[0].axis("off")

    # Panel 2: Ground Truth
    axes[1].imshow(target_mask, cmap=MASK_CMAP, norm=MASK_NORM)
    axes[1].set_title(f"2. Ground Truth Mask\n(Water: {water_px:,} px | {gt_coverage_pct:.1f}%)", fontsize=10, fontweight="bold")
    axes[1].axis("off")
    gt_patches = [
        mpatches.Patch(color="#2d3748", label="Land"),
        mpatches.Patch(color="#3182ce", label="Water"),
        mpatches.Patch(color="#f6e05e", label="Invalid/Cloud"),
    ]
    axes[1].legend(handles=gt_patches, loc="lower right", framealpha=0.85, fontsize=8)

    # Panel 3: Predicted Flood Mask
    axes[2].imshow(pred_binary, cmap=PRED_CMAP, norm=PRED_NORM)
    axes[2].set_title(f"3. Predicted Flood Mask\n(Pred Water: {pred_water_px:,} px | {pred_coverage_pct:.1f}%)", fontsize=10, fontweight="bold")
    axes[2].axis("off")
    pred_patches = [
        mpatches.Patch(color="#2d3748", label="Pred Land"),
        mpatches.Patch(color="#00d2ff", label="Pred Flood"),
    ]
    axes[2].legend(handles=pred_patches, loc="lower right", framealpha=0.85, fontsize=8)

    # Panel 4: Ground Truth Overlay
    axes[3].imshow(bg_img)
    gt_overlay = np.zeros((*bg_img.shape[:2], 4), dtype=np.float32)
    gt_overlay[target_mask == 1] = [0.0, 0.45, 1.0, 0.60]
    axes[3].imshow(gt_overlay)
    axes[3].set_title("4. Ground Truth Overlay", fontsize=10, fontweight="bold")
    axes[3].axis("off")

    # Panel 5: Predicted Overlay
    axes[4].imshow(bg_img)
    pred_overlay = np.zeros((*bg_img.shape[:2], 4), dtype=np.float32)
    pred_overlay[(pred_binary == 1) & valid_mask] = [0.0, 0.90, 1.0, 0.65]
    axes[4].imshow(pred_overlay)
    axes[4].set_title("5. Model Prediction Overlay", fontsize=10, fontweight="bold")
    axes[4].axis("off")

    plt.tight_layout(rect=[0, 0.03, 1, 0.93])
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close()

    return {
        "stem": stem,
        "event": event,
        "category": category_label,
        "iou": float(round(iou, 4)),
        "dice": float(round(dice, 4)),
        "precision": float(round(prec, 4)),
        "recall": float(round(rec, 4)),
        "gt_water_pixels": int(water_px),
        "pred_water_pixels": int(pred_water_px),
        "figure_path": output_path,
    }


def generate_three_representative_visualizations(
    checkpoint_path: str = "checkpoints/best_s1.pt",
    output_dir: str = "outputs/visualizations/final_test",
    data_dir: str = "data/samples",
    splits_dir: str = "data/raw/splits",
    modality: str = "s1",
) -> List[Dict[str, Any]]:
    """
    Finds and generates the 3 representative test cases (Good, Average, Difficult).
    """
    device = get_device()
    test_split = os.path.join(splits_dir, "flood_test_data.csv")
    dataset = Sen1Floods11Dataset(data_dir=data_dir, split_file=test_split, modality=modality)

    checkpoint = torch.load(checkpoint_path, map_location=device)
    model = build_unet(modality=modality).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    # Score all test samples with substantial water (>500 pixels)
    candidates = []
    for idx in range(len(dataset)):
        sample = dataset[idx]
        image = sample["image"].unsqueeze(0).to(device)
        logits = model(image)
        tp, fp, fn, tn, valid_px, water_px = compute_confusion_matrix_elements(
            logits, sample["mask"].unsqueeze(0).to(device), threshold=0.0, ignore_index=-1
        )
        iou = tp / max(1, tp + fp + fn) if (tp + fp + fn) > 0 else 0.0
        dice = (2.0 * tp) / max(1, 2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0.0
        prec = tp / max(1, tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / max(1, tp + fn) if (tp + fn) > 0 else 0.0

        if water_px >= 500:
            candidates.append({
                "idx": idx,
                "stem": sample["metadata"]["stem"],
                "event": sample["metadata"]["event"],
                "iou": iou,
                "dice": dice,
                "precision": prec,
                "recall": rec,
                "water_pixels": water_px,
            })

    # Sort candidates by IoU
    candidates.sort(key=lambda x: x["iou"], reverse=True)

    # 1. Good Prediction: top tier (e.g. highest IoU)
    good_sample = candidates[0]
    # 2. Average Prediction: median candidate
    avg_sample = candidates[len(candidates) // 2]
    # 3. Difficult Prediction: lower tier with significant ground-truth water but challenging topology/recall
    difficult_sample = candidates[-2]

    selection = [
        ("Good Prediction", "1_good_prediction", good_sample),
        ("Average Prediction", "2_average_prediction", avg_sample),
        ("Difficult Prediction", "3_difficult_prediction", difficult_sample),
    ]

    os.makedirs(output_dir, exist_ok=True)
    results = []

    print("\n--- Generating 3 Representative Test Visualizations ---")
    for category_name, prefix, item in selection:
        sample = dataset[item["idx"]]
        out_filename = f"{prefix}_{item['stem']}.png"
        out_path = os.path.join(output_dir, out_filename)
        res = render_5panel_figure(
            model=model,
            sample=sample,
            output_path=out_path,
            device=device,
            category_label=category_name,
        )
        results.append(res)
        print(f"  [{category_name}] {item['stem']:<20} -> IoU: {res['iou']:.4f} | Dice: {res['dice']:.4f} | Prec: {res['precision']:.4f} | Rec: {res['recall']:.4f} | Saved: {out_filename}")

    # Save summary json
    with open(os.path.join(output_dir, "representative_summary.json"), "w") as f:
        json.dump(results, f, indent=2)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate 3 Representative Test Visualizations")
    parser.add_argument("--checkpoint", type=str, default="checkpoints/best_s1.pt")
    parser.add_argument("--output_dir", type=str, default="outputs/visualizations/final_test")
    parser.add_argument("--data_dir", type=str, default="data/samples")
    parser.add_argument("--splits_dir", type=str, default="data/raw/splits")
    parser.add_argument("--modality", type=str, default="s1")
    args = parser.parse_args()

    generate_three_representative_visualizations(
        checkpoint_path=args.checkpoint,
        output_dir=args.output_dir,
        data_dir=args.data_dir,
        splits_dir=args.splits_dir,
        modality=args.modality,
    )
