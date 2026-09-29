# Sen1Floods11 Dataset Specification & Verification Report

**Project:** AI-Based Flood Detection and Mapping Using Satellite Imagery  
**Primary Dataset:** **Sen1Floods11 (v1.1)**  
**Authors:** Derrick Bonafilia, Beth Tellman, Tyler Anderson, Erica Issenberg (*Cloud to Street / CVPR 2020 EarthVision*)  
**Benchmark Reference:** [Bonafilia et al., 2020 (CVPRW)](https://openaccess.thecvf.com/content_CVPRW_2020/papers/w11/Bonafilia_Sen1Floods11_A_Georeferenced_Dataset_to_Train_and_Test_Deep_Learning_CVPRW_2020_paper.pdf)

---

## 1. Verified Dataset Structure & Storage Location

The official dataset is publicly hosted in Google Cloud Storage at `gs://sen1floods11/v1.1/` and accessible over HTTPS at `https://storage.googleapis.com/sen1floods11/v1.1/`.

### Directory Layout

```
sen1floods11/v1.1/
├── data/
│   ├── flood_events/
│   │   ├── HandLabeled/                # High-quality benchmark set (446 chips)
│   │   │   ├── S1Hand/                 # Sentinel-1 SAR imagery (2 bands: VV, VH)
│   │   │   ├── S2Hand/                 # Sentinel-2 Optical MSI imagery (13 bands)
│   │   │   ├── LabelHand/              # Hand-annotated ground-truth masks
│   │   │   ├── JRCWaterHand/           # Pre-flood permanent water baseline (JRC)
│   │   │   └── S1OtsuLabelHand/        # Baseline Otsu thresholded masks
│   │   └── WeaklyLabeled/              # 4,385 weakly-labeled scenes for pretraining
│   └── perm_water/                     # 815 chips for permanent water mapping
└── splits/
    └── flood_handlabeled/              # Official partition CSVs
        ├── flood_train_data.csv        # 252 chips (56.5%)
        ├── flood_valid_data.csv        # 89 chips (20.0%)
        ├── flood_test_data.csv         # 90 chips (20.2%)
        └── flood_bolivia_data.csv      # 15 chips (3.3%) [Isolated out-of-sample test]
```

---

## 2. Satellite Sensors, Bands & Physical Properties

| Layer | Satellite / Sensor | Format & Dtype | Bands & Polarization | Physical Meaning & Units |
|---|---|---|---|---|
| **`S1Hand`** | **Sentinel-1 C-SAR** (IW mode, GRD) | GeoTIFF ($512 \times 512$), `float32` | **Band 0:** `VV`<br>**Band 1:** `VH` (Cross-pol) | Radar backscatter amplitude in Decibels ($\text{dB}$). Specular reflection on calm water yields low backscatter ($<-18\text{ dB}$). |
| **`S2Hand`** | **Sentinel-2 MSI** (Level-1C) | GeoTIFF ($512 \times 512$), `int16` | **13 Spectral Bands:**<br>B1, B2 (Blue), B3 (Green), B4 (Red), B5, B6, B7, B8 (NIR), B8A, B9, B10, B11 (SWIR-1), B12 (SWIR-2) | Top of Atmosphere (TOA) reflectance scaled by $10{,}000$. True-Color RGB: (B4, B3, B2). |
| **`LabelHand`** | Human Annotator Consensus | GeoTIFF ($512 \times 512$), `int16` | **1 Band:** Pixel class label | Ground truth flood / water mask with invalid pixel tracking. |
| **`JRCWaterHand`** | JRC Global Surface Water (Pekel et al., 2016) | GeoTIFF ($512 \times 512$), `uint8` | **1 Band:** Historical permanence | $0 = \text{Dry land}$, $1 = \text{Historical permanent surface water}$ ($\ge 80\%$ occurrence). |

### Spatial & Geographic Properties
* **Ground Sampling Distance (GSD):** $10.0\text{ meters}$ per pixel.
* **Coordinate Reference System (CRS):** `EPSG:4326` (WGS 84).
* **Chip Dimension:** $512 \times 512\text{ pixels}$ ($\approx 5.12\text{ km} \times 5.12\text{ km} = 26.21\text{ km}^2$ per chip).
* **Physical Pixel Area:** $1\text{ pixel} = 100\text{ m}^2 = 0.0001\text{ km}^2$.

---

## 3. Mask Encoding & Label Handling

The ground truth raster masks (`LabelHand`) encode three distinct states:

| Value | Semantic Meaning | Recommended Handling in PyTorch |
|:---:|---|---|
| **`-1`** | **Invalid / Cloud / No-Data / Shadow** | Mapped to `ignore_index = -1` in Cross-Entropy / Dice Loss. Excluded from gradient updates and metric denominators. |
| **`0`** | **Non-Water (Dry land, vegetation, urban)** | Negative class in binary segmentation ($y = 0$). |
| **`1`** | **Water (Inundated flood extent / surface water)** | Positive class in binary segmentation ($y = 1$). |

> **Critical Implementation Rule:** Mask transformations must **strictly use nearest-neighbor interpolation**. Bilinear or bicubic interpolation on integer masks would create corrupt intermediate float labels (e.g., $0.4$, $-0.2$).

---

## 4. Analysis of Pre/Post Temporal Availability

### Findings from Actual Dataset Inspection
* In the official Sen1Floods11 release, image chips are collected during the 11 flood event windows.
* The dataset does **not** provide separate pre-flood SAR image files (i.e., there is no `_S1Pre.tif`).
* Instead, Sen1Floods11 provides **`JRCWaterHand`** (Joint Research Centre Global Surface Water dataset), which acts as the **standard pre-flood historical water baseline** derived from 30+ years of satellite observations.

### Redesign of Input Representation Decision

Based on actual dataset evidence, we support 5 flexible multi-modal ingestion pipelines:

1. **`s1` (2 Channels - Default SAR Baseline):**
   * Channels: `[S1_VV, S1_VH]`
   * **Advantage:** Operates in all-weather, day/night conditions, penetrates cloud cover during severe storms.
2. **`s2_rgb` (3 Channels - Optical Baseline):**
   * Channels: `[S2_Red (B4), S2_Green (B3), S2_Blue (B2)]`
   * **Advantage:** High visual interpretability for cloud-free flood assessment.
3. **`s1_jrc` (3 Channels - SAR + Pre-Flood Baseline):**
   * Channels: `[S1_VV, S1_VH, JRC_Permanent_Water]`
   * **Advantage:** Explicitly feeds pre-flood permanent water status alongside post-flood SAR backscatter to isolate *newly flooded pixels* from *existing lakes/rivers*.
4. **`s1_s2_rgb` (5 Channels - Optical + SAR Multi-Sensor Fusion):**
   * Channels: `[S1_VV, S1_VH, S2_Red, S2_Green, S2_Blue]`
   * **Advantage:** Combines structural radar scattering with rich optical surface reflectance.
5. **`s1_s2_rgb_jrc` (6 Channels - Multi-Sensor + Pre-Flood Baseline):**
   * Channels: `[S1_VV, S1_VH, S2_Red, S2_Green, S2_Blue, JRC_Permanent_Water]`
   * **Advantage:** Most comprehensive bi-temporal & multi-modal configuration.

---

## 5. Measured Dataset Statistics (Hand-Labeled Benchmark Split)

From our dataset validation run across the 11 global flood events:

* **Total Hand-Labeled Chips:** $446\text{ chips}$ ($252\text{ train}, 89\text{ val}, 90\text{ test}, 15\text{ bolivia}$)
* **Total Discovered & Validated Sample Pixels:** $7{,}121{,}893\text{ valid pixels}$
* **Water Pixels:** $1{,}150{,}214\text{ px}$ ($16.15\%$)
* **Non-Water Land Pixels:** $5{,}971{,}679\text{ px}$ ($83.85\%$)
* **Invalid / Cloud Pixels:** $1{,}266{,}715\text{ px}$ ($15.10\%$ of raw pixels)
* **Class Imbalance Ratio:** $\approx 1 : 5.19$ ($\text{Water} : \text{Land}$)

### SAR Backscatter Characteristics
* **VV Polarization:** Range $[-53.18\text{ dB}, +23.05\text{ dB}]$, Global Mean: $-10.75\text{ dB}$
* **VH Polarization:** Range $[-60.44\text{ dB}, +12.02\text{ dB}]$, Global Mean: $-17.56\text{ dB}$
* **Standard Normalization Strategy:** Clip to $[-35.0, +5.0]\text{ dB}$ and linearly scale to $[0.0, 1.0]$.
