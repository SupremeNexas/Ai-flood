"""
Unit tests for Masked Loss Functions.
"""

import pytest
import torch
from src.training.losses import MaskedBCEWithLogitsLoss, MaskedDiceLoss, CombinedBCEDiceLoss


def test_masked_bce_loss():
    loss_fn = MaskedBCEWithLogitsLoss(ignore_index=-1)
    # Logits and target where half the pixels are invalid (-1)
    logits = torch.tensor([[[2.0, -2.0], [2.0, -2.0]]], requires_grad=True)
    targets = torch.tensor([[[1, 0], [-1, -1]]], dtype=torch.int64)

    loss = loss_fn(logits, targets)
    loss.backward()

    assert not torch.isnan(loss), "Loss is NaN"
    assert loss.item() > 0.0
    assert logits.grad is not None
    # Gradients on invalid positions must be zero
    assert logits.grad[0, 1, 0].item() == 0.0
    assert logits.grad[0, 1, 1].item() == 0.0


def test_masked_dice_loss():
    loss_fn = MaskedDiceLoss(ignore_index=-1)
    # Perfect prediction on valid pixels
    logits = torch.tensor([[[10.0, -10.0], [0.0, 0.0]]], requires_grad=True)
    targets = torch.tensor([[[1, 0], [-1, -1]]], dtype=torch.int64)

    loss = loss_fn(logits, targets)
    assert not torch.isnan(loss)
    assert loss.item() < 0.1, "Dice loss should be near 0 for near-perfect prediction"


def test_combined_bce_dice_loss():
    loss_fn = CombinedBCEDiceLoss(alpha=0.5, beta=0.5, ignore_index=-1)
    logits = torch.randn(2, 64, 64, requires_grad=True)
    targets = torch.randint(low=-1, high=2, size=(2, 64, 64))

    loss = loss_fn(logits, targets)
    loss.backward()

    assert not torch.isnan(loss)
    assert logits.grad is not None


def test_all_invalid_mask_safety():
    loss_fn = CombinedBCEDiceLoss(ignore_index=-1)
    logits = torch.randn(1, 32, 32, requires_grad=True)
    targets = torch.full((1, 32, 32), fill_value=-1, dtype=torch.int64)

    loss = loss_fn(logits, targets)
    loss.backward()

    assert loss.item() == 0.0
    assert not torch.isnan(loss)
