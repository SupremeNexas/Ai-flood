"""
Sen1Floods11 Image Preprocessing and Synchronized Augmentation Module.

Provides robust, domain-specific normalization for SAR backscatter,
Sentinel-2 optical reflectance, JRC baseline water, and interpolation-safe
mask processing with synchronized spatial transforms.
"""

import torch
import numpy as np
from typing import Dict, Tuple, Optional, Union, Any


class FloodPreprocessor:
    """
    Handles domain-specific normalization and conversion for satellite imagery.
    """

    def __init__(
        self,
        s1_clip_min: float = -35.0,
        s1_clip_max: float = 5.0,
        s2_scale_factor: float = 10000.0,
        s2_clip_max: float = 0.4,
        ignore_index: int = -1,
    ):
        self.s1_clip_min = s1_clip_min
        self.s1_clip_max = s1_clip_max
        self.s2_scale_factor = s2_scale_factor
        self.s2_clip_max = s2_clip_max
        self.ignore_index = ignore_index

    def normalize_s1(self, s1_data: np.ndarray) -> np.ndarray:
        """
        Normalizes Sentinel-1 SAR (VV, VH) dB backscatter data.
        1. Replaces NaNs/Infs with s1_clip_min.
        2. Clips backscatter to [s1_clip_min, s1_clip_max] (e.g. [-35, 5] dB).
        3. Linearly scales to [0.0, 1.0].

        Input shape: (2, H, W) or (H, W, 2)
        Output shape matches input, dtype float32 in [0, 1].
        """
        data = np.nan_to_num(s1_data, nan=self.s1_clip_min, posinf=self.s1_clip_max, neginf=self.s1_clip_min)
        clipped = np.clip(data, self.s1_clip_min, self.s1_clip_max)
        normalized = (clipped - self.s1_clip_min) / (self.s1_clip_max - self.s1_clip_min)
        return normalized.astype(np.float32)

    def normalize_s2(self, s2_data: np.ndarray, bands: Optional[Tuple[int, ...]] = None) -> np.ndarray:
        """
        Normalizes Sentinel-2 Optical MSI imagery.
        1. If bands is specified (e.g. (3, 2, 1) for RGB from 13-band stack), extracts those channels.
        2. Scales raw integer TOA reflectance by dividing by scale factor (10,000).
        3. Clips to [0.0, s2_clip_max] and scales to [0.0, 1.0].

        Input shape: (C, H, W) or (13, H, W)
        """
        if bands is not None:
            # Note: in 13-band Sen1Floods11: Band 0=B1, 1=B2(Blue), 2=B3(Green), 3=B4(Red), 7=B8(NIR)
            data = s2_data[list(bands)]
        else:
            data = s2_data

        data = np.nan_to_num(data, nan=0.0, posinf=self.s2_scale_factor, neginf=0.0)
        toa = data.astype(np.float32) / self.s2_scale_factor
        clipped = np.clip(toa, 0.0, self.s2_clip_max)
        normalized = clipped / self.s2_clip_max
        return normalized.astype(np.float32)

    def extract_s2_rgb(self, s2_data: np.ndarray) -> np.ndarray:
        """
        Extracts True-Color RGB bands from 13-band Sentinel-2 stack:
        Band 3 (Red: B4), Band 2 (Green: B3), Band 1 (Blue: B2).
        Returns shape (3, H, W) normalized in [0, 1].
        """
        return self.normalize_s2(s2_data, bands=(3, 2, 1))

    def normalize_jrc(self, jrc_data: np.ndarray) -> np.ndarray:
        """
        Normalizes JRC historical permanent water baseline.
        Maps {0 -> 0.0 (Dry land), 1 -> 1.0 (Permanent water)}.
        Shape: (1, H, W) float32.
        """
        if jrc_data.ndim == 2:
            jrc_data = jrc_data[np.newaxis, ...]
        binary = (jrc_data > 0).astype(np.float32)
        return binary

    def process_mask(self, mask_data: np.ndarray) -> np.ndarray:
        """
        Validates and formats the ground truth segmentation mask:
        -1: Invalid / No-data / Cloud
         0: Non-water / Dry
         1: Flood / Surface water

        Returns int64 tensor target of shape (H, W) or (1, H, W).
        """
        if mask_data.ndim == 3 and mask_data.shape[0] == 1:
            mask_data = mask_data[0]
        mask = mask_data.astype(np.int64)
        # Ensure only {-1, 0, 1} are present
        mask[~np.isin(mask, [-1, 0, 1])] = self.ignore_index
        return mask


class SynchronizedAugmentation:
    """
    Applies spatially synchronized geometric augmentations to multi-channel
    satellite imagery and ground-truth masks.
    Guarantees no spatial misalignment or interpolation distortion.
    """

    def __init__(
        self,
        hflip_prob: float = 0.5,
        vflip_prob: float = 0.5,
        rot90_prob: float = 0.5,
        random_crop: bool = False,
        crop_size: Tuple[int, int] = (256, 256),
    ):
        self.hflip_prob = hflip_prob
        self.vflip_prob = vflip_prob
        self.rot90_prob = rot90_prob
        self.random_crop = random_crop
        self.crop_size = crop_size

    def __call__(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        aux: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, np.ndarray, Optional[np.ndarray]]:
        """
        Applies synchronized transforms.
        image: (C, H, W)
        mask: (H, W) or (1, H, W)
        aux: Optional auxiliary tensor, e.g. JRC baseline (C_aux, H, W)
        """
        # 1. Random Crop
        if self.random_crop:
            c, h, w = image.shape
            ch, cw = self.crop_size
            if h > ch and w > cw:
                top = np.random.randint(0, h - ch + 1)
                left = np.random.randint(0, w - cw + 1)
                image = image[:, top : top + ch, left : left + cw]
                if mask.ndim == 3:
                    mask = mask[:, top : top + ch, left : left + cw]
                else:
                    mask = mask[top : top + ch, left : left + cw]
                if aux is not None:
                    aux = aux[:, top : top + ch, left : left + cw]

        # 2. Horizontal Flip
        if np.random.rand() < self.hflip_prob:
            image = np.flip(image, axis=-1).copy()
            mask = np.flip(mask, axis=-1).copy()
            if aux is not None:
                aux = np.flip(aux, axis=-1).copy()

        # 3. Vertical Flip
        if np.random.rand() < self.vflip_prob:
            image = np.flip(image, axis=-2).copy()
            mask = np.flip(mask, axis=-2).copy()
            if aux is not None:
                aux = np.flip(aux, axis=-2).copy()

        # 4. Random 90-degree Rotations (0, 90, 180, 270 deg)
        if np.random.rand() < self.rot90_prob:
            k = np.random.randint(1, 4)
            image = np.rot90(image, k, axes=(-2, -1)).copy()
            mask = np.rot90(mask, k, axes=(-2, -1)).copy()
            if aux is not None:
                aux = np.rot90(aux, k, axes=(-2, -1)).copy()

        return image, mask, aux
