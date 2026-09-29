"""
Unit tests for data preprocessing and synchronized augmentation.
"""

import numpy as np
import pytest
import torch
from src.data.preprocessing import FloodPreprocessor, SynchronizedAugmentation


def test_s1_normalization():
    prep = FloodPreprocessor(s1_clip_min=-35.0, s1_clip_max=5.0)
    # Synthetic S1 data with extreme dB values and NaNs
    raw_s1 = np.array([[-50.0, -35.0, -15.0, 5.0, 20.0, np.nan]], dtype=np.float32)
    norm = prep.normalize_s1(raw_s1)

    assert norm.shape == raw_s1.shape
    assert norm.dtype == np.float32
    assert np.all(norm >= 0.0) and np.all(norm <= 1.0)
    # -50 clipped to -35 -> 0.0; -35 -> 0.0; 5 -> 1.0; 20 clipped to 5 -> 1.0; nan -> 0.0
    assert norm[0, 0] == 0.0
    assert norm[0, 1] == 0.0
    assert norm[0, 3] == 1.0
    assert norm[0, 4] == 1.0
    assert norm[0, 5] == 0.0


def test_s2_normalization():
    prep = FloodPreprocessor(s2_scale_factor=10000.0, s2_clip_max=0.4)
    # 13-band synthetic optical stack (13, 10, 10)
    raw_s2 = np.full((13, 10, 10), fill_value=2000, dtype=np.int16)
    rgb = prep.extract_s2_rgb(raw_s2)

    assert rgb.shape == (3, 10, 10)
    assert rgb.dtype == np.float32
    assert np.all(rgb >= 0.0) and np.all(rgb <= 1.0)
    # 2000 / 10000 = 0.2 -> 0.2 / 0.4 = 0.5
    assert np.allclose(rgb, 0.5)


def test_mask_processing():
    prep = FloodPreprocessor(ignore_index=-1)
    raw_mask = np.array([[-1, 0, 1, 99]], dtype=np.int16)
    processed = prep.process_mask(raw_mask)

    assert processed.dtype == np.int64
    assert processed[0, 0] == -1
    assert processed[0, 1] == 0
    assert processed[0, 2] == 1
    assert processed[0, 3] == -1  # 99 mapped to ignore_index -1


def test_synchronized_augmentation():
    aug = SynchronizedAugmentation(hflip_prob=1.0, vflip_prob=0.0, rot90_prob=0.0)
    image = np.array([[[1.0, 2.0], [3.0, 4.0]]])  # shape (1, 2, 2)
    mask = np.array([[10, 20], [30, 40]])          # shape (2, 2)

    aug_img, aug_mask, _ = aug(image, mask)

    # Both image and mask must be horizontally flipped identically
    assert np.array_equal(aug_img, np.array([[[2.0, 1.0], [4.0, 3.0]]]))
    assert np.array_equal(aug_mask, np.array([[20, 10], [40, 30]]))
