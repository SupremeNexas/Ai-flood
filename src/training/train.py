"""
PyTorch Training and Evaluation Pipeline for Flood Semantic Segmentation.

Supports multi-modal benchmarking, masked loss computation, gradient clipping,
learning rate scheduling, early stopping, and automatic curve plotting.
"""

import os
import sys
import json
import random
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Ensure project root is in sys.path
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm

from src.models.unet import build_unet, UNet
from src.data.dataset import Sen1Floods11Dataset, create_dataloaders
from src.training.losses import CombinedBCEDiceLoss, MaskedBCEWithLogitsLoss, MaskedDiceLoss
from src.training.metrics import SegmentationMetrics
from src.training.early_stopping import EarlyStopping
from src.utils.config_loader import load_config, get_device


def set_seed(seed: int = 42) -> None:
    """Sets random seeds across Python, NumPy, and PyTorch for strict reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def train_one_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: str,
    grad_clip: float = 1.0,
    scaler: Optional[torch.amp.GradScaler] = None,
) -> Tuple[float, Dict[str, float]]:
    """
    Executes one training epoch across all training batches.
    """
    model.train()
    running_loss = 0.0
    metrics = SegmentationMetrics(threshold=0.0, ignore_index=-1)

    for batch in dataloader:
        images = batch["image"].to(device, non_blocking=True)
        masks = batch["mask"].to(device, non_blocking=True)

        optimizer.zero_grad(set_to_none=True)

        use_amp = scaler is not None and device == "cuda"
        with torch.autocast(device_type=device if device in ["cuda", "cpu"] else "cpu", enabled=use_amp):
            logits = model(images)
            loss = criterion(logits, masks)

        if scaler is not None and device == "cuda":
            scaler.scale(loss).backward()
            if grad_clip > 0:
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
            scaler.step(optimizer)
            scaler.update()
        else:
            loss.backward()
            if grad_clip > 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
            optimizer.step()

        running_loss += loss.item() * images.size(0)
        metrics.update(logits.detach(), masks.detach())

    epoch_loss = running_loss / len(dataloader.dataset)
    epoch_metrics = metrics.compute()
    return epoch_loss, epoch_metrics


@torch.no_grad()
def evaluate(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    device: str,
) -> Tuple[float, Dict[str, float]]:
    """
    Evaluates the model over validation or test batches without gradient tracking.
    """
    model.eval()
    running_loss = 0.0
    metrics = SegmentationMetrics(threshold=0.0, ignore_index=-1)

    for batch in dataloader:
        images = batch["image"].to(device, non_blocking=True)
        masks = batch["mask"].to(device, non_blocking=True)

        logits = model(images)
        loss = criterion(logits, masks)

        running_loss += loss.item() * images.size(0)
        metrics.update(logits, masks)

    eval_loss = running_loss / max(1, len(dataloader.dataset))
    eval_metrics = metrics.compute()
    return eval_loss, eval_metrics


def plot_training_curves(
    history: Dict[str, List[float]],
    modality: str,
    output_dir: str = "outputs/training",
) -> None:
    """
    Generates and saves training and validation loss & metric curves.
    """
    os.makedirs(os.path.join(output_dir, "loss_curves"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "metric_curves"), exist_ok=True)

    epochs = range(1, len(history["train_loss"]) + 1)

    # 1. Loss Curves
    plt.figure(figsize=(8, 5))
    plt.plot(epochs, history["train_loss"], "b-o", label="Train Loss", linewidth=2)
    plt.plot(epochs, history["val_loss"], "r--s", label="Validation Loss", linewidth=2)
    plt.title(f"Loss Curves: Modality [{modality.upper()}]", fontsize=13, fontweight="bold")
    plt.xlabel("Epoch")
    plt.ylabel("Loss (Combined BCE + Dice)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    loss_path = os.path.join(output_dir, "loss_curves", f"{modality}_loss_curve.png")
    plt.savefig(loss_path, dpi=150)
    plt.close()

    # 2. Metric Curves (IoU and Dice / F1)
    plt.figure(figsize=(8, 5))
    plt.plot(epochs, history["val_iou"], "g-o", label="Val IoU", linewidth=2)
    plt.plot(epochs, history["val_dice"], "m--^", label="Val Dice (F1)", linewidth=2)
    plt.plot(epochs, history["val_precision"], "c:", label="Val Precision", linewidth=1.5)
    plt.plot(epochs, history["val_recall"], "y-.", label="Val Recall", linewidth=1.5)
    plt.title(f"Validation Metrics: Modality [{modality.upper()}]", fontsize=13, fontweight="bold")
    plt.xlabel("Epoch")
    plt.ylabel("Score [0 - 1]")
    plt.ylim([0.0, 1.05])
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    metric_path = os.path.join(output_dir, "metric_curves", f"{modality}_metric_curve.png")
    plt.savefig(metric_path, dpi=150)
    plt.close()


def train_modality(
    modality: str,
    epochs: int = 5,
    batch_size: int = 2,
    lr: float = 0.0005,
    patience: int = 2,
    image_size: Optional[int] = 256,
    data_dir: str = "data/samples",
    splits_dir: str = "data/raw/splits",
    checkpoints_dir: str = "checkpoints",
    outputs_dir: str = "outputs/training",
    device: Optional[str] = None,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Executes complete lightweight training and validation cycle for a specific input modality.
    """
    set_seed(seed)
    device = device or get_device()
    os.makedirs(checkpoints_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)

    print(f"\n=======================================================")
    print(f"TRAINING U-NET | Modality: {modality.upper()} | Device: {device.upper()} | Epochs: {epochs} | Batch: {batch_size} | Size: {image_size}x{image_size}")
    print(f"=======================================================\n")

    # 1. Build DataLoaders
    loaders = create_dataloaders(
        data_dir=data_dir,
        splits_dir=splits_dir,
        modality=modality,
        batch_size=batch_size,
        num_workers=0,
        enable_augmentation=True,
        image_size=image_size,
    )

    train_loader = loaders.get("train")
    val_loader = loaders.get("val")

    if train_loader is None or len(train_loader) == 0:
        raise ValueError(f"Train dataloader is empty for modality {modality}")
    if val_loader is None or len(val_loader) == 0:
        print("Warning: Validation loader empty, using train loader for validation sanity checks.")
        val_loader = train_loader

    # 2. Instantiate Model
    model = build_unet(modality=modality).to(device)
    print(f"Model: U-Net (In-channels: {model.in_channels}, Parameters: {model.get_num_parameters():,})")

    # 3. Setup Loss, Optimizer, Scheduler, EarlyStopping
    criterion = CombinedBCEDiceLoss(alpha=0.5, beta=0.5, ignore_index=-1)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)
    best_ckpt_path = os.path.join(checkpoints_dir, f"best_{modality}.pt")
    last_ckpt_path = os.path.join(checkpoints_dir, f"last_{modality}.pt")

    early_stopping = EarlyStopping(
        patience=patience,
        mode="max",
        checkpoint_path=best_ckpt_path,
        verbose=False,
    )

    scaler = torch.amp.GradScaler("cuda") if device == "cuda" else None

    history: Dict[str, List[float]] = {
        "train_loss": [],
        "val_loss": [],
        "val_iou": [],
        "val_dice": [],
        "val_precision": [],
        "val_recall": [],
        "lr": [],
    }

    best_val_metrics: Dict[str, float] = {}

    for epoch in range(1, epochs + 1):
        train_loss, train_metrics = train_one_epoch(
            model=model,
            dataloader=train_loader,
            criterion=criterion,
            optimizer=optimizer,
            device=device,
            grad_clip=1.0,
            scaler=scaler,
        )

        val_loss, val_metrics = evaluate(
            model=model,
            dataloader=val_loader,
            criterion=criterion,
            device=device,
        )

        current_lr = optimizer.param_groups[0]["lr"]
        scheduler.step()

        # Record history
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["val_iou"].append(val_metrics["iou"])
        history["val_dice"].append(val_metrics["dice"])
        history["val_precision"].append(val_metrics["precision"])
        history["val_recall"].append(val_metrics["recall"])
        history["lr"].append(current_lr)

        print(
            f"Epoch [{epoch:02d}/{epochs:02d}] "
            f"Train Loss: {train_loss:.4f} (IoU: {train_metrics['iou']:.4f}) | "
            f"Val Loss: {val_loss:.4f} | "
            f"Val IoU: {val_metrics['iou']:.4f} | "
            f"Val Dice: {val_metrics['dice']:.4f} | "
            f"Val Prec: {val_metrics['precision']:.4f} | "
            f"Val Rec: {val_metrics['recall']:.4f} | "
            f"LR: {current_lr:.6f}"
        )

        # Checkpoint saving
        ckpt_dict = {
            "epoch": epoch,
            "modality": modality,
            "in_channels": model.in_channels,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "val_loss": val_loss,
            "val_metrics": val_metrics,
            "config": {
                "epochs": epochs,
                "batch_size": batch_size,
                "lr": lr,
                "seed": seed,
            },
        }

        # Save last checkpoint
        torch.save(ckpt_dict, last_ckpt_path)

        # Check early stopping and best model
        is_best = early_stopping(val_metrics["iou"], epoch, ckpt_dict)
        if is_best:
            best_val_metrics = val_metrics

        if early_stopping.early_stop:
            print(f"Early stopping triggered at epoch {epoch}")
            break

    # Save training curves
    plot_training_curves(history, modality, outputs_dir)

    result_summary = {
        "modality": modality,
        "in_channels": model.in_channels,
        "best_epoch": early_stopping.best_epoch,
        "best_val_iou": best_val_metrics.get("iou", history["val_iou"][-1]),
        "best_val_dice": best_val_metrics.get("dice", history["val_dice"][-1]),
        "best_val_precision": best_val_metrics.get("precision", history["val_precision"][-1]),
        "best_val_recall": best_val_metrics.get("recall", history["val_recall"][-1]),
        "best_val_f1": best_val_metrics.get("f1", history["val_dice"][-1]),
        "final_train_loss": history["train_loss"][-1],
        "final_val_loss": history["val_loss"][-1],
    }

    return result_summary


