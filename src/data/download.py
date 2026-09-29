"""
Sen1Floods11 Dataset Ingestion and Acquisition Module.

This script manages downloading split CSVs, development sample chips,
and the full benchmark dataset from Google Cloud Storage.
"""

import os
import sys
import argparse
import urllib.request
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from typing import List, Optional

# Base URL for public HTTP access to Sen1Floods11 Google Cloud Storage
BASE_GCS_URL = "https://storage.googleapis.com/sen1floods11/v1.1"


def download_file(url: str, dest_path: str, retries: int = 3) -> bool:
    """Downloads a file from a URL with progress bar and retry mechanism."""
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        return True

    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp, open(dest_path, "wb") as out_f:
                total_size = int(resp.headers.get("Content-Length", 0))
                with tqdm(total=total_size, unit="B", unit_scale=True, desc=os.path.basename(dest_path), leave=False) as pbar:
                    while True:
                        chunk = resp.read(8192)
                        if not chunk:
                            break
                        out_f.write(chunk)
                        pbar.update(len(chunk))
            return True
        except Exception as e:
            if attempt == retries - 1:
                print(f"Failed to download {url}: {e}")
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                return False
    return False


def download_splits(dest_dir: str) -> None:
    """Downloads official hand-labeled split CSV files."""
    os.makedirs(dest_dir, exist_ok=True)
    split_files = [
        "flood_train_data.csv",
        "flood_valid_data.csv",
        "flood_test_data.csv",
        "flood_bolivia_data.csv",
    ]
    print(f"Fetching official dataset splits to: {dest_dir}")
    for s_file in split_files:
        url = f"{BASE_GCS_URL}/splits/flood_handlabeled/{s_file}"
        dest = os.path.join(dest_dir, s_file)
        success = download_file(url, dest)
        status = "OK" if success else "FAILED"
        print(f"  [{status}] {s_file}")


def download_samples(
    samples_dir: str,
    splits_dir: str,
    samples_per_event: int = 2,
    layers: Optional[List[str]] = None,
) -> List[str]:
    """
    Downloads a curated representative development sample subset spanning all flood events.
    Layers: S1Hand, S2Hand, LabelHand, JRCWaterHand.
    """
    if layers is None:
        layers = ["S1Hand", "S2Hand", "LabelHand", "JRCWaterHand"]

    download_splits(splits_dir)

    train_df = pd.read_csv(os.path.join(splits_dir, "flood_train_data.csv"), header=None, names=["s1", "label"])
    val_df = pd.read_csv(os.path.join(splits_dir, "flood_valid_data.csv"), header=None, names=["s1", "label"])
    test_df = pd.read_csv(os.path.join(splits_dir, "flood_test_data.csv"), header=None, names=["s1", "label"])
    bolivia_df = pd.read_csv(os.path.join(splits_dir, "flood_bolivia_data.csv"), header=None, names=["s1", "label"])

    all_df = pd.concat([train_df, val_df, test_df, bolivia_df]).drop_duplicates()
    all_df["event"] = all_df["s1"].apply(lambda x: x.split("_")[0])
    all_df["stem"] = all_df["s1"].apply(lambda x: x.replace("_S1Hand.tif", ""))

    selected_stems = []
    for event_name, grp in all_df.groupby("event"):
        selected_stems.extend(grp["stem"].head(samples_per_event).tolist())

    print(f"Downloading {len(selected_stems)} sample chips across {all_df['event'].nunique()} flood events...")

    for stem in tqdm(selected_stems, desc="Samples Progress"):
        for lyr in layers:
            fname = f"{stem}_{lyr}.tif"
            dest_path = os.path.join(samples_dir, lyr, fname)
            url = f"{BASE_GCS_URL}/data/flood_events/HandLabeled/{lyr}/{fname}"
            download_file(url, dest_path)

    print(f"Successfully downloaded development samples to: {samples_dir}")
    return selected_stems


def download_full_dataset(
    target_dir: str,
    splits_dir: str,
    layers: Optional[List[str]] = None,
) -> None:
    """
    Downloads the entire hand-labeled benchmark dataset (446 chips x requested layers).
    """
    if layers is None:
        layers = ["S1Hand", "S2Hand", "LabelHand", "JRCWaterHand"]

    download_splits(splits_dir)

    train_df = pd.read_csv(os.path.join(splits_dir, "flood_train_data.csv"), header=None, names=["s1", "label"])
    val_df = pd.read_csv(os.path.join(splits_dir, "flood_valid_data.csv"), header=None, names=["s1", "label"])
    test_df = pd.read_csv(os.path.join(splits_dir, "flood_test_data.csv"), header=None, names=["s1", "label"])
    bolivia_df = pd.read_csv(os.path.join(splits_dir, "flood_bolivia_data.csv"), header=None, names=["s1", "label"])

    all_df = pd.concat([train_df, val_df, test_df, bolivia_df]).drop_duplicates()
    stems = all_df["s1"].apply(lambda x: x.replace("_S1Hand.tif", "")).tolist()

    print(f"Starting full benchmark download: {len(stems)} chips x {len(layers)} layers = {len(stems) * len(layers)} files")

    for stem in tqdm(stems, desc="Full Dataset Download"):
        for lyr in layers:
            fname = f"{stem}_{lyr}.tif"
            dest_path = os.path.join(target_dir, lyr, fname)
            url = f"{BASE_GCS_URL}/data/flood_events/HandLabeled/{lyr}/{fname}"
            download_file(url, dest_path)

    print("Full benchmark dataset download completed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download Sen1Floods11 Dataset or Development Samples")
    parser.add_argument("--mode", choices=["splits", "samples", "full"], default="samples", help="Download mode")
    parser.add_argument("--data_dir", type=str, default="data/samples", help="Target data directory")
    parser.add_argument("--splits_dir", type=str, default="data/raw/splits", help="Target splits directory")
    parser.add_argument("--samples_per_event", type=int, default=2, help="Samples per flood event")
    args = parser.parse_args()

    if args.mode == "splits":
        download_splits(args.splits_dir)
    elif args.mode == "samples":
        download_samples(args.data_dir, args.splits_dir, samples_per_event=args.samples_per_event)
    elif args.mode == "full":
        download_full_dataset(args.data_dir, args.splits_dir)
