# AI-Based Flood Detection and Mapping Using Satellite Imagery

**Academic Final Project Report**  
**Course / Degree:** Bachelor of Technology in Computer Science & Engineering (AI / ML)  
**Domain:** Deep Learning, Computer Vision, Earth Observation & Remote Sensing  
**Benchmark Dataset:** Sen1Floods11 Hand-Labeled Partition  
**Primary Architecture:** Sentinel-1 Synthetic Aperture Radar (SAR) PyTorch U-Net  

---

## 1. Title
**AI-Based Flood Detection and Mapping Using Pre- and Post-Flood Satellite Imagery: A Deep Learning Semantic Segmentation Framework on Sentinel-1 SAR Data**

---

## 2. Abstract
Flooding is among the most catastrophic and economically devastating natural disasters globally, demanding rapid, reliable, and all-weather surface water delineation for emergency response and damage mitigation. While multispectral optical satellite imagery is standard for environmental monitoring, it is severely impaired during active flood crises due to dense cloud cover and heavy precipitation. In this project, we design, implement, and rigorously evaluate an end-to-end Deep Learning semantic segmentation system utilizing Sentinel-1 dual-polarization ($VV + VH$) Synthetic Aperture Radar (SAR) data from the globally distributed Sen1Floods11 benchmark. Our system employs a customized 4-stage U-Net architecture integrated with Group Normalization ($G=8$) to ensure batch-size invariant training stability across diverse terrestrial biomes. To handle severe class imbalance and unannotated pixels, the network is optimized using a domain-specific combined Binary Cross-Entropy and Dice loss computed exclusively over valid pixels. The pipeline was audited and evaluated across all 90 chips of the official Sen1Floods11 test split ($20,517,367$ valid pixels), achieving a Test Intersection over Union (IoU) of **0.5548**, a Test Dice / F1 Score of **0.7137**, a Precision of **0.7717**, a Recall of **0.6637**, and an Overall Accuracy of **0.9334**. Furthermore, an interactive Streamlit web dashboard was developed to facilitate rapid chip inspection, probability mapping, and custom GeoTIFF inference. The system serves as an academic prototype for automated flood extent assessment, with documented caveats regarding WGS84 latitudinal geometric scaling and radar double-bounce reflections.

---

## 3. Introduction
Satellite remote sensing has revolutionized disaster response by providing synoptic, repeated earth observations across large geographic scales. During severe flood emergencies caused by monsoons, tropical cyclones, or dam bursts, civil protection authorities require timely information indicating the exact boundaries of standing surface water. 

Conventional flood mapping relied on manual photo-interpretation or classical thresholding algorithms applied to optical reflectance data. However, active flood periods are inherently characterized by continuous cloud cover, rendering optical sensors ineffective. Synthetic Aperture Radar (SAR) sensors operate in the microwave frequency spectrum (e.g., C-band at $5.405\text{ GHz}$ for Sentinel-1), which penetrates clouds, haze, rain, and operates independently of solar illumination. When microwave pulses encounter smooth open water, specular reflection directs the energy away from the sensor, producing low backscatter values that appear dark in SAR imagery. 

Leveraging these physical characteristics, Deep Learning semantic segmentation models—specifically Convolutional Neural Networks (CNNs) based on the encoder-decoder U-Net topology—can learn non-linear spatial and contextual representations to segment flooded terrain from complex radar backscatter signals.

---

## 4. Problem Statement
Accurate automated flood delineation using SAR satellite data presents significant technical challenges:
1. **Cloud Interference with Optical Imagery:** Optical sensors (Sentinel-2, Landsat) cannot view the ground during severe storms, necessitating radar-based solutions.
2. **SAR Backscatter Artifacts:** Radar imagery contains speckle noise, terrain shadows in mountainous areas, and double-bounce scattering from flooded urban structures and emergent vegetation canopies, causing false positives and false negatives.
3. **Severe Geographic Class Imbalance:** Floodwaters typically cover only $10\%–20\%$ of a satellite scene, causing standard machine learning classifiers to bias heavily toward the background land class.
4. **Data Integrity & Leakage:** Many existing academic prototypes evaluate models on non-standard, truncated subsets or introduce spatial leakage between training and testing splits.

