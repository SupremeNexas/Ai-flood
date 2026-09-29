"""
Loss functions for Flood Segmentation with Invalid/No-Data Masking.

Implements masked Binary Cross Entropy, masked Dice Loss, and combined BCE + Dice Loss
that strictly ignore pixels with target value -1 (clouds/sensor no-data).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional


class MaskedBCEWithLogitsLoss(nn.Module):
    """
    Binary Cross-Entropy Loss with Logits that masks out invalid pixels (target == -1).
    """

    def __init__(self, pos_weight: Optional[float] = None, ignore_index: int = -1):
        super().__init__()
        self.ignore_index = ignore_index
        self.pos_weight = torch.tensor([pos_weight]) if pos_weight is not None else None

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """
        logits: (B, H, W) raw unnormalized scores
        targets: (B, H, W) ground truth labels with {-1, 0, 1}
        """
        valid_mask = targets != self.ignore_index
        if not valid_mask.any():
            return logits.sum() * 0.0

        valid_logits = logits[valid_mask]
        valid_targets = targets[valid_mask].float()

        weight = self.pos_weight.to(logits.device) if self.pos_weight is not None else None
        return F.binary_cross_entropy_with_logits(valid_logits, valid_targets, pos_weight=weight)


class MaskedDiceLoss(nn.Module):
    """
    Dice Loss computed strictly on valid pixels (target != -1).
    Smooths region-level overlap to handle severe land/water class imbalance.
    """

    def __init__(self, smooth: float = 1e-6, ignore_index: int = -1):
        super().__init__()
        self.smooth = smooth
        self.ignore_index = ignore_index

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """
        logits: (B, H, W)
        targets: (B, H, W)
        """
        probs = torch.sigmoid(logits)
        valid_mask = targets != self.ignore_index

        if not valid_mask.any():
            return logits.sum() * 0.0

        # Mask out invalid pixels by setting both pred and target to 0 for invalid locations
        valid_mask_float = valid_mask.float()
        valid_probs = probs * valid_mask_float
        valid_targets = (targets == 1).float() * valid_mask_float

        # Compute per-sample Dice over valid regions then average across batch
        batch_size = logits.shape[0]
        dice_losses = []

        for i in range(batch_size):
            p_i = valid_probs[i].contiguous().view(-1)
            t_i = valid_targets[i].contiguous().view(-1)
            v_i = valid_mask_float[i].contiguous().view(-1)

            if v_i.sum() == 0:
                continue

            intersection = (p_i * t_i).sum()
            denominator = p_i.sum() + t_i.sum()

            dice = (2.0 * intersection + self.smooth) / (denominator + self.smooth)
            dice_losses.append(1.0 - dice)

        if not dice_losses:
            return logits.sum() * 0.0

        return torch.stack(dice_losses).mean()


class CombinedBCEDiceLoss(nn.Module):
    """
    Combined Masked BCE + Masked Dice Loss:
    Loss = alpha * BCE + beta * Dice
    """

    def __init__(
        self,
        alpha: float = 0.5,
        beta: float = 0.5,
        pos_weight: Optional[float] = None,
        smooth: float = 1e-6,
        ignore_index: int = -1,
    ):
        super().__init__()
        self.alpha = alpha
        self.beta = beta
        self.bce = MaskedBCEWithLogitsLoss(pos_weight=pos_weight, ignore_index=ignore_index)
        self.dice = MaskedDiceLoss(smooth=smooth, ignore_index=ignore_index)

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        bce_loss = self.bce(logits, targets)
        dice_loss = self.dice(logits, targets)
        return self.alpha * bce_loss + self.beta * dice_loss
