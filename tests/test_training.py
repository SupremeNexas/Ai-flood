"""
Unit tests for Training, Checkpointing, and Early Stopping.
"""

import os
import pytest
import torch
from src.models.unet import build_unet
from src.training.losses import CombinedBCEDiceLoss
from src.training.early_stopping import EarlyStopping
from src.training.train import train_one_epoch
from torch.utils.data import DataLoader, TensorDataset


def test_one_training_step():
    model = build_unet(modality="s1")
    criterion = CombinedBCEDiceLoss(alpha=0.5, beta=0.5, ignore_index=-1)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)

    # Synthetic batch: images (2, 2, 64, 64), masks (2, 64, 64)
    images = torch.rand(2, 2, 64, 64)
    masks = torch.randint(low=-1, high=2, size=(2, 64, 64))

    dataset = [{"image": images[i], "mask": masks[i]} for i in range(2)]
    loader = DataLoader(dataset, batch_size=2)

    loss, metrics = train_one_epoch(
        model=model,
        dataloader=loader,
        criterion=criterion,
        optimizer=optimizer,
        device="cpu",
    )

    assert loss > 0.0
    assert not torch.isnan(torch.tensor(loss))
    assert "iou" in metrics


def test_early_stopping_and_checkpointing(tmp_path):
    ckpt_path = str(tmp_path / "test_best.pt")
    early_stop = EarlyStopping(patience=3, mode="max", checkpoint_path=ckpt_path, verbose=False)

    ckpt_data = {"epoch": 1, "score": 0.75}
    # Epoch 1: score improves (0.75) -> saves
    is_best1 = early_stop(0.75, epoch=1, checkpoint_dict=ckpt_data)
    assert is_best1 is True
    assert os.path.exists(ckpt_path)

    # Epoch 2: score drops (0.60) -> counter 1
    is_best2 = early_stop(0.60, epoch=2, checkpoint_dict=ckpt_data)
    assert is_best2 is False
    assert early_stop.counter == 1

    # Epoch 3: score drops (0.62) -> counter 2
    early_stop(0.62, epoch=3, checkpoint_dict=ckpt_data)
    assert early_stop.counter == 2

    # Epoch 4: score drops (0.55) -> counter 3 -> triggers early stop
    early_stop(0.55, epoch=4, checkpoint_dict=ckpt_data)
    assert early_stop.early_stop is True

    # Test loading checkpoint
    loaded = torch.load(ckpt_path, map_location="cpu")
    assert loaded["score"] == 0.75