---

## 5. Objectives
The primary objectives of this project are:
1. **Data Ingestion & Leakage Verification:** Ingest, parse, and validate the global **Sen1Floods11** dataset across 11 flood events, strictly verifying pairwise mutual exclusivity between training, validation, and testing splits.
2. **Model Architecture Implementation:** Build an efficient PyTorch **U-Net** semantic segmentation network utilizing **Group Normalization ($G=8$)** and GELU activations for batch-invariant performance.
3. **Domain-Specific Masked Loss Formulation:** Formulate and verify a hybrid **Masked BCE + Dice Loss** function that ignores invalid/cloud pixels (`-1`) and counteracts severe land/water class imbalance.
4. **Full Test Benchmark Evaluation:** Evaluate the trained checkpoint across **100% of the official 90-chip test partition** (`flood_test_data.csv`) without silent exclusions.
5. **Interactive Demonstration Interface:** Develop and verify an interactive **Streamlit application** (`app.py`) allowing multi-panel visualization (Input SAR, Ground Truth, Predicted Mask, Overlay, Flood Probability Map) and custom GeoTIFF upload.

---

## 6. Existing Approach vs. Motivation
Traditional flood detection techniques primarily employ:
* **Optical Water Indices (e.g., MNDWI, NDWI):** Highly accurate under clear skies but fail completely under storm clouds and overcast weather.
* **Global Otsu / Fixed Thresholding on SAR:** Applying a single backscatter threshold (e.g., $VV < -18\text{ dB}$) fails in diverse terrain due to soil moisture variations, surface roughness, and radar speckle.

**Motivation for Proposed System:** A Deep Convolutional U-Net model learns multi-scale hierarchical spatial contexts. It does not examine single pixels in isolation; rather, it considers neighborhood textures, topographic continuity, and multi-polarization ratios ($VV$ and $VH$), yielding superior delineation accuracy and noise robustness.

---

## 7. Proposed System Overview
The proposed system consists of five modular stages:
1. **Data Ingestion & Discovery:** Identifies multi-modal GeoTIFF rasters and ensures split alignment.
2. **Radiometric Normalization & Preprocessing:** Converts raw radar backscatter values to normalized floating-point tensors in $[0, 1]$.
3. **Deep Semantic Segmentation:** Executes forward inference through a 4-stage PyTorch U-Net with skip connections.
4. **Post-Processing & Quantification:** Converts continuous logits to flood probability maps and binary masks, computing pixel confusion matrices and nominal area approximations.
5. **Interactive UI Delivery:** Provides an accessible web dashboard for real-time visualization and user uploads.

---

## 8. Dataset: Sen1Floods11
The system is built upon **Sen1Floods11**, an internationally recognized benchmark dataset developed by Cloud to Street and published at IEEE CVPRW 2020.

### Dataset Characteristics:
* **Global Diversity:** Spans 11 flood events across 6 continents (Bolivia, Ghana, India, Mekong/Cambodia, Nigeria, Pakistan, Paraguay, Somalia, Spain, Sri Lanka, USA).
* **Sensor Modalities:**
  * **Sentinel-1 SAR:** Level-1 Ground Range Detected (GRD) in Interferometric Wide (IW) swath mode, providing dual-polarization $VV$ (vertical transmit/vertical receive) and $VH$ (vertical transmit/horizontal receive) backscatter.
  * **JRC Global Surface Water Baseline:** 30+ year historical water permanence layer derived from the European Commission Joint Research Centre (JRC).
* **Hand-Labeled Benchmark Partitions:**
  * **Training Split (`flood_train_data.csv`):** 252 chips ($1,008$ GeoTIFF files)
  * **Validation Split (`flood_valid_data.csv`):** 89 chips ($356$ GeoTIFF files)
  * **Official Test Split (`flood_test_data.csv`):** 90 chips ($360$ GeoTIFF files)
  * **Bolivia Holdout Split (`flood_bolivia_data.csv`):** 15 chips ($60$ GeoTIFF files)
* **Data Leakage Verification:** Pairwise intersection checks confirmed **0 overlapping chips** between all dataset partitions.
* **Temporal Context:** Sen1Floods11 does not provide separate pre-flood SAR acquisitions; instead, the JRC historical water layer serves as the pre-flood surface baseline.

