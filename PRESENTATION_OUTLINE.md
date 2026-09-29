# AI-Based Flood Detection and Mapping Using Satellite Imagery
## Final Presentation Slide Outline (12 Slides)

**Target Duration:** 8–10 Minutes  
**Audience:** College Examination Board, Project Guides, and External Examiners  

---

### Slide 1: Title Slide
* **Slide Title:** AI-Based Flood Detection and Mapping Using Satellite Imagery
* **Subtitle:** An Audited Deep Learning Semantic Segmentation System on Sentinel-1 SAR Data
* **Presenter Information:** [Student Name] | Department of Computer Science & Engineering
* **Key Visual / Figure:** High-contrast composite graphic showing Sentinel-1 SAR false-color image side-by-side with predicted cyan flood mask.

---

### Slide 2: The Problem
* **Slide Title:** Disaster Response & The Optical Cloud Barrier
* **Bullet Points:**
  * Floods are the most frequent and costly natural disasters worldwide.
  * Rapid post-disaster flood mapping is vital for relief and evacuation routing.
  * **The Critical Bottleneck:** Optical satellites (Sentinel-2, Landsat) cannot see through storm clouds and heavy precipitation during active flooding.
  * Ground surveys are dangerous, slow, and constrained by blocked access routes.
* **Key Visual / Figure:** Sentinel-2 optical image covered in $100\%$ cloud cover next to clear Sentinel-1 SAR penetrating through the storm.

---

### Slide 3: Motivation & Physics of SAR
* **Slide Title:** Why Synthetic Aperture Radar (SAR)?
* **Bullet Points:**
  * **All-Weather, Day/Night Capability:** Operates in C-band microwave spectrum ($5.405\text{ GHz}$).
  * **Specular Reflection Mechanism:** Smooth standing water reflects radar pulses away from the antenna $\to$ appearing characteristically dark ($<-18\text{ dB}$).
  * **Dual-Polarization Signals:**
    * $VV$ (Vertical transmit / Vertical receive): Highly sensitive to surface water roughness.
    * $VH$ (Vertical transmit / Horizontal receive): Captures depolarized volume scattering from land/vegetation.
* **Key Visual / Figure:** Diagram illustrating specular radar reflection over calm water vs. diffuse backscatter over rough soil/vegetation.

---

### Slide 4: Project Objectives
* **Slide Title:** System Objectives & Engineering Goals
* **Bullet Points:**
  * Ingest and audit the globally diverse **Sen1Floods11** benchmark dataset.
  * Implement an optimized **U-Net** architecture with **Group Normalization ($G=8$)** for batch-size invariant training stability.
  * Formulate a domain-specific **Masked BCE + Dice Loss** ignoring invalid/cloud pixels (`-1`).
  * Perform rigorous evaluation over **100% of the official test split (90 chips)** without data leakage.
  * Build an interactive **Streamlit** application for live demonstration and custom GeoTIFF upload.
* **Key Visual / Figure:** End-to-end pipeline block diagram (Data Ingestion $\to$ Preprocessing $\to$ U-Net $\to$ Masked Loss $\to$ Streamlit UI).

---

### Slide 5: Dataset: Sen1Floods11
* **Slide Title:** Benchmark Dataset & Ingestion Audit
* **Bullet Points:**
  * **Benchmark:** Sen1Floods11 hand-labeled dataset (CVPRW 2020) spanning 11 global flood events across 6 continents.
  * **Dataset Partitions:**
    * Train: 252 chips ($1,008$ GeoTIFFs) | Val: 89 chips ($356$ GeoTIFFs) | Test: 90 chips ($360$ GeoTIFFs) | Bolivia Holdout: 15 chips.
  * **Zero Data Leakage:** Verified pairwise mutual exclusivity across all CSV splits.
  * **Temporal Context:** JRC Global Surface Water 30-year permanence raster provides the pre-flood historical baseline.
* **Key Visual / Figure:** Global map highlighting the 11 flood event locations (USA, Pakistan, Bolivia, Ghana, Mekong, etc.).

---

### Slide 6: Proposed Methodology
* **Slide Title:** End-to-End Deep Learning Pipeline
* **Bullet Points:**
  * **Radiometric Normalization:** Linear scaling of dB backscatter from $[-35, +5]\text{ dB} \to [0, 1]$.
  * **Strided Subsampling:** Spatial resizing to $256 \times 256$ preserving discrete integer labels (`-1, 0, 1`).
  * **Synchronized Augmentation:** Random horizontal/vertical flips and $90^\circ$ rotations applied to images and masks.
  * **Pixel-Level Prediction:** Sigmoid continuous probability generation followed by thresholding at $\tau = 0.50$.
* **Key Visual / Figure:** Flowchart showing preprocessing, tensor formation, forward pass, and binary thresholding.

---

