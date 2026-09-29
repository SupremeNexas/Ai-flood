# AI-Based Flood Detection and Mapping Using Satellite Imagery

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![PyTorch 2.0+](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org/)
[![Dataset: Sen1Floods11](https://img.shields.io/badge/Dataset-Sen1Floods11-green.svg)](https://github.com/cloudtostreet/Sen1Floods11)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An end-to-end Deep Learning pipeline for detecting, segmenting, and mapping flooded regions from Sentinel-1 Synthetic Aperture Radar (SAR) and Sentinel-2 optical satellite imagery.

---

## 📁 Project Architecture

```
Ai-flood/
├── configs/
│   └── config.yaml                     # Central experiment & pipeline configuration
├── data/
│   ├── raw/
│   │   └── splits/                     # Official Sen1Floods11 benchmark CSV splits
│   ├── samples/                        # Curated development sample chips (S1, S2, Label, JRC)
│   └── processed/                      # Cached preprocessed artifacts (if generated)
├── notebooks/
│   └── 01_dataset_exploration.ipynb    # Interactive exploration & verification notebook
├── outputs/
│   ├── dataset_summary.json            # Machine-readable validation metrics
│   ├── dataset_statistics.csv          # Per-chip tabular band and mask statistics
│   └── visualizations/
│       └── dataset_samples/            # 6-panel multi-modal verification figures
├── src/
│   ├── data/
│   │   ├── download.py                 # Dataset & sample ingestion CLI
│   │   ├── validation.py               # Data integrity & quality control checks
│   │   ├── preprocessing.py            # SAR/Optical normalization & synchronized transforms
│   │   └── dataset.py                  # PyTorch Dataset & DataLoader factory
│   ├── visualization/
│   │   └── visualize_data.py           # Multi-panel sample visualization generator
│   └── utils/
│       └── config_loader.py            # Configuration parser & device detection
├── tests/
│   ├── test_dataset_discovery.py       # Layer matching & integrity tests
│   ├── test_preprocessing.py           # Normalization & transform tests
│   ├── test_dataset.py                 # PyTorch Dataset modality tests
│   └── test_dataloader.py              # DataLoader batch shape tests
├── DATASET.md                          # Detailed Sen1Floods11 specification
├── requirements.txt                    # Project dependencies
└── README.md
```

---

## 🛰️ Dataset: Sen1Floods11

The system uses **Sen1Floods11**, a globally distributed benchmark containing 11 flood events across 6 continents:
* **Sentinel-1 SAR:** 2 channels (VV, VH backscatter in dB). All-weather radar capable of penetrating cloud cover.
* **Sentinel-2 Optical:** 13 spectral bands (TOA reflectance). High-resolution multispectral imagery.
* **JRC Permanent Water:** Pre-flood historical water baseline to separate newly flooded land from permanent lakes/rivers.
* **Ground Truth Masks:** Dense pixel annotations (`-1` = Invalid/Cloud, `0` = Land, `1` = Water).

For complete technical specifications, see [DATASET.md](DATASET.md).

---

## ⚡ Quickstart & Setup

### 1. Installation

```bash
# Clone repository
git clone https://github.com/SupremeNexas/Ai-flood.git
cd Ai-flood

# Create & activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Download Development Samples or Full Benchmark

```bash
# Download curated sample chips spanning all 11 flood events (recommended for dev)
python src/data/download.py --mode samples

# (Optional) Download the full 446 hand-labeled benchmark chips
python src/data/download.py --mode full
```

### 3. Run Dataset Validation & Quality Control

```bash
python src/data/validation.py --data_dir data/samples --output_dir outputs
```
This produces:
* `outputs/dataset_summary.json`
* `outputs/dataset_statistics.csv`

### 4. Generate Visual Verification Figures

```bash
python src/visualization/visualize_data.py --data_dir data/samples --output_dir outputs/visualizations/dataset_samples --max_samples 12
```

### 5. Run Unit Tests

```bash
pytest -v tests/
```

---

## 🔬 Multi-Modal Ingestion Options

The PyTorch dataset (`Sen1Floods11Dataset`) supports 5 configurable input modalities:

```python
from src.data.dataset import Sen1Floods11Dataset, create_dataloaders

# 1. Standard SAR Baseline (VV, VH - 2 channels)
ds_s1 = Sen1Floods11Dataset(data_dir="data/samples", modality="s1")

# 2. Optical RGB Baseline (B4, B3, B2 - 3 channels)
ds_s2 = Sen1Floods11Dataset(data_dir="data/samples", modality="s2_rgb")

# 3. SAR + Pre-Flood Permanent Water Baseline (3 channels)
ds_jrc = Sen1Floods11Dataset(data_dir="data/samples", modality="s1_jrc")

# 4. Multi-Sensor Early Fusion: SAR + Optical RGB (5 channels)
ds_fusion = Sen1Floods11Dataset(data_dir="data/samples", modality="s1_s2_rgb")

# 5. Full Bi-Temporal & Multi-Sensor Stack (6 channels)
ds_full = Sen1Floods11Dataset(data_dir="data/samples", modality="s1_s2_rgb_jrc")

# Batch creation via factory
loaders = create_dataloaders(data_dir="data/samples", splits_dir="data/raw/splits", modality="s1", batch_size=4)
for batch in loaders['train']:
    images = batch['image']  # Shape: (4, 2, 512, 512)
    masks = batch['mask']    # Shape: (4, 512, 512)
    break
```

---

## 📊 Summary of Validated Sample Statistics

* **Validated Chips:** 32 chips across 11 countries (Bolivia, Ghana, India, Mekong/Cambodia, Nigeria, Pakistan, Paraguay, Somalia, Spain, Sri Lanka, USA)
* **Pixel Distribution:**
  * **Water Pixels:** $16.15\%$
  * **Land / Non-Water Pixels:** $83.85\%$
  * **Invalid / Cloud Pixels:** $15.10\%$
  * **Class Imbalance Ratio:** $\approx 1 : 5.19$ ($\text{Water} : \text{Land}$)
* **Spatial Resolution:** $10.0\text{ m/pixel}$ ($1\text{ px} = 100\text{ m}^2 = 0.0001\text{ km}^2$)

---

## 📜 Citations

If using this project or dataset, please cite the original authors:

```bibtex
@inproceedings{bonafilia2020sen1floods11,
  title={Sen1Floods11: a georeferenced dataset to train and test deep learning flood algorithms for Sentinel-1},
  author={Bonafilia, Derrick and Tellman, Beth and Anderson, Tyler and Issenberg, Erica},
  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition Workshops},
  pages={210--211},
  year={2020}
}
```
