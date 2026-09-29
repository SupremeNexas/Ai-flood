"""
Unit tests for Sen1Floods11 PyTorch Dataset.
"""

import pytest
import torch
from src.data.dataset import Sen1Floods11Dataset, MODALITY_CHANNELS


@pytest.mark.parametrize("modality", ["s1", "s2_rgb", "s1_jrc", "s1_s2_rgb", "s1_s2_rgb_jrc"])
def test_dataset_modalities(modality):
    ds = Sen1Floods11Dataset(data_dir="data/samples", modality=modality)
    assert len(ds) > 0, f"No samples found for modality {modality}"

    expected_channels = MODALITY_CHANNELS[modality]
    assert ds.in_channels == expected_channels

    item = ds[0]
    assert "image" in item and "mask" in item and "metadata" in item

    image = item["image"]
    mask = item["mask"]
    meta = item["metadata"]

    assert isinstance(image, torch.Tensor)
    assert isinstance(mask, torch.Tensor)

    assert image.shape == (expected_channels, 512, 512)
    assert mask.shape == (512, 512)

    assert image.dtype == torch.float32
    assert mask.dtype == torch.int64

    # Verify normalization bounds
    assert image.min() >= 0.0 and image.max() <= 1.0

    # Verify mask values are in {-1, 0, 1}
    unq_vals = torch.unique(mask).tolist()
    for v in unq_vals:
        assert v in [-1, 0, 1], f"Unexpected mask value {v}"

    assert meta["in_channels"] == expected_channels
    assert meta["height"] == 512
    assert meta["width"] == 512
