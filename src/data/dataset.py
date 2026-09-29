"""
Sen1Floods11 PyTorch Dataset and DataLoader Module.

Provides memory-efficient raster loading, multi-modal band combinations,
synchronized augmentations, and deterministic batch creation.
"""

import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import rasterio
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from typing import Dict, List, Optional, Tuple, Any, Union

from src.data.preprocessing import FloodPreprocessor, SynchronizedAugmentation
from src.data.validation import discover_chips


MODALITY_CHANNELS = {
    "s1": 2,               # VV, VH
    "s2_rgb": 3,           # Red, Green, Blue
    "s1_jrc": 3,           # VV, VH, JRC Permanent Water Baseline
    "s1_s2_rgb": 5,        # VV, VH, Red, Green, Blue
    "s1_s2_rgb_jrc": 6,    # VV, VH, Red, Green, Blue, JRC Permanent Water Baseline
}


class Sen1Floods11Dataset(Dataset):
    """
    PyTorch Dataset for Sen1Floods11 satellite flood segmentation.
    """

    def __init__(
        self,
        data_dir: str,
        split_file: Optional[str] = None,
        modality: str = "s1",
        transform: Optional[SynchronizedAugmentation] = None,
        preprocessor: Optional[FloodPreprocessor] = None,
        return_metadata: bool = True,
        image_size: Optional[int] = None,
    ):
        self.data_dir = data_dir
        self.split_file = split_file
        self.modality = modality.lower()
        self.transform = transform
        self.preprocessor = preprocessor or FloodPreprocessor()
        self.return_metadata = return_metadata
        self.image_size = image_size

        if self.modality not in MODALITY_CHANNELS:
            raise ValueError(f"Unsupported modality '{self.modality}'. Choose from: {list(MODALITY_CHANNELS.keys())}")

        self.in_channels = MODALITY_CHANNELS[self.modality]
        self.samples = self._load_sample_manifest()

    def _load_sample_manifest(self) -> List[Dict[str, str]]:
        """
        Loads and verifies the list of sample paths.
        Uses split_file if provided; otherwise discovers all valid matching chips in data_dir.
        """
        all_discovered = discover_chips(self.data_dir)
        samples = []

        if self.split_file and os.path.exists(self.split_file):
            df = pd.read_csv(self.split_file, header=None, names=["s1", "label"])
            for _, row in df.iterrows():
                stem = row["s1"].replace("_S1Hand.tif", "")
                if stem in all_discovered:
                    # Check that required layers for this modality exist
                    layer_dict = all_discovered[stem]
                    if self._has_required_layers(layer_dict):
                        samples.append({"stem": stem, **layer_dict})
        else:
            for stem, layer_dict in all_discovered.items():
                if self._has_required_layers(layer_dict):
                    samples.append({"stem": stem, **layer_dict})

        return samples

    def _has_required_layers(self, layer_dict: Dict[str, str]) -> bool:
        """Verifies that all layers needed for the selected modality and label exist."""
        if "LabelHand" not in layer_dict:
            return False
        if "s1" in self.modality and "S1Hand" not in layer_dict:
            return False
        if "s2" in self.modality and "S2Hand" not in layer_dict:
            return False
        if "jrc" in self.modality and "JRCWaterHand" not in layer_dict:
            return False
        return True

    def __len__(self) -> int:
        return len(self.samples)

    def _load_raster(self, path: str) -> np.ndarray:
        """Loads a GeoTIFF raster file via rasterio."""
        with rasterio.open(path) as src:
            data = src.read()
        return data

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        sample_info = self.samples[idx]
        stem = sample_info["stem"]
        event = stem.split("_")[0]

        # 1. Load Label Mask
        raw_mask = self._load_raster(sample_info["LabelHand"])
        mask = self.preprocessor.process_mask(raw_mask)

        # 2. Load and compose input image channels according to selected modality
        channel_arrays = []

        if "s1" in self.modality:
            raw_s1 = self._load_raster(sample_info["S1Hand"])
            norm_s1 = self.preprocessor.normalize_s1(raw_s1)
            channel_arrays.append(norm_s1)

        if "s2" in self.modality:
            raw_s2 = self._load_raster(sample_info["S2Hand"])
            norm_s2_rgb = self.preprocessor.extract_s2_rgb(raw_s2)
            channel_arrays.append(norm_s2_rgb)

        if "jrc" in self.modality:
            raw_jrc = self._load_raster(sample_info["JRCWaterHand"])
            norm_jrc = self.preprocessor.normalize_jrc(raw_jrc)
            channel_arrays.append(norm_jrc)

        # Stack into (C, H, W)
        image = np.concatenate(channel_arrays, axis=0)

        # 3. Apply spatial downsampling if image_size specified (e.g. 256x256)
        if self.image_size is not None and image.shape[1] > self.image_size:
            stride = image.shape[1] // self.image_size
            image = image[:, ::stride, ::stride]
            mask = mask[::stride, ::stride]

        # 4. Apply Synchronized Augmentation if enabled
        if self.transform is not None:
            image, mask, _ = self.transform(image, mask)

        # 5. Convert to PyTorch Tensors
        image_tensor = torch.from_numpy(image).float()
        mask_tensor = torch.from_numpy(mask).long()

        result: Dict[str, Any] = {
            "image": image_tensor,
            "mask": mask_tensor,
        }

        if self.return_metadata:
            valid_mask = mask != self.preprocessor.ignore_index
            valid_pixels = int(valid_mask.sum())
            water_pixels = int((mask == 1).sum())
            flood_ratio = float(water_pixels / valid_pixels) if valid_pixels > 0 else 0.0

            result["metadata"] = {
                "stem": stem,
                "event": event,
                "modality": self.modality,
                "in_channels": self.in_channels,
                "height": image_tensor.shape[1],
                "width": image_tensor.shape[2],
                "valid_pixels": valid_pixels,
                "water_pixels": water_pixels,
                "flood_ratio": flood_ratio,
            }

        return result


def create_dataloaders(
    data_dir: str,
    splits_dir: Optional[str] = None,
    modality: str = "s1",
    batch_size: int = 4,
    num_workers: int = 0,
    enable_augmentation: bool = True,
    image_size: Optional[int] = None,
) -> Dict[str, DataLoader]:
    """
    Convenience factory to build PyTorch DataLoaders for train, valid, test, and bolivia splits.
    """
    loaders = {}
    preprocessor = FloodPreprocessor()

    train_aug = SynchronizedAugmentation(hflip_prob=0.5, vflip_prob=0.5, rot90_prob=0.5) if enable_augmentation else None

    split_mapping = {
        "train": "flood_train_data.csv",
        "val": "flood_valid_data.csv",
        "test": "flood_test_data.csv",
        "bolivia": "flood_bolivia_data.csv",
    }

    for split_name, split_filename in split_mapping.items():
        split_path = os.path.join(splits_dir, split_filename) if splits_dir else None
        aug = train_aug if split_name == "train" else None
        shuffle = (split_name == "train")

        ds = Sen1Floods11Dataset(
            data_dir=data_dir,
            split_file=split_path,
            modality=modality,
            transform=aug,
            preprocessor=preprocessor,
            image_size=image_size,
        )

        if len(ds) > 0:
            loaders[split_name] = DataLoader(
                ds,
                batch_size=min(batch_size, len(ds)),
                shuffle=shuffle,
                num_workers=num_workers,
                pin_memory=torch.cuda.is_available(),
                drop_last=(split_name == "train" and len(ds) > batch_size),
            )

    return loaders