---

## 9. Data Preprocessing & Augmentation

### 1. Radiometric Normalization
Raw Sentinel-1 backscatter values $\sigma^0$ in decibels ($\text{dB}$) typically range from $-35\text{ dB}$ to $+5\text{ dB}$. Extreme outliers are clipped and normalized linearly:

$$x_{\text{norm}} = \frac{\text{clip}(\sigma^0, -35.0, 5.0) - (-35.0)}{5.0 - (-35.0)} \in [0.0, 1.0]$$

### 2. Spatial Subsampling
Chips are subsampled from their native $512 \times 512$ resolution to $256 \times 256$ using strided slicing (`[::stride, ::stride]`), preserving exact integer mask values (`-1, 0, 1`) without interpolation distortion.

### 3. Synchronized Spatial Augmentation
During training, input channels and ground-truth masks undergo synchronized geometric transformations:
* Horizontal flip ($p=0.5$)
* Vertical flip ($p=0.5$)
* Orthogonal $90^\circ$ rotation ($p=0.5$)

---

## 10. U-Net Architecture

The network follows an encoder-decoder U-Net architecture engineered for memory efficiency and spatial fidelity:

```
Input (2, 256, 256) [S1 SAR: VV, VH Normalized]
  │
  ├── DoubleConv(2 → 32)      ─── Skip 1 ──────────────────────────────┐
  ├── MaxPool2d(2x2)                                                   │
  ├── DoubleConv(32 → 64)     ─── Skip 2 ────────────────────┐         │
  ├── MaxPool2d(2x2)                                         │         │
  ├── DoubleConv(64 → 128)    ─── Skip 3 ──────────┐         │         │
  ├── MaxPool2d(2x2)                               │         │         │
  ├── DoubleConv(128 → 256)   ─── Skip 4 ─┐        │         │         │
  ├── MaxPool2d(2x2)                      │        │         │         │
  ├── Bottleneck(256 → 512, Dropout=0.1)  │        │         │         │
  ├── UpConv(512 → 256) + Cat(Skip 4) ────┘        │         │         │
  ├── UpConv(256 → 128) + Cat(Skip 3) ─────────────┘         │         │
  ├── UpConv(128 → 64)  + Cat(Skip 2) ───────────────────────┘         │
  ├── UpConv(64 → 32)   + Cat(Skip 1) ─────────────────────────────────┘
  └── Conv2d(32 → 1, 1x1) ── Logits Output (1, 256, 256)
```

### Architectural Key Elements:
* **Group Normalization ($G=8$):** Replaces standard Batch Normalization. When operating on small batch sizes ($\text{batch\_size} = 2$) across globally varied terrain, BatchNorm suffers from noisy batch statistics; GroupNorm normalizes across channel groups per sample, guaranteeing batch-size invariance.
* **GELU Non-Linearity:** Gaussian Error Linear Units provide smoother gradient propagation than standard ReLU.
* **Skip Connections:** Concatenates encoder feature representations with upsampled decoder layers to retain fine spatial boundaries (canals, shorelines).
* **Trainable Parameters:** **7,760,257 parameters**.

---

## 11. Loss Function Formulation
Ground-truth annotations contain three classes: `-1` (Invalid/Cloud), `0` (Land), `1` (Water). The loss is computed strictly over the valid pixel set $\mathcal{V} = \{i \mid y_i \neq -1\}$:

### 1. Masked Binary Cross-Entropy Loss
$$\mathcal{L}_{\text{BCE}} = -\frac{1}{|\mathcal{V}|} \sum_{i \in \mathcal{V}} \left[ y_i \log \sigma(z_i) + (1 - y_i) \log (1 - \sigma(z_i)) \right]$$

### 2. Masked Soft Dice Loss
$$\mathcal{L}_{\text{Dice}} = 1 - \frac{2 \sum_{i \in \mathcal{V}} \sigma(z_i) y_i + \epsilon}{\sum_{i \in \mathcal{V}} \sigma(z_i) + \sum_{i \in \mathcal{V}} y_i + \epsilon}$$

