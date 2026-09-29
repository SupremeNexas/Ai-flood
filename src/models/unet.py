"""
U-Net Semantic Segmentation Architecture for Satellite Flood Mapping.

Implements an encoder-decoder architecture with skip connections,
configurable input channels, feature widths, activation functions,
and normalization layers.
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

# Ensure project root is in sys.path
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import torch
import torch.nn as nn
import torch.nn.functional as F


def get_norm_layer(norm_type: str, num_channels: int) -> nn.Module:
    """Helper to return appropriate normalization layer."""
    if norm_type.lower() == "group":
        # Ensure num_groups divides num_channels
        num_groups = min(8, num_channels)
        while num_channels % num_groups != 0 and num_groups > 1:
            num_groups -= 1
        return nn.GroupNorm(num_groups=num_groups, num_channels=num_channels)
    return nn.BatchNorm2d(num_channels)


class DoubleConv(nn.Module):
    """
    Standard double convolution block with configurable normalization:
    [Conv2d -> Norm -> Activation -> Conv2d -> Norm -> Activation]
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        mid_channels: Optional[int] = None,
        activation: str = "relu",
        norm_type: str = "group",
        dropout_prob: float = 0.0,
    ):
        super().__init__()
        if mid_channels is None:
            mid_channels = out_channels

        act_layer = nn.GELU() if activation.lower() == "gelu" else nn.ReLU(inplace=True)

        layers: List[nn.Module] = [
            nn.Conv2d(in_channels, mid_channels, kernel_size=3, padding=1, bias=False),
            get_norm_layer(norm_type, mid_channels),
            act_layer,
        ]

        if dropout_prob > 0.0:
            layers.append(nn.Dropout2d(p=dropout_prob))

        layers.extend([
            nn.Conv2d(mid_channels, out_channels, kernel_size=3, padding=1, bias=False),
            get_norm_layer(norm_type, out_channels),
            act_layer,
        ])

        self.double_conv = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.double_conv(x)


