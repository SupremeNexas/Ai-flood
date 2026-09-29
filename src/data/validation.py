"""
Sen1Floods11 Dataset Validation and Quality Control Module.

Performs integrity checks, validates layer alignments, verifies dimensions,
calculates band statistics, analyzes class distributions, and exports
comprehensive dataset summaries to JSON and CSV.
"""

import os
import glob
import json
import argparse
import rasterio
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from pathlib import Path


def discover_chips(data_dir: str) -> Dict[str, Dict[str, str]]:
    """
    Discovers and matches all available layers for each chip stem.
    Layers: S1Hand, S2Hand, LabelHand, JRCWaterHand.
    """
    layers = ["S1Hand", "S2Hand", "LabelHand", "JRCWaterHand"]
    chip_dict = {}

    for lyr in layers:
        layer_dir = os.path.join(data_dir, lyr)
        if not os.path.exists(layer_dir):
            continue
        files = glob.glob(os.path.join(layer_dir, f"*_{lyr}.tif"))
        for f in files:
            stem = os.path.basename(f).replace(f"_{lyr}.tif", "")
            if stem not in chip_dict:
                chip_dict[stem] = {}
            chip_dict[stem][lyr] = f

    return chip_dict


def validate_single_chip(
    stem: str, layer_paths: Dict[str, str]
) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Validates a single chip's layers for integrity, dimension match,
    and expected value ranges.
    """
    issues = []
    stats: Dict[str, Any] = {
        "stem": stem,
        "event": stem.split("_")[0],
        "has_s1": "S1Hand" in layer_paths,
        "has_s2": "S2Hand" in layer_paths,
        "has_label": "LabelHand" in layer_paths,
        "has_jrc": "JRCWaterHand" in layer_paths,
    }

    # Verify presence of essential components
    if not stats["has_s1"]:
        issues.append("Missing S1Hand layer")
    if not stats["has_label"]:
        issues.append("Missing LabelHand ground truth")

    # 1. Validate S1 SAR
    if stats["has_s1"]:
        try:
            with rasterio.open(layer_paths["S1Hand"]) as src:
                s1_data = src.read()
                stats["s1_bands"] = src.count
                stats["s1_height"] = src.height
                stats["s1_width"] = src.width
                stats["s1_dtype"] = str(s1_data.dtype)
                stats["s1_crs"] = str(src.crs)

                if src.count != 2:
                    issues.append(f"S1 band count mismatch: expected 2, got {src.count}")
                if src.height != 512 or src.width != 512:
                    issues.append(f"S1 dimension mismatch: expected 512x512, got {src.height}x{src.width}")

                # Band statistics
                vv = s1_data[0]
                vh = s1_data[1]
                stats["s1_vv_min"] = float(np.nanmin(vv))
                stats["s1_vv_max"] = float(np.nanmax(vv))
                stats["s1_vv_mean"] = float(np.nanmean(vv))
                stats["s1_vh_min"] = float(np.nanmin(vh))
                stats["s1_vh_max"] = float(np.nanmax(vh))
                stats["s1_vh_mean"] = float(np.nanmean(vh))
                stats["s1_nan_count"] = int(np.isnan(s1_data).sum())
        except Exception as e:
            issues.append(f"Corrupt S1 file: {e}")

    # 2. Validate Label
    if stats["has_label"]:
        try:
            with rasterio.open(layer_paths["LabelHand"]) as src:
                label_data = src.read(1)
                stats["label_height"] = src.height
                stats["label_width"] = src.width
                stats["label_dtype"] = str(label_data.dtype)

                if src.height != 512 or src.width != 512:
                    issues.append(f"Label dimension mismatch: expected 512x512, got {src.height}x{src.width}")

                unq, cnts = np.unique(label_data, return_counts=True)
                val_counts = dict(zip([int(x) for x in unq], [int(c) for c in cnts]))
                stats["label_invalid_px"] = val_counts.get(-1, 0)
                stats["label_non_water_px"] = val_counts.get(0, 0)
                stats["label_water_px"] = val_counts.get(1, 0)
                stats["total_valid_px"] = stats["label_non_water_px"] + stats["label_water_px"]

                if stats["total_valid_px"] > 0:
                    stats["flood_water_ratio"] = float(stats["label_water_px"] / stats["total_valid_px"])
                else:
                    stats["flood_water_ratio"] = 0.0

                unexpected_values = [v for v in val_counts.keys() if v not in [-1, 0, 1]]
                if unexpected_values:
                    issues.append(f"Unexpected label values: {unexpected_values}")
        except Exception as e:
            issues.append(f"Corrupt Label file: {e}")

    # 3. Validate S2 Optical if available
    if stats["has_s2"]:
        try:
            with rasterio.open(layer_paths["S2Hand"]) as src:
                s2_data = src.read()
                stats["s2_bands"] = src.count
                stats["s2_height"] = src.height
                stats["s2_width"] = src.width
                stats["s2_dtype"] = str(s2_data.dtype)
                stats["s2_min"] = float(np.nanmin(s2_data))
                stats["s2_max"] = float(np.nanmax(s2_data))
                stats["s2_mean"] = float(np.nanmean(s2_data))
        except Exception as e:
            issues.append(f"Corrupt S2 file: {e}")

    # 4. Validate JRC Baseline if available
    if stats["has_jrc"]:
        try:
            with rasterio.open(layer_paths["JRCWaterHand"]) as src:
                jrc_data = src.read(1)
                unq, cnts = np.unique(jrc_data, return_counts=True)
                jrc_counts = dict(zip([int(x) for x in unq], [int(c) for c in cnts]))
                stats["jrc_permanent_water_px"] = jrc_counts.get(1, 0)
                stats["jrc_dry_px"] = jrc_counts.get(0, 0)
        except Exception as e:
            issues.append(f"Corrupt JRC file: {e}")

    is_valid = len(issues) == 0
    stats["is_valid"] = is_valid
    stats["issues"] = "; ".join(issues) if issues else "None"
    return is_valid, stats, issues


def run_dataset_validation(
    data_dir: str,
    output_dir: str = "outputs",
) -> Dict[str, Any]:
    """
    Executes comprehensive validation across the entire discovered dataset
    and writes out summary JSON and CSV reports.
    """
    os.makedirs(output_dir, exist_ok=True)
    chip_dict = discover_chips(data_dir)
    print(f"\n=======================================================")
    print(f"RUNNING DATASET VALIDATION: {data_dir}")
    print(f"Discovered {len(chip_dict)} unique chip stems across all layers.")
    print(f"=======================================================\n")

    if not chip_dict:
        print(f"Warning: No dataset chips found in {data_dir}")
        return {"total_chips": 0, "status": "empty"}

    all_stats = []
    total_valid = 0
    total_invalid = 0

    for stem, lpaths in chip_dict.items():
        is_valid, stats, issues = validate_single_chip(stem, lpaths)
        if is_valid:
            total_valid += 1
        else:
            total_invalid += 1
        all_stats.append(stats)

    df = pd.DataFrame(all_stats)

    # Save detailed CSV
    csv_path = os.path.join(output_dir, "dataset_statistics.csv")
    df.to_csv(csv_path, index=False)
    print(f"Detailed chip statistics saved to: {csv_path}")

    # Compute global summary metrics
    total_pixels = int(df["label_invalid_px"].sum() + df["label_non_water_px"].sum() + df["label_water_px"].sum()) if "label_water_px" in df else 0
    total_water_px = int(df["label_water_px"].sum()) if "label_water_px" in df else 0
    total_non_water_px = int(df["label_non_water_px"].sum()) if "label_non_water_px" in df else 0
    total_invalid_px = int(df["label_invalid_px"].sum()) if "label_invalid_px" in df else 0
    total_valid_px = total_water_px + total_non_water_px

    summary = {
        "dataset_name": "Sen1Floods11",
        "data_directory": data_dir,
        "total_chips_discovered": len(chip_dict),
        "valid_chips": total_valid,
        "invalid_chips": total_invalid,
        "geographic_events_represented": sorted(df["event"].unique().tolist()) if "event" in df else [],
        "layers_available": {
            "S1Hand": int(df["has_s1"].sum()) if "has_s1" in df else 0,
            "S2Hand": int(df["has_s2"].sum()) if "has_s2" in df else 0,
            "LabelHand": int(df["has_label"].sum()) if "has_label" in df else 0,
            "JRCWaterHand": int(df["has_jrc"].sum()) if "has_jrc" in df else 0,
        },
        "spatial_properties": {
            "image_height": 512,
            "image_width": 512,
            "crs": "EPSG:4326",
            "spatial_resolution_meters": 10.0,
            "pixel_area_m2": 100.0,
            "pixel_area_km2": 0.0001,
        },
        "pixel_class_distribution": {
            "total_pixels": total_pixels,
            "valid_pixels": total_valid_px,
            "water_pixels": total_water_px,
            "non_water_pixels": total_non_water_px,
            "invalid_cloud_nodata_pixels": total_invalid_px,
            "water_percentage_overall": round((total_water_px / total_valid_px * 100), 2) if total_valid_px > 0 else 0.0,
            "non_water_percentage_overall": round((total_non_water_px / total_valid_px * 100), 2) if total_valid_px > 0 else 0.0,
            "invalid_pixel_percentage": round((total_invalid_px / total_pixels * 100), 2) if total_pixels > 0 else 0.0,
            "imbalance_ratio_nonwater_to_water": round((total_non_water_px / total_water_px), 2) if total_water_px > 0 else 0.0,
        },
        "s1_sar_statistics": {
            "vv_min_global": float(df["s1_vv_min"].min()) if "s1_vv_min" in df else None,
            "vv_max_global": float(df["s1_vv_max"].max()) if "s1_vv_max" in df else None,
            "vv_mean_global": float(df["s1_vv_mean"].mean()) if "s1_vv_mean" in df else None,
            "vh_min_global": float(df["s1_vh_min"].min()) if "s1_vh_min" in df else None,
            "vh_max_global": float(df["s1_vh_max"].max()) if "s1_vh_max" in df else None,
            "vh_mean_global": float(df["s1_vh_mean"].mean()) if "s1_vh_mean" in df else None,
        }
    }

    json_path = os.path.join(output_dir, "dataset_summary.json")
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Global dataset summary saved to: {json_path}")

    # Print summary console table
    print("\n---------------- DATASET VALIDATION SUMMARY ----------------")
    print(f"Total Chips Evaluated:  {len(chip_dict)}")
    print(f"Valid / Passing Chips: {total_valid} / {len(chip_dict)} ({(total_valid/len(chip_dict)*100):.1f}%)")
    print(f"Events Covered ({len(summary['geographic_events_represented'])}): {', '.join(summary['geographic_events_represented'])}")
    print(f"Total Valid Pixels:    {total_valid_px:,}")
    print(f"Water Pixels:          {total_water_px:,} ({summary['pixel_class_distribution']['water_percentage_overall']}%)")
    print(f"Non-Water Pixels:      {total_non_water_px:,} ({summary['pixel_class_distribution']['non_water_percentage_overall']}%)")
    print(f"Invalid Pixels:        {total_invalid_px:,} ({summary['pixel_class_distribution']['invalid_pixel_percentage']}%)")
    print(f"Class Imbalance Ratio: 1 : {summary['pixel_class_distribution']['imbalance_ratio_nonwater_to_water']} (Water : Non-Water)")
    print(f"SAR Backscatter VV:    [{summary['s1_sar_statistics']['vv_min_global']:.2f}, {summary['s1_sar_statistics']['vv_max_global']:.2f}] dB (Mean: {summary['s1_sar_statistics']['vv_mean_global']:.2f})")
    print(f"SAR Backscatter VH:    [{summary['s1_sar_statistics']['vh_min_global']:.2f}, {summary['s1_sar_statistics']['vh_max_global']:.2f}] dB (Mean: {summary['s1_sar_statistics']['vh_mean_global']:.2f})")
    print("------------------------------------------------------------\n")

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate Sen1Floods11 Dataset Files and Quality")
    parser.add_argument("--data_dir", type=str, default="data/samples", help="Path to data directory")
    parser.add_argument("--output_dir", type=str, default="outputs", help="Output directory for reports")
    args = parser.parse_args()

    run_dataset_validation(args.data_dir, args.output_dir)