### 3. Total Combined Loss
$$\mathcal{L}_{\text{total}} = 0.5 \cdot \mathcal{L}_{\text{BCE}} + 0.5 \cdot \mathcal{L}_{\text{Dice}}$$

---

## 12. Training Configuration
* **Hardware Accelerator:** Apple Silicon MPS (`mps:0`) / CUDA compatible.
* **Batch Size:** 2
* **Spatial Resolution:** $256 \times 256$ pixels
* **Total Epochs:** 5 (Early stopping patience: 2 epochs)
* **Optimizer:** AdamW ($\text{lr} = 5 \times 10^{-4}$, $\text{weight\_decay} = 10^{-4}$)
* **Learning Rate Schedule:** Cosine Annealing ($\eta_{\text{min}} = 10^{-5}$)
* **Training Wall-Clock Time:** **~15.2 seconds total** (~3.0 seconds/epoch)

---

## 13. Evaluation Metrics
For binary segmentation over valid pixels $\mathcal{V}$:
* **Intersection over Union (IoU / Jaccard Index):**
  $$\text{IoU} = \frac{\text{TP}}{\text{TP} + \text{FP} + \text{FN}}$$
* **Dice Coefficient / F1 Score:**
  $$\text{Dice} = \frac{2 \cdot \text{TP}}{2 \cdot \text{TP} + \text{FP} + \text{FN}} = \text{F1}$$
* **Precision:**
  $$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}$$
* **Recall (Sensitivity):**
  $$\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}$$
* **Overall Accuracy:**
  $$\text{Accuracy} = \frac{\text{TP} + \text{TN}}{\text{Total Valid Pixels}}$$

---

## 14. Experimental Results & Modality Benchmarking
During validation exploration, five input configurations were benchmarked under identical conditions:

| Modality Configuration | Input Channels | Val Loss | Val IoU | Val Dice (F1) | Val Precision | Val Recall |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Sentinel-1 SAR (Selected)** | **2 (VV, VH)** | **0.3548** | **0.5827** | **0.7363** | **0.7410** | **0.7317** |
| Sentinel-2 Optical RGB | 3 (B4, B3, B2) | 0.4412 | 0.5120 | 0.6772 | 0.6950 | 0.6603 |
| S1 SAR + JRC Permanent Water | 3 (VV, VH, JRC) | 0.3690 | 0.5694 | 0.7256 | 0.7280 | 0.7232 |
| S1 SAR + S2 Optical RGB | 5 (VV, VH, R, G, B)| 0.3810 | 0.5510 | 0.7105 | 0.7310 | 0.6912 |
| Full Stack (S1 + S2 + JRC) | 6 Channels | 0.3750 | 0.5640 | 0.7212 | 0.7380 | 0.7051 |

**Model Selection Decision:** Sentinel-1 SAR alone demonstrated the strongest all-weather generalization (Validation IoU: **0.5827**) without susceptibility to optical cloud dropouts.

---

## 15. Full Test-Set Results (Official 90-Chip Evaluation)
The selected Sentinel-1 SAR U-Net was evaluated on **100% of the official test split (90/90 chips)**:

| Metric | Official 90-Chip Test Result |
| :--- | :---: |
| **Test Chips Evaluated** | **90 / 90 (100%)** |
| **Total Valid Pixels Evaluated** | **20,517,367** |
| **Ground Truth Water Pixels** | **2,566,101 (12.51%)** |
| **Test Loss** | **0.3918** |
| **Test IoU (Jaccard Index)** | **0.5548** |
| **Test Dice / F1 Score** | **0.7137** |
| **Test Precision** | **0.7717** |
| **Test Recall** | **0.6637** |
| **Test Overall Accuracy** | **0.9334** |

### Complete Test Confusion Matrix:
* **True Positives (TP):** $1,703,186$ pixels
* **False Positives (FP):** $503,818$ pixels
* **False Negatives (FN):** $862,915$ pixels
* **True Negatives (TN):** $17,447,448$ pixels

---

## 16. Representative Prediction Examples
Saved in `outputs/visualizations/final_test/` as 5-panel diagnostic figures:

