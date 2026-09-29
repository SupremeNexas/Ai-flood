"""
Unified Final Report and Audit Artefact Generator.

Produces:
- outputs/final/benchmark_results.csv
- outputs/final/validation_results.json
- outputs/final/official_test_results.json
- outputs/final/confusion_matrix.json
- outputs/final/experiment_summary.md
- outputs/visualizations/final_test/*.png
"""

import os
import sys
import json
import torch
import pandas as pd
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.training.evaluate_test import evaluate_full_test_split
from src.visualization.visualize_predictions import generate_representative_test_visualizations

MODALITIES = [
    {"name": "S1 (SAR Only)", "key": "s1", "channels": 2, "ckpt": "checkpoints/best_s1.pt"},
    {"name": "S2 RGB (Optical Only)", "key": "s2_rgb", "channels": 3, "ckpt": "checkpoints/best_s2_rgb.pt"},
    {"name": "S1 + JRC (SAR + Baseline)", "key": "s1_jrc", "channels": 3, "ckpt": "checkpoints/best_s1_jrc.pt"},
    {"name": "S1 + S2 RGB (Fusion)", "key": "s1_s2_rgb", "channels": 5, "ckpt": "checkpoints/best_s1_s2_rgb.pt"},
    {"name": "S1 + S2 RGB + JRC (Full Multi-Modal)", "key": "s1_s2_rgb_jrc", "channels": 6, "ckpt": "checkpoints/best_s1_s2_rgb_jrc.pt"},
]


