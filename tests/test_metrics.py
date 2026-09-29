"""
Unit tests for Segmentation Metrics.
"""

import pytest
import torch
from src.training.metrics import compute_confusion_matrix_elements, SegmentationMetrics


def test_confusion_matrix_elements():
    # 2x2 grid
    # Target: [[1, 0], [1, -1]]
    # Preds:  [[1, 0], [0, 1]] (Logits: [[2.0, -2.0], [-2.0, 2.0]])
    logits = torch.tensor([[[2.0, -2.0], [-2.0, 2.0]]])
    targets = torch.tensor([[[1, 0], [1, -1]]], dtype=torch.int64)

    tp, fp, fn, tn, valid_px, water_px = compute_confusion_matrix_elements(
        logits, targets, threshold=0.0, ignore_index=-1
    )

    # Valid pixels = 3 (one is -1)
    # [0,0]: target=1, pred=1 -> TP
    # [0,1]: target=0, pred=0 -> TN
    # [1,0]: target=1, pred=0 -> FN
    # [1,1]: target=-1 (ignored)
    assert tp == 1
    assert fp == 0
    assert fn == 1
    assert tn == 1
    assert valid_px == 3
    assert water_px == 2


def test_segmentation_metrics_calculation():
    metrics = SegmentationMetrics(threshold=0.0, ignore_index=-1)
    logits = torch.tensor([[[2.0, -2.0], [-2.0, 2.0]]])
    targets = torch.tensor([[[1, 0], [1, -1]]], dtype=torch.int64)

    metrics.update(logits, targets)
    results = metrics.compute()

    # TP=1, FP=0, FN=1, TN=1
    # IoU = 1 / (1 + 0 + 1) = 0.5
    # Dice = 2*1 / (2*1 + 0 + 1) = 2/3 = 0.6667
    # Precision = 1 / (1 + 0) = 1.0
    # Recall = 1 / (1 + 1) = 0.5
    assert results["iou"] == 0.5
    assert results["dice"] == pytest.approx(0.6667, abs=1e-3)
    assert results["precision"] == 1.0
    assert results["recall"] == 0.5
    assert results["f1"] == pytest.approx(0.6667, abs=1e-3)
    assert results["valid_pixels"] == 3
    assert results["water_pixels"] == 2
