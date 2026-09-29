# FINAL PROJECT SUMMARY REPORT
## AI-Based Flood Detection and Mapping Using Satellite Imagery

**Academic Project Report / Final Documentation**  
**Dataset:** Sen1Floods11 Hand-Labeled Partition  
**Primary Architecture:** Sentinel-1 SAR ($VV + VH$) Dual-Polarization PyTorch U-Net  

---

### 1. Title
**AI-Based Flood Detection and Mapping Using Satellite Imagery: An Audited Deep Learning Semantic Segmentation System on Sentinel-1 SAR Data**

---

### 2. Problem Statement
Flooding is among the most catastrophic and economically damaging natural disasters worldwide. Rapid, accurate post-disaster flood extent mapping is essential for disaster relief, resource allocation, and damage estimation. However, optical satellite sensors (such as Sentinel-2 or Landsat) are frequently blinded by dense cloud cover and precipitation during active flood events. Synthetic Aperture Radar (SAR), such as Sentinel-1, penetrates cloud cover, smoke, and operates day and night, but SAR backscatter imagery suffers from speckle noise, double-bounce reflections from vegetation, and complex terrain geometry, necessitating robust Deep Learning segmentation models.

---

### 3. Objectives
1. **Dataset Ingestion & Pipeline Construction:** Ingest and validate the global **Sen1Floods11** benchmark spanning 11 flood events across 6 continents.
2. **Architecture Implementation:** Develop a memory-efficient, robust PyTorch **U-Net** semantic segmentation architecture with **Group Normalization ($G=8$)** to ensure batch-size invariant normalization.
3. **Domain-Specific Masked Loss Formulation:** Implement a combined binary cross-entropy and Dice loss ($\mathcal{L} = 0.5\mathcal{L}_{\text{BCE}} + 0.5\mathcal{L}_{\text{Dice}}$) calculated strictly over valid pixels ($\mathcal{V} = \{i \mid y_i \neq -1\}$).
4. **Full Test Partition Evaluation:** Evaluate the trained model across all **90 chips** of the official test split (`flood_test_data.csv`) without data leakage or silent exclusions.
5. **Interactive Web Demonstration:** Deploy a lightweight, reproducible **Streamlit** dashboard supporting benchmark test chip evaluation and custom SAR GeoTIFF upload.

---

### 4. Dataset: Sen1Floods11
* **Source:** Cloud to Street / IEEE CVPRW Sen1Floods11 hand-labeled benchmark.
* **Geographic Coverage:** 11 globally distributed flood events (Bolivia, Ghana, India, Mekong/Cambodia, Nigeria, Pakistan, Paraguay, Somalia, Spain, Sri Lanka, USA).
* **Partitions:**
  * **Training Split (`flood_train_data.csv`):** 252 chips ($1,008$ GeoTIFFs)
  * **Validation Split (`flood_valid_data.csv`):** 89 chips ($356$ GeoTIFFs)
  * **Official Test Split (`flood_test_data.csv`):** 90 chips ($360$ GeoTIFFs)
  * **Bolivia Event Split (`flood_bolivia_data.csv`):** 15 chips ($60$ GeoTIFFs)
  * **Data Leakage Verification:** Verified pairwise mutual exclusivity across all CSV splits — **0 overlapping chips detected**.
* **Input Channels Used:**
  * Channel 0: Sentinel-1 $VV$ Polarization (normalized $[-35\text{ dB}, +5\text{ dB}] \to [0, 1]$)
  * Channel 1: Sentinel-1 $VH$ Polarization (normalized $[-35\text{ dB}, +5\text{ dB}] \to [0, 1]$)
* **Labels:** `-1` = Invalid/Cloud/Shadow (ignored), `0` = Land/Dry, `1` = Flood/Water.

---

### 5. Methodology
1. **Radar Preprocessing:** Raw GeoTIFF raster data in decibels (dB) are clipped to $[-35, +5]\text{ dB}$ to filter extreme specular and corner-reflector outliers, then min-max normalized to $[0.0, 1.0]$.
2. **Strided Sub-Sampling:** Satellite chips are subsampled to $256 \times 256$ spatial resolution using strided slicing (`[::stride, ::stride]`), preserving discrete integer mask values (`-1, 0, 1`) without interpolation artifacts.
3. **Synchronized Augmentation:** Random horizontal flipping ($p=0.5$), vertical flipping ($p=0.5$), and orthogonal $90^\circ$ rotations ($p=0.5$) applied identically to input channels and ground-truth targets.
4. **Inference & Thresholding:** The model outputs continuous logits. A Sigmoid function converts logits to pixel-level water probabilities $\hat{p} \in [0, 1]$, thresholded at $\tau = 0.50$ (adjustable via UI).

---

### 6. U-Net Architecture
* **Encoder:** 4 contracting stages $[32, 64, 128, 256]$ with $3\times3$ convolutions, Group Normalization ($G=8$), and GELU activations.
* **Bottleneck:** 512 channels with spatial dropout ($p=0.10$).
* **Decoder:** 4 expanding stages with bilinear upsampling, skip-connection concatenation, and double convolutions.
* **Final Layer:** $1\times1$ convolution producing single-channel logits.
* **Total Trainable Parameters:** **7,760,257 parameters**.

---

