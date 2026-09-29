"""
Robust Split Downloader and Integrity Verifier for Sen1Floods11.

Downloads all chips listed in official split CSV files (train, valid, test, bolivia)
using concurrent threads with exponential backoff and rasterio validation.
"""

import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Tuple, Dict, Any

# Ensure project root is in sys.path
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import rasterio
from tqdm import tqdm

BASE_GCS_URL = "https://storage.googleapis.com/sen1floods11/v1.1"


def download_single_layer(stem: str, layer: str, target_dir: str, retries: int = 3) -> Tuple[str, str, bool, str]:
    """Downloads and verifies a single GeoTIFF file."""
    fname = f"{stem}_{layer}.tif"
    dest_path = os.path.join(target_dir, layer, fname)
    os.makedirs(os.path.join(target_dir, layer), exist_ok=True)

    # Check if already exists and is valid
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        try:
            with rasterio.open(dest_path) as src:
                if src.width == 512 and src.height == 512:
                    return stem, layer, True, "Already exists and valid"
        except Exception:
            # Corrupted file, re-download
            try:
                os.remove(dest_path)
            except OSError:
                pass

    url = f"{BASE_GCS_URL}/data/flood_events/HandLabeled/{layer}/{fname}"

    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp, open(dest_path, "wb") as out_f:
                while True:
                    chunk = resp.read(16384)
                    if not chunk:
                        break
                    out_f.write(chunk)

            # Validate integrity via rasterio
            with rasterio.open(dest_path) as src:
                if src.width != 512 or src.height != 512:
                    raise ValueError(f"Invalid dimensions: {src.width}x{src.height}")
            return stem, layer, True, "Downloaded & Verified"
        except Exception as e:
            if os.path.exists(dest_path):
                try:
                    os.remove(dest_path)
                except OSError:
                    pass
            if attempt == retries - 1:
                return stem, layer, False, str(e)
            time.sleep(1.0 * (attempt + 1))

    return stem, layer, False, "Max retries exceeded"


def download_split_chips(
    split_file: str,
    target_dir: str = "data/samples",
    layers: List[str] = None,
    max_workers: int = 12,
) -> Dict[str, Any]:
    """
    Downloads all chips in a given split CSV across all specified layers.
    """
    if layers is None:
        layers = ["S1Hand", "S2Hand", "LabelHand", "JRCWaterHand"]

    if not os.path.exists(split_file):
        raise FileNotFoundError(f"Split file not found: {split_file}")

    df = pd.read_csv(split_file, header=None)
    stems = df[0].apply(lambda x: x.split("/")[-1].replace("_S1Hand.tif", "").replace("_LabelHand.tif", "")).tolist()

    print(f"\n=======================================================")
    print(f"DOWNLOADING SPLIT: {os.path.basename(split_file)}")
    print(f"Total Chips: {len(stems)} | Layers: {layers}")
    print(f"Total Files to Verify/Download: {len(stems) * len(layers)}")
    print(f"Target Directory: {target_dir}")
    print(f"=======================================================\n")

    tasks = []
    for stem in stems:
        for lyr in layers:
            tasks.append((stem, lyr))

    results = {"success": 0, "failed": 0, "failed_items": []}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(download_single_layer, stem, lyr, target_dir): (stem, lyr)
            for stem, lyr in tasks
        }

        with tqdm(total=len(tasks), desc=f"Ingesting {os.path.basename(split_file)}") as pbar:
            for future in as_completed(futures):
                stem, layer, ok, msg = future.result()
                if ok:
                    results["success"] += 1
                else:
                    results["failed"] += 1
                    results["failed_items"].append({"stem": stem, "layer": layer, "error": msg})
                pbar.update(1)

    print(f"\nDownload Summary for {os.path.basename(split_file)}:")
    print(f"  Verified/Downloaded Files: {results['success']} / {len(tasks)}")
    print(f"  Failed Files: {results['failed']}")

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Download Split Chips")
    parser.add_argument("--split", type=str, default="test", choices=["train", "valid", "test", "bolivia", "all"])
    parser.add_argument("--data_dir", type=str, default="data/samples")
    parser.add_argument("--splits_dir", type=str, default="data/raw/splits")
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()

    splits = ["test"] if args.split == "test" else (["train", "valid", "test", "bolivia"] if args.split == "all" else [args.split])

    for s in splits:
        split_path = os.path.join(args.splits_dir, f"flood_{s}_data.csv")
        download_split_chips(split_path, target_dir=args.data_dir, max_workers=args.workers)
