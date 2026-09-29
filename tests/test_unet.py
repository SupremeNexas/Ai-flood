"""
Unit tests for U-Net Architecture.
"""

import pytest
import torch
from src.models.unet import UNet, build_unet


@pytest.mark.parametrize("in_channels", [2, 3, 5, 6])
def test_unet_forward_pass_channels(in_channels):
    model = UNet(in_channels=in_channels, num_classes=1, features=(16, 32, 64, 128, 256))
    x = torch.randn(2, in_channels, 128, 128)
    out = model(x)

    assert out.shape == (2, 128, 128), f"Expected output shape (2, 128, 128), got {out.shape}"
    assert not torch.isnan(out).any(), "Output contains NaN values"


@pytest.mark.parametrize("modality, expected_channels", [
    ("s1", 2),
    ("s2_rgb", 3),
    ("s1_jrc", 3),
    ("s1_s2_rgb", 5),
    ("s1_s2_rgb_jrc", 6),
])
def test_build_unet_factory(modality, expected_channels):
    model = build_unet(modality=modality)
    assert model.in_channels == expected_channels
    assert model.get_num_parameters() > 0


def test_unet_gelu_and_transpose():
    model = UNet(in_channels=2, num_classes=1, features=(16, 32, 64, 128, 256), bilinear=False, activation="gelu")
    x = torch.randn(1, 2, 64, 64)
    out = model(x)
    assert out.shape == (1, 64, 64)
