"""
Unit tests for the Streamlit Application (app.py).

Verifies:
1. App module and components import cleanly.
2. Cached model loading and architecture verification.
3. GeoTIFF sample discovery.
4. SAR false-color composite generation.
5. End-to-end forward inference pipeline and output shape verification.
6. Figure rendering pipeline stability.
"""

import os
import sys
import pytest
import torch
import numpy as np
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import (
    load_cached_model,
    create_sar_composite,
    get_available_test_samples,
    render_prediction_figure,
    render_page_overview,
    render_page_dataset,
    render_page_ai_architecture,
    render_page_training,
    render_page_evaluation,
    render_page_prediction_gallery,
    render_page_live_demo,
    render_page_about_limitations,
)
from src.data.preprocessing import FloodPreprocessor


def test_app_imports_successfully():
    """Verifies that app.py and dependencies import cleanly without syntax or import errors."""
    import app
    assert hasattr(app, "load_cached_model")
    assert hasattr(app, "create_sar_composite")
    assert hasattr(app, "get_available_test_samples")
    assert hasattr(app, "render_prediction_figure")
    assert hasattr(app, "render_page_overview")
    assert hasattr(app, "render_page_dataset")
    assert hasattr(app, "render_page_ai_architecture")
    assert hasattr(app, "render_page_training")
    assert hasattr(app, "render_page_evaluation")
    assert hasattr(app, "render_page_prediction_gallery")
    assert hasattr(app, "render_page_live_demo")
    assert hasattr(app, "render_page_about_limitations")


def test_all_page_functions_callable():
    """Verifies that all 8 showcase page functions are callable without errors."""
    assert callable(render_page_overview)
    assert callable(render_page_dataset)
    assert callable(render_page_ai_architecture)
    assert callable(render_page_training)
    assert callable(render_page_evaluation)
    assert callable(render_page_prediction_gallery)
    assert callable(render_page_live_demo)
    assert callable(render_page_about_limitations)


def test_load_cached_model():
    """Verifies that load_cached_model loads the trained S1 U-Net checkpoint properly."""
    checkpoint_path = os.path.join(PROJECT_ROOT, "checkpoints", "best_s1.pt")
    if os.path.exists(checkpoint_path):
        model, device, err = load_cached_model(checkpoint_path)
        assert err is None, f"Model loading failed: {err}"
        assert model is not None
        assert model.in_channels == 2
        assert next(model.parameters()).device.type in ["mps", "cuda", "cpu"]


def test_load_cached_model_missing_checkpoint():
    """Verifies graceful error message when checkpoint is missing."""
    model, device, err = load_cached_model("checkpoints/non_existent_model.pt")
    assert model is None
    assert err is not None
    assert "not found" in err.lower()


def test_get_available_test_samples():
    """Verifies test sample discovery from dataset folder and splits."""
    samples = get_available_test_samples(
        data_dir=os.path.join(PROJECT_ROOT, "data", "samples"),
        splits_dir=os.path.join(PROJECT_ROOT, "data", "raw", "splits"),
    )
    assert isinstance(samples, dict)
    assert len(samples) > 0
    # Check sample format
    first_stem = next(iter(samples))
    assert "s1" in samples[first_stem]
    assert "label" in samples[first_stem]
    assert os.path.exists(samples[first_stem]["s1"])
    assert os.path.exists(samples[first_stem]["label"])


def test_create_sar_composite():
    """Verifies false-color SAR composite creation."""
    vv = np.random.rand(256, 256).astype(np.float32)
    vh = np.random.rand(256, 256).astype(np.float32)
    composite = create_sar_composite(vv, vh)
    assert composite.shape == (256, 256, 3)
    assert composite.min() >= 0.0
    assert composite.max() <= 1.0


def test_app_inference_pipeline():
    """Verifies that preprocessing + U-Net inference produces the expected 256x256 segmentation map."""
    checkpoint_path = os.path.join(PROJECT_ROOT, "checkpoints", "best_s1.pt")
    if not os.path.exists(checkpoint_path):
        pytest.skip("Checkpoint best_s1.pt not found")

    model, device, _ = load_cached_model(checkpoint_path)
    preprocessor = FloodPreprocessor()

    # Synthetic raw S1 data: (2, 512, 512) in dB range [-30, 0]
    raw_s1 = np.random.uniform(-30.0, 0.0, (2, 512, 512)).astype(np.float32)
    norm_s1 = preprocessor.normalize_s1(raw_s1)

    # 256x256 subsampling
    stride_h = norm_s1.shape[1] // 256
    stride_w = norm_s1.shape[2] // 256
    input_s1 = norm_s1[:, ::stride_h, ::stride_w]

    tensor_s1 = torch.from_numpy(input_s1).unsqueeze(0).float().to(device)

    with torch.no_grad():
        logits = model(tensor_s1)
        probs = torch.sigmoid(logits).squeeze().cpu().numpy()
        pred_binary = (probs >= 0.5).astype(np.int64)

    assert logits.shape == (1, 256, 256)
    assert probs.shape == (256, 256)
    assert pred_binary.shape == (256, 256)
    assert np.all(np.isin(pred_binary, [0, 1]))


def test_render_prediction_figure():
    """Verifies that figure rendering produces valid matplotlib figure objects without errors."""
    sar_rgb = np.random.rand(256, 256, 3).astype(np.float32)
    pred_binary = np.random.randint(0, 2, (256, 256), dtype=np.int64)
    probs = np.random.rand(256, 256).astype(np.float32)
    gt_mask = np.random.choice([-1, 0, 1], size=(256, 256))

    # Test with ground truth
    fig_with_gt = render_prediction_figure(
        sar_composite=sar_rgb,
        pred_binary=pred_binary,
        prob_map=probs,
        gt_mask=gt_mask,
    )
    assert fig_with_gt is not None
    import matplotlib.pyplot as plt
    plt.close(fig_with_gt)

    # Test without ground truth (e.g. Upload mode)
    fig_no_gt = render_prediction_figure(
        sar_composite=sar_rgb,
        pred_binary=pred_binary,
        prob_map=probs,
        gt_mask=None,
    )
    assert fig_no_gt is not None
    plt.close(fig_no_gt)
