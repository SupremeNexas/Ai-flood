"""
Early Stopping and Checkpointing Utility for Model Training.
"""

import os
import torch
import numpy as np
from typing import Dict, Any, Optional


class EarlyStopping:
    """
    Early stopping handler that monitors validation metrics and triggers checkpoint saves.
    """

    def __init__(
        self,
        patience: int = 10,
        min_delta: float = 1e-4,
        mode: str = "max",
        checkpoint_path: Optional[str] = None,
        verbose: bool = True,
    ):
        self.patience = patience
        self.min_delta = min_delta
        self.mode = mode.lower()
        self.checkpoint_path = checkpoint_path
        self.verbose = verbose

        self.counter = 0
        self.best_score: Optional[float] = None
        self.early_stop = False
        self.best_epoch = 0

    def __call__(
        self,
        current_score: float,
        epoch: int,
        checkpoint_dict: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Updates tracking and returns True if a new best score was achieved.
        """
        if self.mode == "min":
            score = -current_score
        else:
            score = current_score

        if self.best_score is None:
            self.best_score = score
            self.best_epoch = epoch
            self._save_checkpoint(checkpoint_dict)
            return True

        if score < self.best_score + self.min_delta:
            self.counter += 1
            if self.verbose:
                print(f"EarlyStopping counter: {self.counter} out of {self.patience}")
            if self.counter >= self.patience:
                self.early_stop = True
            return False
        else:
            self.best_score = score
            self.best_epoch = epoch
            self.counter = 0
            self._save_checkpoint(checkpoint_dict)
            return True

    def _save_checkpoint(self, checkpoint_dict: Optional[Dict[str, Any]]):
        if self.checkpoint_path and checkpoint_dict:
            os.makedirs(os.path.dirname(self.checkpoint_path), exist_ok=True)
            torch.save(checkpoint_dict, self.checkpoint_path)
            if self.verbose:
                print(f"Saved new best model checkpoint to: {self.checkpoint_path}")
