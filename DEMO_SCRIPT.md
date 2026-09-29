# Live Demonstration Script (2–3 Minutes)
## AI-Based Flood Detection and Mapping Using Satellite Imagery

**Target Audience:** Viva Examination Board / Project Evaluators  
**Application Endpoint:** `http://localhost:8501` (`./.venv/bin/streamlit run app.py`)  

---

### [0:00 – 0:30] 1. Page 1: Project Overview & Motivation
> *(Open the Streamlit app on `1. Project Overview`)*
>
> *"Good morning, respected examiners. Today I am presenting our final year project: **AI-Based Flood Detection and Mapping Using Satellite Imagery**.*
>
> *During severe flood disasters, disaster response authorities urgently need to know the exact spatial boundaries of standing floodwater. Optical satellites like Sentinel-2 fail during active floods due to thick storm clouds. To solve this, our system uses **Sentinel-1 Synthetic Aperture Radar (SAR)**, which emits C-band microwave pulses that penetrate clouds, haze, and darkness 24/7.*
>
> *Our full test benchmark across 90 official test chips ($20,517,367$ valid pixels) achieved a **Test IoU of 0.5548**, **Test Dice/F1 of 0.7137**, and **93.34% overall accuracy**."*

---

### [0:30 – 0:50] 2. Pages 2 & 3: Dataset & How the AI Works
> *(Click `2. Dataset` and then `3. How the AI Works` in the sidebar)*
>
> *"We trained and benchmarked on **Sen1Floods11**, spanning 11 global flood events across 6 continents with 0 data leakage between splits.*
>
> *Our core AI architecture is a customized PyTorch **U-Net** semantic segmentation model. It processes dual-polarization $VV$ and $VH$ radar channels through a 4-stage contracting encoder (32 → 64 → 128 → 256), a 512-channel bottleneck, and an expanding decoder with direct **skip connections** and **Group Normalization ($G=8$)** to preserve fine spatial boundaries like riverbanks and road levees."*

---

### [0:50 – 1:15] 3. Pages 4 & 5: Training & Evaluation
> *(Click `4. Training` and `5. Evaluation`)*
>
> *"We trained the model with AdamW and a domain-specific **Masked BCE + Dice Loss** that dynamically masks out invalid/cloud pixels (`-1`) to prevent gradient corruption while overcoming the 4.86:1 land-to-water class imbalance.*
>
> *On the **Evaluation Dashboard**, examiners can review the confusion matrix of all 20.5 million test pixels: $1,703,186$ True Positives and $17,447,448$ True Negatives."*

---

### [1:15 – 1:40] 4. Page 6: Flood Prediction Gallery
> *(Click `6. Flood Prediction`)*
>
> *"To demonstrate scientific honesty, our **Prediction Gallery** shows three representative cases:
> 1. **High-Performance (USA_905409):** IoU of 0.9350 with pristine open floodplain delineation.
> 2. **Average (Pakistan_694942):** IoU of 0.3829 capturing high-recall flood zones amidst wet soil.
> 3. **Difficult Challenge (Sri-Lanka_450918):** Demonstrating known SAR double-bounce attenuation under dense tropical forest canopies."*

---

### [1:40 – 2:30] 5. Page 7: Live Demo (Benchmark Chip & Custom Upload)
> *(Click `7. Live Demo`)*
>
> *"In **Live Demo Mode A**, we can select any official benchmark chip, adjust the detection threshold, and inspect the 5 diagnostic panels: Input SAR, Ground Truth, Predicted Flood, Prediction Overlay, and the Flood Probability Map.*
>
> *In **Mode B**, users can upload any external dual-polarization Sentinel-1 GeoTIFF raster to extract detected flood pixels, coverage percentage, and nominal flooded area."*

---

### [2:30 – 3:00] 6. Page 8: About & Limitations & Conclusion
> *(Click `8. About / Limitations`)*
>
> *"Our pipeline is fully verified with **39/39 passing unit tests**. We explicitly document key physical considerations including SAR specular physics, the JRC historical water baseline, and nominal WGS84 area scaling.*
>
> *Thank you, and I am now pleased to answer any questions from the examination board."*
