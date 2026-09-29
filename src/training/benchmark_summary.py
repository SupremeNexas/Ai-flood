"""
Benchmark Aggregator for all 5 trained input modalities.
Reads best validation checkpoints and computes comparative statistics.
"""

import os
import sys
import json
import torch
from pathlib import Path

PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.models.unet import build_unet
from src.training.evaluate_test import evaluate_test_split

MODALITIES = [
    {"name": "S1 (SAR Only)", "key": "s1", "channels": 2, "ckpt": "checkpoints/best_s1.pt"},
    {"name": "S2 RGB (Optical Only)", "key": "s2_rgb", "channels": 3, "ckpt": "checkpoints/best_s2_rgb.pt"},
    {"name": "S1 + JRC (SAR + Baseline)", "key": "s1_jrc", "channels": 3, "ckpt": "checkpoints/best_s1_jrc.pt"},
    {"name": "S1 + S2 RGB (Fusion)", "key": "s1_s2_rgb", "channels": 5, "ckpt": "checkpoints/best_s1_s2_rgb.pt"},
    {"name": "S1 + S2 RGB + JRC (Full Multi-Modal)", "key": "s1_s2_rgb_jrc", "channels": 6, "ckpt": "checkpoints/best_s1_s2_rgb_jrc.pt"},
]

def main():
    print("=" * 70)
    print("5-MODALITY BENCHMARK COMPARISON SUMMARY")
    print("=" * 70)

    summary_records = []

    for item in MODALITIES:
        ckpt_path = item["ckpt"]
        if not os.path.exists(ckpt_path):
            print(f"Warning: Checkpoint not found: {ckpt_path}")
            continue

        ckpt = torch.load(ckpt_path, map_location="cpu")
        val_metrics = ckpt.get("val_metrics", {})
        epoch = ckpt.get("epoch", -1)
        val_loss = ckpt.get("val_loss", 0.0)

        record = {
            "configuration": item["name"],
            "modality": item["key"],
            "channels": item["channels"],
            "best_epoch": epoch,
            "val_loss": round(val_loss, 4),
            "val_iou": val_metrics.get("iou", 0.0),
            "val_dice": val_metrics.get("dice", 0.0),
            "val_precision": val_metrics.get("precision", 0.0),
            "val_recall": val_metrics.get("recall", 0.0),
            "val_f1": val_metrics.get("f1", 0.0),
            "val_accuracy": val_metrics.get("accuracy", 0.0),
        }
        summary_records.append(record)

    output_json = "outputs/training/benchmark_summary.json"
    with open(output_json, "w") as f:
        json.dump(summary_records, f, indent=2)

    # Print Table
    header = f"| {'Configuration':<32} | {'Ch':<2} | {'Epoch':<5} | {'Val Loss':<8} | {'IoU':<7} | {'Dice':<7} | {'Precision':<9} | {'Recall':<7} | {'F1':<7} |"
    sep = f"|{'-'*34}|{'-'*4}|{'-'*7}|{'-'*10}|{'-'*9}|{'-'*9}|{'-'*11}|{'-'*9}|{'-'*9}|"
    print(header)
    print(sep)
    for r in summary_records:
        row = f"| {r['configuration']:<32} | {r['channels']:<2} | {r['best_epoch']:<5} | {r['val_loss']:<8.4f} | {r['val_iou']:<7.4f} | {r['val_dice']:<7.4f} | {r['val_precision']:<9.4f} | {r['val_recall']:<7.4f} | {r['val_f1']:<7.4f} |"
        print(row)
    print("=" * 70)

    # Identify best model based on validation IoU
    best_record = max(summary_records, key=lambda x: x["val_iou"])
    print(f"\nWINNING CONFIGURATION: {best_record['configuration']} (Val IoU: {best_record['val_iou']:.4f})")

    # Evaluate best model on official test set
    best_ckpt = f"checkpoints/best_{best_record['modality']}.pt"
    print(f"\nEvaluating Best Checkpoint on Test Set: {best_ckpt}")
    test_res = evaluate_test_split(
        checkpoint_path=best_ckpt,
        modality=best_record["modality"],
        output_path="outputs/training/official_test_set_evaluation.json",
    )

if __name__ == "__main__":
    main()