### 7. Training Setup
* **Hardware Accelerator:** Apple Silicon MPS (`mps:0`) / CUDA compatible.
* **Batch Size:** 2
* **Total Epochs:** 5 (Early stopping patience: 2 epochs).
* **Optimizer:** AdamW ($\text{lr} = 5 \times 10^{-4}$, $\text{weight\_decay} = 10^{-4}$).
* **Learning Rate Schedule:** Cosine Annealing ($\eta_{\text{min}} = 10^{-5}$).
* **Total Training Wall-Clock Time:** **~15.2 seconds** (~3.0 s/epoch).

---

### 8. Evaluation Metrics & Formulations
All metrics are evaluated exclusively over valid pixels $\mathcal{V} = \{i \mid y_i \neq -1\}$:
* **Intersection over Union (IoU / Jaccard Index):**
  $$\text{IoU} = \frac{\text{TP}}{\text{TP} + \text{FP} + \text{FN}}$$
* **Dice Coefficient / F1 Score:**
  $$\text{Dice} = \frac{2 \cdot \text{TP}}{2 \cdot \text{TP} + \text{FP} + \text{FN}} = \text{F1}$$
* **Precision:**
  $$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}$$
* **Recall (Sensitivity):**
  $$\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}$$
* **Overall Pixel Accuracy:**
  $$\text{Accuracy} = \frac{\text{TP} + \text{TN}}{\text{Total Valid Pixels}}$$

---

### 9. Final Test Results (Official 90-Chip Benchmark)

The model was evaluated across **100% of the official test split (90/90 chips)**:

| Metric | Verified Score |
| :--- | :---: |
| **Official Test Chips Evaluated** | **90 / 90 (100%)** |
| **Total Valid Pixels Evaluated** | **20,517,367** |
| **Ground Truth Water Pixels** | **2,566,101 (12.51%)** |
| **Test Loss** | **0.3918** |
| **Test IoU (Jaccard Index)** | **0.5548** |
| **Test Dice / F1 Score** | **0.7137** |
| **Test Precision** | **0.7717** |
| **Test Recall** | **0.6637** |
| **Test Overall Accuracy** | **0.9334** |

#### Complete Test Pixel Confusion Matrix:
* **True Positives (TP):** $1,703,186$ pixels
* **False Positives (FP):** $503,818$ pixels
* **False Negatives (FN):** $862,915$ pixels
* **True Negatives (TN):** $17,447,448$ pixels

---

### 10. Streamlit Interactive Demo Features
* **Mode 1 — Benchmark Test Sample Prediction:**
  * Dropdown selector for all 90 official test chips.
  * Side-by-side diagnostic panels: Input SAR composite ($VV, VH, \text{Ratio}$), Ground Truth mask, Predicted Flood mask, Model Overlay, and Probability Heatmap.
  * Quantitative breakdown: IoU, Dice/F1, Precision, Recall, confusion matrix pixel counts, and nominal flooded area.
* **Mode 2 — Custom SAR GeoTIFF Upload:**
  * File uploader accepting raw `.tif` / `.tiff` dual-polarization Sentinel-1 files.
  * Validates channel count ($\ge 2$), applies normalization, executes fast inference, and estimates flood extent and nominal area.
* **User Control:** Interactive probability threshold slider ($0.10 \to 0.90$).
* **Performance:** Sub-50ms inference per chip via `@st.cache_resource` model caching.

---

### 11. Limitations & Geospatial Considerations
1. **Nominal Area Approximation:** Sen1Floods11 rasters are projected in WGS84 (`EPSG:4326`) with angular resolution $\Delta \approx 8.98 \times 10^{-5\circ}$. Physical meter width varies with $\cos(\text{latitude})$. Reported $\text{km}^2$ values are documented nominal equatorial approximations ($100\text{ m}^2/\text{pixel}$).
2. **Double-Bounce & Dense Canopies:** Smooth open water specularly reflects radar energy (low backscatter $<-18\text{ dB}$), but flooded vegetation can cause corner-reflector double-bounce, occasionally resulting in localized false negatives.
3. **Temporal Baseline Definition:** Pre-flood surface baseline is derived from the JRC Global Surface Water 30-year permanence raster as Sen1Floods11 does not provide separate pre-flood SAR files.

---

### 12. Future Scope
1. **Bi-Temporal SAR Difference Networks:** Integrating co-registered pre-flood and post-flood SAR acquisitions to distinguish floodwater from permanent water directly without auxiliary optical baselines.
2. **Building Damage & Critical Infrastructure Intersection:** Overlaying OpenStreetMap building footprints and road networks on predicted flood masks to estimate stranded populations and blocked evacuation routes.
3. **Cloud-Native Deployment:** Deploying the inference engine as an AWS Lambda / Google Cloud Run container hooked to Sentinel-1 Copernicus Open Access Hub webhooks for automated real-time flood alerting.

---

### 13. Conclusion
The project successfully designed, implemented, validated, and evaluated an end-to-end Deep Learning semantic segmentation system for all-weather flood detection using Sentinel-1 SAR imagery. The model achieved a **Test IoU of 0.5548** and **Test Dice/F1 of 0.7137** across all **90 chips (20.5M valid pixels)** of the official Sen1Floods11 test benchmark. The accompanying Streamlit application provides a robust, presentation-ready demonstration platform for academic assessment and viva examination.
