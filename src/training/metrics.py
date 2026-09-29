"""
Semantic Segmentation Evaluation Metrics for Flood Detection.

Calculates IoU, Dice Score, Precision, Recall, and F1 Score strictly over valid pixels,
explicitly excluding invalid / cloud pixels (target == -1).
"""

import torch
import numpy as np
from typing import Dict, Any, Optional, Union, Tuple


def compute_confusion_matrix_elements(
    logits: torch.Tensor,
    targets: torch.Tensor,
    threshold: float = 0.0,
    ignore_index: int = -1,
) -> Tuple[int, int, int, int, int, int]:
    """
    Computes TP, FP, FN, TN, valid_pixels, and ground-truth water_pixels
    on valid regions where target != ignore_index.

    Args:
        logits: (B, H, W) raw model outputs
        targets: (B, H, W) ground truth labels {-1, 0, 1}
        threshold: Decision boundary on logits (0.0 corresponds to sigmoid probability 0.5)
        ignore_index: Pixel value to exclude (-1)

    Returns:
        (TP, FP, FN, TN, valid_pixels, water_pixels)
    """
    valid_mask = targets != ignore_index
    if not valid_mask.any():
        return 0, 0, 0, 0, 0, 0

    preds = (logits > threshold) & valid_mask
    ground_truth = (targets == 1) & valid_mask
    background = (targets == 0) & valid_mask

    tp = int((preds & ground_truth).sum().item())
    fp = int((preds & background).sum().item())
    fn = int((~preds & ground_truth).sum().item())
    tn = int((~preds & background).sum().item())
    valid_pixels = int(valid_mask.sum().item())
    water_pixels = int(ground_truth.sum().item())

    return tp, fp, fn, tn, valid_pixels, water_pixels


class SegmentationMetrics:
    """
    Metric tracker for accumulation over an evaluation epoch or test split.
    """

    def __init__(self, threshold: float = 0.0, ignore_index: int = -1, eps: float = 1e-7):
        self.threshold = threshold
        self.ignore_index = ignore_index
        self.eps = eps
        self.reset()

    def reset(self):
        self.tp = 0
        self.fp = 0
        self.fn = 0
        self.tn = 0
        self.valid_pixels = 0
        self.water_pixels = 0
        self.total_samples = 0

    def update(self, logits: torch.Tensor, targets: torch.Tensor):
        tp, fp, fn, tn, valid_px, water_px = compute_confusion_matrix_elements(
            logits=logits,
            targets=targets,
            threshold=self.threshold,
            ignore_index=self.ignore_index,
        )
        self.tp += tp
        self.fp += fp
        self.fn += fn
        self.tn += tn
        self.valid_pixels += valid_px
        self.water_pixels += water_px
        self.total_samples += logits.shape[0]

    def compute(self) -> Dict[str, float]:
        """
        Computes global dataset-level metrics.
        Formulas:
          IoU = TP / (TP + FP + FN + eps)
          Dice = 2*TP / (2*TP + FP + FN + eps)
          Precision = TP / (TP + FP + eps)
          Recall = TP / (TP + FN + eps)
          F1 = Dice
        """
        tp = float(self.tp)
        fp = float(self.fp)
        fn = float(self.fn)
        tn = float(self.tn)

        iou = tp / (tp + fp + fn + self.eps)
        dice = (2.0 * tp) / (2.0 * tp + fp + fn + self.eps)
        precision = tp / (tp + fp + self.eps)
        recall = tp / (tp + fn + self.eps)
        f1 = dice
        accuracy = (tp + tn) / (tp + fp + fn + tn + self.eps)

        return {
            "iou": float(round(iou, 4)),
            "dice": float(round(dice, 4)),
            "precision": float(round(precision, 4)),
            "recall": float(round(recall, 4)),
            "f1": float(round(f1, 4)),
            "accuracy": float(round(accuracy, 4)),
            "tp": int(self.tp),
            "fp": int(self.fp),
            "fn": int(self.fn),
            "tn": int(self.tn),
            "valid_pixels": int(self.valid_pixels),
            "water_pixels": int(self.water_pixels),
        }