def benchmark_all_modalities(
    epochs: int = 15,
    batch_size: int = 4,
    lr: float = 0.0005,
    data_dir: str = "data/samples",
    splits_dir: str = "data/raw/splits",
    outputs_dir: str = "outputs/training",
    checkpoints_dir: str = "checkpoints",
    seed: int = 42,
) -> pd.DataFrame:
    """
    Systematically runs and compares all 5 input modalities under identical conditions.
    """
    modalities = ["s1", "s2_rgb", "s1_jrc", "s1_s2_rgb", "s1_s2_rgb_jrc"]
    results = []

    print(f"\n=======================================================")
    print(f"STARTING COMPREHENSIVE MODALITY BENCHMARK (5 MODES)")
    print(f"=======================================================\n")

    for mod in modalities:
        res = train_modality(
            modality=mod,
            epochs=epochs,
            batch_size=batch_size,
            lr=lr,
            data_dir=data_dir,
            splits_dir=splits_dir,
            checkpoints_dir=checkpoints_dir,
            outputs_dir=outputs_dir,
            seed=seed,
        )
        results.append(res)

    results_df = pd.DataFrame(results)
    csv_path = os.path.join(outputs_dir, "experiment_results.csv")
    results_df.to_csv(csv_path, index=False)

    print("\n=======================================================")
    print("BENCHMARK EXPERIMENT RESULTS (VALIDATION SET)")
    print("=======================================================\n")
    print(results_df[["modality", "in_channels", "best_val_iou", "best_val_dice", "best_val_precision", "best_val_recall", "best_val_f1"]].to_string(index=False))
    print(f"\nResults table saved to: {csv_path}")

    return results_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train U-Net for Flood Segmentation")
    parser.add_argument("--modality", choices=["s1", "s2_rgb", "s1_jrc", "s1_s2_rgb", "s1_s2_rgb_jrc", "all"], default="s1", help="Input modality")
    parser.add_argument("--epochs", type=int, default=5, help="Number of epochs")
    parser.add_argument("--batch_size", type=int, default=2, help="Batch size")
    parser.add_argument("--lr", type=float, default=0.0005, help="Learning rate")
    parser.add_argument("--patience", type=int, default=2, help="Early stopping patience")
    parser.add_argument("--image_size", type=int, default=256, help="Spatial image resolution (e.g. 256 or 512)")
    parser.add_argument("--data_dir", type=str, default="data/samples", help="Data directory")
    parser.add_argument("--splits_dir", type=str, default="data/raw/splits", help="Splits directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    if args.modality == "all":
        benchmark_all_modalities(
            epochs=args.epochs,
            batch_size=args.batch_size,
            lr=args.lr,
            data_dir=args.data_dir,
            splits_dir=args.splits_dir,
            seed=args.seed,
        )
    else:
        train_modality(
            modality=args.modality,
            epochs=args.epochs,
            batch_size=args.batch_size,
            lr=args.lr,
            patience=args.patience,
            image_size=args.image_size,
            data_dir=args.data_dir,
            splits_dir=args.splits_dir,
            seed=args.seed,
        )
