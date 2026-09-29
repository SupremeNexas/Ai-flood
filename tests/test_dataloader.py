"""
Unit tests for DataLoader batch creation.
"""

import pytest
import torch
from src.data.dataset import create_dataloaders


@pytest.mark.parametrize("batch_size", [4, 8])
def test_dataloader_batch_shapes(batch_size):
    loaders = create_dataloaders(
        data_dir="data/samples",
        splits_dir="data/raw/splits",
        modality="s1",
        batch_size=batch_size,
        num_workers=0,
    )

    assert "train" in loaders
    train_loader = loaders["train"]
    assert len(train_loader) > 0

    batch = next(iter(train_loader))
    images = batch["image"]
    masks = batch["mask"]

    assert images.shape[0] == min(batch_size, len(train_loader.dataset))
    assert images.shape[1] == 2  # S1 VV, VH
    assert images.shape[2] == 512
    assert images.shape[3] == 512

    assert masks.shape[0] == min(batch_size, len(train_loader.dataset))
    assert masks.shape[1] == 512
    assert masks.shape[2] == 512

    assert images.dtype == torch.float32
    assert masks.dtype == torch.int64