### Slide 7: U-Net Architecture
* **Slide Title:** Customized PyTorch U-Net Architecture
* **Bullet Points:**
  * **Encoder:** 4 contracting stages $[32, 64, 128, 256]$ with double convolutions and max-pooling.
  * **Bottleneck:** 512 channels with spatial dropout ($p=0.10$) to prevent overfitting.
  * **Decoder:** 4 expanding stages with bilinear upsampling and skip-connection feature concatenation.
  * **Group Normalization ($G=8$):** Eliminates batch-size dependency when training on small batch sizes ($\text{batch\_size} = 2$).
  * **Total Parameters:** $7,760,257$ trainable parameters.
* **Key Visual / Figure:** Detailed U-Net architecture diagram showing skip connections, feature channels, and GroupNorm blocks.

---

### Slide 8: Loss Function & Training Configuration
* **Slide Title:** Loss Formulation & Lightweight Training
* **Bullet Points:**
  * **Masked Hybrid Loss:** Evaluated strictly on valid pixels $\mathcal{V} = \{i \mid y_i \neq -1\}$:
    $$\mathcal{L}_{\text{total}} = 0.5 \cdot \mathcal{L}_{\text{BCE}} + 0.5 \cdot \mathcal{L}_{\text{Dice}}$$
  * **BCE Loss:** Guides smooth pixel-level probability convergence.
  * **Dice Loss:** Directly mitigates severe foreground floodwater class imbalance ($12.5\%$ water vs. $87.5\%$ land).
  * **Optimization:** AdamW ($\text{lr} = 5 \times 10^{-4}$), Cosine Annealing, 5 epochs in **~15 seconds** on Apple Silicon MPS.
* **Key Visual / Figure:** Loss and metric convergence curves over training epochs.

---

### Slide 9: Experimental Test Results
* **Slide Title:** Full Test-Set Evaluation (90 / 90 Chips)
* **Results Table:**

| Metric | Full Test Result (90 Chips) | Mathematical Formulation |
| :--- | :---: | :--- |
| **Test IoU (Jaccard)** | **0.5548** | $\text{TP} / (\text{TP} + \text{FP} + \text{FN})$ |
| **Test Dice / F1** | **0.7137** | $2\text{TP} / (2\text{TP} + \text{FP} + \text{FN})$ |
| **Precision** | **0.7717** | $\text{TP} / (\text{TP} + \text{FP})$ |
| **Recall** | **0.6637** | $\text{TP} / (\text{TP} + \text{FN})$ |
| **Overall Accuracy** | **0.9334** | $(\text{TP} + \text{TN}) / \text{Valid Pixels}$ |

* **Confusion Matrix:** $\text{TP} = 1,703,186$ | $\text{FP} = 503,818$ | $\text{FN} = 862,915$ | $\text{TN} = 17,447,448$ ($20.5\text{M}$ valid pixels).
* **Key Visual / Figure:** Representative 5-panel test visualization (`USA_905409`, IoU: $0.9350$).

---

### Slide 10: Interactive Streamlit Demonstration
* **Slide Title:** Streamlit Web Application (`app.py`)
* **Bullet Points:**
  * **Mode 1 — Test Set Evaluation:** Dropdown selection of all 90 benchmark chips with live ground truth overlay, confusion counts, and **Flood Probability Maps**.
  * **Mode 2 — Custom GeoTIFF Upload:** Ingests external Sentinel-1 SAR files, validates $\ge 2$ channels, and maps flood extent.
  * **Nominal Area Estimation:** Computes flooded area in $\text{km}^2$ with interactive probability thresholding slider ($0.10 \to 0.90$).
  * **Inference Latency:** Sub-50ms inference via cached model weights (`@st.cache_resource`).
* **Key Visual / Figure:** Screenshot of the Streamlit user interface showing the 5-panel output and metric cards.

---

### Slide 11: Limitations & Future Scope
* **Slide Title:** Critical Limitations & Future Enhancements
* **Academic Limitations:**
  * **Geospatial Latitudinal Scaling:** WGS84 $\text{EPSG:4326}$ pixel width varies with $\cos(\text{latitude})$; area is reported as a nominal equatorial approximation.
  * **Radar Double-Bounce:** Flooded vegetation can cause corner-reflection backscatter, leading to false negatives in dense canopies.
* **Future Work:**
  * Bi-temporal SAR difference networks (pre-flood and post-flood paired SAR).
  * Integration with OpenStreetMap building and road vector layers for infrastructure damage mapping.
* **Key Visual / Figure:** Illustration of radar double-bounce over flooded vegetation.

---

### Slide 12: Conclusion & Summary
* **Slide Title:** Conclusion & Key Achievements
* **Bullet Points:**
  * Successfully built an end-to-end all-weather flood segmentation pipeline using Sentinel-1 SAR and PyTorch U-Net.
  * Group Normalization and Masked BCE+Dice loss effectively overcame extreme class imbalance and small-batch training noise.
  * Rigorously verified across **100% of the 90-chip Sen1Floods11 test split** ($20.5\text{M}$ pixels) with **$0.5548$ IoU** and **$0.7137$ Dice/F1**.
  * Complete, interactive Streamlit demo verified with **39/39 unit tests passing**.
* **Key Visual / Figure:** Summary badge graphic: 39/39 Tests Passed • 90 Test Chips • U-Net Operational.