1. **Good Case (`USA_905409`):** IoU: **0.9350** | Dice: **0.9664** | Precision: **0.9720** | Recall: **0.9609**. Clean open-water flood expanse with sharp specular demarcation.
2. **Average Case (`Pakistan_694942`):** IoU: **0.3829** | Dice: **0.5538** | Precision: **0.4152** | Recall: **0.8313**. Floodwater across agricultural parcels with high recall and minor over-segmentation.
3. **Difficult Case (`Sri-Lanka_450918`):** IoU: **0.0086** | Dice: **0.0171** | Precision: **0.2317** | Recall: **0.0089**. Complex narrow dendritic waterways surrounded by dense vegetation double-bounce.

---

## 17. Streamlit Application
The application (`app.py`) provides an interactive interface featuring:
* **Mode 1 (Benchmark Evaluation):** Dropdown selector for all 90 test chips displaying Input SAR, Ground Truth, Predicted Flood Mask, Prediction Overlay, and the continuous **Flood Probability Map**.
* **Mode 2 (Custom GeoTIFF Upload):** Accepts user-uploaded dual-band ($VV+VH$) GeoTIFFs, executing validation, normalization, inference, and flood extent quantification.
* **Performance:** Sub-50ms inference latency via `@st.cache_resource` model caching.

---

## 18. Geospatial Area Estimation
Flood surface area is computed as:

$$\text{Nominal Area } (\text{km}^2) = \frac{\text{Detected Water Pixels} \times \text{Pixel Area } (\text{m}^2)}{10^6}$$

**Geospatial Caveat:** Rasters are projected in WGS84 (`EPSG:4326`, angular resolution $\Delta \approx 8.98 \times 10^{-5\circ}$). Pixel ground width in meters varies with $\cos(\text{latitude})$; hence, area figures are documented as **nominal equatorial approximations** ($100\text{ m}^2/\text{pixel}$).

---

## 19. Limitations
1. **Radar Double-Bounce in Vegetation:** Calms surface water creates specular reflection, but flooded trees and dense urban structures induce corner-reflector scattering, generating localized false negatives.
2. **Latitudinal Distortion:** Nominal area calculations assume equatorial square pixels; exact geographic polygon re-projection to local UTM zones is required for physical surveying.
3. **Static Baseline Reliance:** The system relies on the JRC historical permanence layer rather than paired pre-flood SAR acquisitions.

---

## 20. Future Scope
1. **Bi-Temporal SAR Difference Networks:** Ingesting co-registered pre- and post-flood SAR pairs to eliminate permanent water confusion directly.
2. **Critical Infrastructure Overlays:** Intersecting predicted flood polygons with OpenStreetMap road and building vectors to automate evacuation route planning.
3. **Automated Satellite Ingestion Pipelines:** Connecting the model to Copernicus Open Access Hub APIs for real-time automated emergency processing.

---

## 21. Conclusion
This project successfully delivered an academically verified, end-to-end Deep Learning semantic segmentation system for satellite-based flood detection. Optimized with Group Normalization and a Masked BCE + Dice loss, the Sentinel-1 SAR U-Net achieved a **Test IoU of 0.5548** and **Test Dice/F1 of 0.7137** across **20.5 million valid pixels** on the complete 90-chip Sen1Floods11 test split. The accompanying Streamlit application and comprehensive test suite (39/39 passing) confirm presentation and demo readiness.

---

## 22. References
1. Bonafilia, D., Tellman, B., Anderson, T., & Issenberg, E. (2020). *Sen1Floods11: a georeferenced dataset to train and test deep learning flood algorithms for Sentinel-1*. IEEE/CVF Conference on Computer Vision and Pattern Recognition Workshops (CVPRW), 210–211.
2. Ronneberger, O., Fischer, P., & Brox, T. (2015). *U-Net: Convolutional networks for biomedical image segmentation*. International Conference on Medical Image Computing and Computer-Assisted Intervention (MICCAI), 234–241.
3. Wu, Y., & He, K. (2018). *Group normalization*. European Conference on Computer Vision (ECCV), 3–19.
4. Pekel, J. F., Cottam, A., Gorelick, N., & Belward, A. S. (2016). *High-resolution mapping of global surface water and its long-term changes*. Nature, 540(7633), 418–422.
