# AI-Based Flood Detection and Mapping Using Satellite Imagery

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![PyTorch 2.0+](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.64+-ff4b4b.svg)](https://streamlit.io/)
[![Dataset: Sen1Floods11](https://img.shields.io/badge/Dataset-Sen1Floods11-green.svg)](https://github.com/cloudtostreet/Sen1Floods11)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests: 39/39 Passing](https://img.shields.io/badge/Tests-39%20Passing-brightgreen.svg)]()

An end-to-end Deep Learning semantic segmentation system for detecting, mapping, and quantifying flood extents from dual-polarization **Sentinel-1 SAR (VV + VH)** satellite imagery using an academically audited PyTorch U-Net architecture.

---

## 📌 Executive Summary

* **Primary Model:** Sentinel-1 SAR ($VV + VH$ dual-polarization) U-Net with Group Normalization ($G=8$).
* **Official Test Split Evaluated:** **90 / 90 chips** (100% of official Sen1Floods11 test split, zero exclusions).
* **Test Metrics (Full 90 Chips):**
  * **Test IoU (Jaccard Index):** **0.5548**
  * **Test Dice / F1 Score:** **0.7137**
  * **Test Precision:** **0.7717**
  * **Test Recall:** **0.6637**
  * **Test Overall Accuracy:** **0.9334**
* **Total Valid Pixels Evaluated:** 20,517,367 pixels
* **Test Confusion Matrix:** $\text{TP} = 1,703,186$, $\text{FP} = 503,818$, $\text{FN} = 862,915$, $\text{TN} = 17,447,448$.
* **Fast & Lightweight Execution:** ~15 seconds total training on Apple Silicon MPS / CUDA with memory-efficient sub-sampling and GroupNorm.

---

## 🚀 Interactive Streamlit Web Application

An interactive web dashboard is provided for live demonstration, chip evaluation, and custom image inference.

### Run the Application

```bash
./.venv/bin/streamlit run app.py
```

### Application Features & Workflow

The interface is structured into two operational modes:

1. **Mode 1: Sample Prediction (Test Set Benchmark)**
   * **Input:** Dropdown selection across all 90 official Sen1Floods11 test chips.
   * **Inference:** Automatically loads dual-band SAR and reference label mask, executes cached U-Net inference, and generates:
     * False-color SAR composite ($VV, VH, VV/VH\text{ ratio}$)
     * Ground-Truth reference mask (Land, Water, Invalid)
     * Predicted binary flood mask
     * Model overlay visualization
     * Flood Probability Map (Sigmoid logits)
   * **Quantitative Evaluation:** Real-time IoU, Dice/F1, Precision, Recall, Confusion Matrix counts, and nominal flooded area in $\text{km}^2$.

2. **Mode 2: Upload Custom SAR GeoTIFF**
   * **Input:** Accepts user-uploaded Sentinel-1 GeoTIFF rasters (`.tif` / `.tiff`).
   * **Validation:** Validates raster readability and verifies at least 2 channels ($VV$ and $VH$).
   * **Processing:** Normalizes SAR dB values $[-35\text{ dB}, +5\text{ dB}] \to [0, 1]$, resizes/downsamples to $256\times256$, runs inference with interactive probability threshold slider, and produces flood extent maps and nominal area estimates.

---

## 🏗️ Architecture & Loss Formulation

### 1. U-Net Network Architecture
```
Input (2, 256, 256) [VV, VH Normalized dB]
   │
   ├── ConvBlock(2 → 32)      ─── Skip 1 ──────────────────────────────┐
   ├── MaxPool(2x2)                                                    │
   ├── ConvBlock(32 → 64)     ─── Skip 2 ────────────────────┐         │
   ├── MaxPool(2x2)                                          │         │
   ├── ConvBlock(64 → 128)    ─── Skip 3 ──────────┐         │         │
   ├── MaxPool(2x2)                                │         │         │
   ├── ConvBlock(128 → 256)   ─── Skip 4 ─┐        │         │         │
   ├── MaxPool(2x2)                       │        │         │         │
   ├── Bottleneck(256 → 512, Dropout=0.1) │        │         │         │
   ├── UpConv(512 → 256) + Cat(Skip 4) ───┘        │         │         │
   ├── UpConv(256 → 128) + Cat(Skip 3) ────────────┘         │         │
   ├── UpConv(128 → 64)  + Cat(Skip 2) ──────────────────────┘         │
   ├── UpConv(64 → 32)   + Cat(Skip 1) ────────────────────────────────┘
   └── Final 1x1 Conv (32 → 1) ── Logits Output (1, 256, 256)
```
* **Group Normalization ($G=8$):** Replaces standard BatchNorm to eliminate batch-size dependency when training on small batch sizes and geographically varied terrain.
* **Regularization:** Bottleneck spatial dropout ($p=0.1$) and AdamW weight decay ($10^{-4}$).

### 2. Masked Loss Formulation
Ground-truth masks contain three label values: `-1` (Invalid/Cloud), `0` (Land), `1` (Water). The loss is calculated exclusively over valid pixels $\mathcal{V} = \{i \mid y_i \neq -1\}$:

$$\mathcal{L}_{\text{total}} = 0.5 \cdot \mathcal{L}_{\text{BCE}}(\mathbf{\hat{p}}_{\mathcal{V}}, \mathbf{y}_{\mathcal{V}}) + 0.5 \cdot \mathcal{L}_{\text{Dice}}(\mathbf{\hat{p}}_{\mathcal{V}}, \mathbf{y}_{\mathcal{V}})$$

---

## 📊 Full Test Evaluation Results

The primary winning model was evaluated across all 90 test chips in `data/raw/splits/flood_test_data.csv`:

| Metric | Score | Formula / Basis |
| :--- | :---: | :--- |
| **Chips Evaluated** | **90 / 90 (100%)** | All official test chips without data leakage |
| **Total Valid Pixels** | **20,517,367** | Evaluated strictly on valid pixels ($\mathcal{V}$) |
| **Ground Truth Water** | **2,566,101 (12.51%)** | Natural geographic class imbalance |
| **Test IoU** | **0.5548** | $\frac{\text{TP}}{\text{TP} + \text{FP} + \text{FN}} = \frac{1,703,186}{3,069,919}$ |
| **Test Dice (F1)** | **0.7137** | $\frac{2 \cdot \text{TP}}{2 \cdot \text{TP} + \text{FP} + \text{FN}} = \frac{3,406,372}{4,773,105}$ |
| **Test Precision** | **0.7717** | $\frac{\text{TP}}{\text{TP} + \text{FP}} = \frac{1,703,186}{2,207,004}$ |
| **Test Recall** | **0.6637** | $\frac{\text{TP}}{\text{TP} + \text{FN}} = \frac{1,703,186}{2,566,101}$ |
| **Overall Accuracy** | **0.9334** | $\frac{\text{TP} + \text{TN}}{\text{Total Valid}} = \frac{19,150,634}{20,517,367}$ |

---

## 🖼️ Representative Test Visualizations

Visual diagnostics are automatically generated into `outputs/visualizations/final_test/` as 5-panel figures:
1. **Good Prediction (`USA_905409`):** IoU: **0.9350** | Dice: **0.9664** | Precision: **0.9720** | Recall: **0.9609**
2. **Average Prediction (`Pakistan_694942`):** IoU: **0.3829** | Dice: **0.5538** | Precision: **0.4152** | Recall: **0.8313**
3. **Difficult Prediction (`Sri-Lanka_450918`):** IoU: **0.0086** | Dice: **0.0171** | Complex narrow waterways with heavy vegetation interference.

---

## ⚡ Quickstart & Reproducibility

### 1. Environment Setup
```bash
git clone https://github.com/SupremeNexas/Ai-flood.git
cd Ai-flood
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Test Suite (39 Unit Tests)
```bash
./.venv/bin/pytest tests/ -v
```

### 3. Launch the Streamlit Demo Application
```bash
./.venv/bin/streamlit run app.py
```

### 4. Lightweight Training Run
```bash
./.venv/bin/python src/training/train.py --modality s1 --epochs 5 --batch_size 2 --image_size 256 --patience 2
```

### 5. Full 90-Chip Official Test Evaluation
```bash
./.venv/bin/python src/training/evaluate_test.py --checkpoint checkpoints/best_s1.pt --modality s1
```

### 6. Single-Chip Direct Inference Command
```bash
./.venv/bin/python -c "
import torch, rasterio, numpy as np
from src.models.unet import build_unet
from src.data.preprocessing import FloodPreprocessor
from src.utils.config_loader import get_device

device = get_device()
ckpt = torch.load('checkpoints/best_s1.pt', map_location=device)
model = build_unet(modality='s1').to(device)
model.load_state_dict(ckpt['model_state_dict'])
model.eval()

with rasterio.open('data/samples/S1Hand/USA_905409_S1Hand.tif') as src:
    raw_s1 = src.read()
norm_s1 = FloodPreprocessor().normalize_s1(raw_s1)
img_t = torch.from_numpy(norm_s1[:, ::2, ::2]).unsqueeze(0).float().to(device)

with torch.no_grad():
    logits = model(img_t)
    pred_water = (logits > 0.0).cpu().numpy().squeeze()

water_px = int(np.sum(pred_water == 1))
area_km2 = water_px * (10.0 * 10.0) / 1e6
print(f'Inference Successful! Detected Water Pixels: {water_px:,} (~{area_km2:.3f} km² nominal)')
"
```

---

## ⚠️ Academic & Demo Limitations

1. **Resolution Variation by Latitude:** Coordinates are in WGS84 (`EPSG:4326`). Pixel dimensions in degrees ($dx \approx 8.98 \times 10^{-5\circ}$) mean true ground width in meters varies with $\cos(\text{latitude})$. Area in $\text{km}^2$ is documented as a nominal equatorial approximation ($10\text{ m/px} = 100\text{ m}^2/\text{px}$).
2. **Double-Bounce & Radar Shadows:** SAR radar specularly reflects off smooth open water, but dense vegetation canopies and steep urban structures can cause double-bounce backscatter, leading to false negatives in flooded forests.
3. **Temporal Baseline Design:** Sen1Floods11 does not contain separate pre-flood SAR GeoTIFFs; pre-flood permanent water baseline is sourced from the JRC Global Surface Water dataset (30-year permanence).
4. **Custom Upload Ground Truth:** Custom uploaded SAR images will display Flood Probability Maps, binary masks, overlays, and nominal area estimates, but cannot display IoU/Dice metrics due to absence of ground-truth annotations.