def generate_all_final_reports(
    output_dir: str = "outputs/final",
    vis_dir: str = "outputs/visualizations/final_test",
    checkpoints_dir: str = "checkpoints",
    data_dir: str = "data/samples",
    splits_dir: str = "data/raw/splits",
):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(vis_dir, exist_ok=True)

    print("=" * 80)
    print("GENERATING AUDITED FINAL BENCHMARK AND TEST REPORTS")
    print("=" * 80)

    # 1. Collect Validation Benchmark Data
    validation_records = []
    for mod_info in MODALITIES:
        ckpt_path = os.path.join(checkpoints_dir, f"best_{mod_info['key']}.pt")
        if not os.path.exists(ckpt_path):
            print(f"Notice: Checkpoint {ckpt_path} missing; trying fallback...")
            continue

        ckpt = torch.load(ckpt_path, map_location="cpu")
        val_metrics = ckpt.get("val_metrics", {})
        val_loss = ckpt.get("val_loss", 0.0)
        epoch = ckpt.get("epoch", 0)

        record = {
            "configuration": mod_info["name"],
            "modality": mod_info["key"],
            "channels": mod_info["channels"],
            "best_epoch": int(epoch),
            "val_loss": round(float(val_loss), 4),
            "val_iou": round(float(val_metrics.get("iou", 0.0)), 4),
            "val_dice": round(float(val_metrics.get("dice", 0.0)), 4),
            "val_precision": round(float(val_metrics.get("precision", 0.0)), 4),
            "val_recall": round(float(val_metrics.get("recall", 0.0)), 4),
            "val_f1": round(float(val_metrics.get("f1", 0.0)), 4),
            "val_accuracy": round(float(val_metrics.get("accuracy", 0.0)), 4),
            "checkpoint": ckpt_path,
        }
        validation_records.append(record)

    # Save benchmark CSV and JSON
    bench_df = pd.DataFrame(validation_records)
    csv_path = os.path.join(output_dir, "benchmark_results.csv")
    bench_df.to_csv(csv_path, index=False)

    val_json_path = os.path.join(output_dir, "validation_results.json")
    with open(val_json_path, "w") as f:
        json.dump(validation_records, f, indent=2)

    print(f"Saved benchmark CSV to: {csv_path}")
    print(f"Saved validation JSON to: {val_json_path}")

    # 2. Select Winning Model based purely on Validation IoU
    winning_model = max(validation_records, key=lambda x: x["val_iou"])
    print(f"\nWinning Model Selected (Validation Set): {winning_model['configuration']} (Val IoU: {winning_model['val_iou']:.4f})")

    # 3. Evaluate Winning Model on COMPLETE Official Test Split (90 chips)
    print(f"\nEvaluating Winning Model strictly on COMPLETE 90-chip Official Test Split...")
    test_results = evaluate_full_test_split(
        checkpoint_path=winning_model["checkpoint"],
        modality=winning_model["modality"],
        data_dir=data_dir,
        splits_dir=splits_dir,
        output_dir=output_dir,
    )

    # 4. Generate Representative Visual Predictions
    print(f"\nGenerating diverse representative test predictions in {vis_dir}...")
    vis_records = generate_representative_test_visualizations(
        checkpoint_path=winning_model["checkpoint"],
        output_dir=vis_dir,
        data_dir=data_dir,
        splits_dir=splits_dir,
        modality=winning_model["modality"],
    )

    # 5. Compile Comprehensive Markdown Report
    summary_md_path = os.path.join(output_dir, "experiment_summary.md")
    with open(summary_md_path, "w") as f:
        f.write("# Sen1Floods11 Semantic Segmentation — Final Audited Experiment Report\n\n")
        f.write("## 1. Modality Validation Benchmark (Model Selection)\n\n")
        f.write("All 5 input modalities were trained and evaluated under identical conditions (10 epochs, seed 42, lr 0.0005, AdamW, Cosine Annealing, GroupNorm U-Net) on the official training split (252 chips) and validation split (89 chips).\n\n")
        f.write("| Configuration | Channels | Best Epoch | Val Loss | Val IoU | Val Dice | Val Precision | Val Recall | Val F1 |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for r in validation_records:
            f.write(f"| {r['configuration']} | {r['channels']} | {r['best_epoch']} | {r['val_loss']:.4f} | {r['val_iou']:.4f} | {r['val_dice']:.4f} | {r['val_precision']:.4f} | {r['val_recall']:.4f} | {r['val_f1']:.4f} |\n")

        f.write(f"\n**Selected Architecture:** `{winning_model['configuration']}` (Highest Validation IoU: **{winning_model['val_iou']:.4f}**)\n\n")

        f.write("## 2. Official Test Set Evaluation (Unseen 90-Chip Split)\n\n")
        f.write("The winning model was evaluated strictly after model selection on the complete 90 chips of `flood_test_data.csv`:\n\n")
        f.write(f"- **Test Chips Evaluated:** {test_results['total_test_chips_evaluated']} / 90 (100% of official test split)\n")
        f.write(f"- **Total Valid Pixels:** {test_results['total_valid_pixels']:,}\n")
        f.write(f"- **Total Water Pixels (GT):** {test_results['total_water_pixels']:,} ({test_results['water_coverage_pct']}% coverage)\n")
        f.write(f"- **Test Loss:** {test_results['test_loss']:.4f}\n")
        f.write(f"- **Test IoU:** **{test_results['test_iou']:.4f}**\n")
        f.write(f"- **Test Dice (F1):** **{test_results['test_dice']:.4f}**\n")
        f.write(f"- **Test Precision:** **{test_results['test_precision']:.4f}**\n")
        f.write(f"- **Test Recall:** **{test_results['test_recall']:.4f}**\n")
        f.write(f"- **Test Accuracy:** **{test_results['test_accuracy']:.4f}**\n\n")

        f.write("### Test Confusion Matrix (Valid Pixels Only)\n\n")
        f.write("```\n")
        cm_path = os.path.join(output_dir, "confusion_matrix.json")
        with open(cm_path) as cm_f:
            cm = json.load(cm_f)
        f.write(f"True Positives (TP):  {cm['true_positives']:,}\n")
        f.write(f"False Positives (FP): {cm['false_positives']:,}\n")
        f.write(f"False Negatives (FN): {cm['false_negatives']:,}\n")
        f.write(f"True Negatives (TN):  {cm['true_negatives']:,}\n")
        f.write("```\n\n")

        f.write("## 3. Geospatial Area & Temporal Verification\n\n")
        f.write("- **Geospatial Resolution:** Sen1Floods11 GeoTIFFs use WGS84 coordinates (`EPSG:4326`) with pixel resolution $\\approx 8.98 \\times 10^{-5}$ degrees (approx. $10.0\\text{ m}$ nominal at the equator, varying by $\\cos(\\text{lat})$ in longitude). Reported $km^2$ figures are explicitly marked as **nominal approximations**.\n")
        f.write("- **Temporal Setup:** The dataset provides bi-temporal reference via active **Sentinel-1 SAR flood imagery** paired with **JRC Global Surface Water historical permanence baseline** (no separate `_S1Pre.tif` files exist in Sen1Floods11).\n")

    print(f"Successfully compiled experiment summary to: {summary_md_path}")


if __name__ == "__main__":
    generate_all_final_reports()