class Down(nn.Module):
    """Downscaling with MaxPool2d then DoubleConv."""

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        activation: str = "relu",
        norm_type: str = "group",
        dropout_prob: float = 0.0,
    ):
        super().__init__()
        self.maxpool_conv = nn.Sequential(
            nn.MaxPool2d(kernel_size=2, stride=2),
            DoubleConv(
                in_channels=in_channels,
                out_channels=out_channels,
                activation=activation,
                norm_type=norm_type,
                dropout_prob=dropout_prob,
            ),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.maxpool_conv(x)


class Up(nn.Module):
    """Upscaling then DoubleConv with skip connection concatenation."""

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        bilinear: bool = True,
        activation: str = "relu",
        norm_type: str = "group",
        dropout_prob: float = 0.0,
    ):
        super().__init__()
        self.bilinear = bilinear

        if bilinear:
            self.up = nn.Upsample(scale_factor=2, mode="bilinear", align_corners=True)
            self.conv = DoubleConv(
                in_channels=in_channels,
                out_channels=out_channels,
                mid_channels=in_channels // 2,
                activation=activation,
                norm_type=norm_type,
                dropout_prob=dropout_prob,
            )
        else:
            self.up = nn.ConvTranspose2d(
                in_channels=in_channels,
                out_channels=in_channels // 2,
                kernel_size=2,
                stride=2,
            )
            self.conv = DoubleConv(
                in_channels=in_channels,
                out_channels=out_channels,
                activation=activation,
                norm_type=norm_type,
                dropout_prob=dropout_prob,
            )

    def forward(self, x1: torch.Tensor, x2: torch.Tensor) -> torch.Tensor:
        x1 = self.up(x1)

        diff_y = x2.size()[2] - x1.size()[2]
        diff_x = x2.size()[3] - x1.size()[3]

        if diff_y != 0 or diff_x != 0:
            x1 = F.pad(
                x1,
                [diff_x // 2, diff_x - diff_x // 2, diff_y // 2, diff_y - diff_y // 2],
            )

        x = torch.cat([x2, x1], dim=1)
        return self.conv(x)


class OutConv(nn.Module):
    """Final 1x1 convolution mapping feature map to class logits."""

    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.conv(x)


class UNet(nn.Module):
    """
    Standard U-Net architecture for satellite semantic segmentation.

    Args:
        in_channels: Number of input channels (e.g. 2 for S1, 3 for RGB, 5 for S1+RGB, 6 for S1+RGB+JRC).
        num_classes: Number of output channels (1 for binary segmentation logits).
        features: Channel progression across encoder stages. Default: (32, 64, 128, 256, 512).
        bilinear: If True, uses bilinear interpolation for upsampling; otherwise uses ConvTranspose2d.
        activation: Activation function ('relu' or 'gelu').
        norm_type: Normalization type ('group' for GroupNorm or 'batch' for BatchNorm).
        dropout_prob: Dropout probability applied at the bottleneck stage.
    """

    def __init__(
        self,
        in_channels: int = 2,
        num_classes: int = 1,
        features: Tuple[int, ...] = (32, 64, 128, 256, 512),
        bilinear: bool = True,
        activation: str = "relu",
        norm_type: str = "group",
        dropout_prob: float = 0.1,
    ):
        super().__init__()
        self.in_channels = in_channels
        self.num_classes = num_classes
        self.features = features
        self.bilinear = bilinear
        self.activation = activation
        self.norm_type = norm_type

        f0, f1, f2, f3, f4 = features

        # Encoder (Contracting Path)
        self.inc = DoubleConv(in_channels, f0, activation=activation, norm_type=norm_type)
        self.down1 = Down(f0, f1, activation=activation, norm_type=norm_type)
        self.down2 = Down(f1, f2, activation=activation, norm_type=norm_type)
        self.down3 = Down(f2, f3, activation=activation, norm_type=norm_type)
        factor = 2 if bilinear else 1
        self.down4 = Down(f3, f4 // factor, activation=activation, norm_type=norm_type, dropout_prob=dropout_prob)

        # Decoder (Expanding Path)
        self.up1 = Up(f4, f3 // factor, bilinear=bilinear, activation=activation, norm_type=norm_type)
        self.up2 = Up(f3, f2 // factor, bilinear=bilinear, activation=activation, norm_type=norm_type)
        self.up3 = Up(f2, f1 // factor, bilinear=bilinear, activation=activation, norm_type=norm_type)
        self.up4 = Up(f1, f0, bilinear=bilinear, activation=activation, norm_type=norm_type)

        # Output head
        self.outc = OutConv(f0, num_classes)

        # Initialize weights
        self._init_weights()

    def _init_weights(self):
        """Kaiming/He normal initialization for convolutional layers."""
        for m in self.modules():
            if isinstance(m, (nn.Conv2d, nn.ConvTranspose2d)):
                nn.init.kaiming_normal_(m.weight, mode="fan_out", nonlinearity="relu")
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0.0)
            elif isinstance(m, (nn.BatchNorm2d, nn.GroupNorm)):
                nn.init.constant_(m.weight, 1.0)
                nn.init.constant_(m.bias, 0.0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        Input: Tensor of shape (B, in_channels, H, W)
        Output: Logits tensor of shape (B, H, W) for binary segmentation.
        """
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)

        x = self.up1(x5, x4)
        x = self.up2(x, x3)
        x = self.up3(x, x2)
        x = self.up4(x, x1)
        logits = self.outc(x)

        if self.num_classes == 1:
            return logits.squeeze(1)  # (B, H, W)
        return logits

    def get_num_parameters(self) -> int:
        """Returns the total number of trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


def build_unet(
    modality: str = "s1",
    in_channels: Optional[int] = None,
    features: Tuple[int, ...] = (32, 64, 128, 256, 512),
    activation: str = "relu",
    norm_type: str = "group",
    dropout_prob: float = 0.1,
    bilinear: bool = True,
) -> UNet:
    """
    Factory function to build a U-Net model matched to the given modality.
    """
    channel_map = {
        "s1": 2,
        "s2_rgb": 3,
        "s1_jrc": 3,
        "s1_s2_rgb": 5,
        "s1_s2_rgb_jrc": 6,
    }

    if in_channels is None:
        in_channels = channel_map.get(modality.lower(), 2)

    return UNet(
        in_channels=in_channels,
        num_classes=1,
        features=features,
        bilinear=bilinear,
        activation=activation,
        norm_type=norm_type,
        dropout_prob=dropout_prob,
    )
