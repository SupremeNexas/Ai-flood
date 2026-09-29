# Comprehensive Viva Voce Questions & Answers
## AI-Based Flood Detection and Mapping Using Satellite Imagery

A curated set of 25 likely questions and precise, academically rigorous answers for project examination and viva defense.

---

### Q1: Why is automated flood detection an important research problem?
**Answer:** Floods are the most frequent, destructive, and economically costly natural disasters globally. Rapid, automated flood mapping provides emergency disaster response agencies with accurate, real-time spatial footprints of submerged infrastructure, enabling efficient relief distribution, evacuation routing, and accurate economic loss assessment.

---

### Q2: Why use satellite remote sensing instead of drones or ground surveys?
**Answer:** Ground surveys are hazardous, slow, and constrained by submerged or damaged roads. Drones have limited flight range, short battery life, and cannot operate safely in heavy storm turbulence. Satellites provide systematic, wide-area synoptic coverage ($>100\text{ km}$ swaths) across remote and inaccessible global regions without endangering personnel.

---

### Q3: What is Sentinel-1, and why was it chosen for this project?
**Answer:** Sentinel-1 is a European Space Agency (ESA) Copernicus satellite constellation carrying a C-band ($5.405\text{ GHz}$) Synthetic Aperture Radar (SAR). It was chosen because radar waves penetrate through dense storm clouds, precipitation, smoke, and operate day and night, providing reliable all-weather imaging during active flooding.

---

### Q4: What do the terms "VV" and "VH" polarizations mean in SAR?
**Answer:** 
* **VV (Vertical transmit / Vertical receive):** Co-polarization signal sensitive to surface roughness and dielectric permittivity, providing sharp contrast at water-land boundaries.
* **VH (Vertical transmit / Horizontal receive):** Cross-polarization signal sensitive to depolarized volume scattering from vegetation canopies and rough terrain. Combining both helps distinguish smooth water from flat soil.

---

### Q5: Why is SAR preferred over optical RGB imagery for flood detection?
**Answer:** Optical RGB sensors (like Sentinel-2 or Landsat) capture reflected sunlight and are completely obstructed by cloud cover during active storm events. SAR emits its own microwave pulses that pass directly through clouds, providing uninterrupted visibility of standing surface water on the ground.

---

### Q6: What is semantic segmentation, and how does it differ from image classification?
**Answer:** Image classification assigns a single categorical label to an entire image (e.g., "flooded" vs. "non-flooded"). Semantic segmentation assigns a class label to **every individual pixel** in the spatial raster ($256 \times 256$), allowing precise spatial boundary delineation and exact flooded area calculations.

---

### Q7: Why is the U-Net architecture specifically suited for this task?
**Answer:** U-Net has an encoder-decoder topology with contracting feature extraction and expanding spatial reconstruction. Its key strength is **skip connections**, which route high-resolution spatial feature maps directly from encoder stages to corresponding decoder stages, preventing the loss of fine spatial details (canals, coastlines, levees) during downsampling.

---

### Q8: What is the specific function of skip connections in U-Net?
**Answer:** Downsampling (pooling) compresses spatial dimensions to learn abstract contextual representations but destroys exact spatial coordinates. Skip connections concatenate earlier high-resolution feature maps into the decoder, giving the network both high-level semantic context (identifying flood regions) and precise spatial localization (identifying exact water borders).

---

### Q9: Why use a combined BCE + Dice loss rather than standard Cross-Entropy?
**Answer:** In flood segmentation, water pixels comprise only $\approx 12.5\%$ of the scene, creating severe foreground-background class imbalance. Standard Cross-Entropy biases predictions toward the dominant land class. Dice loss directly optimizes the intersection over union (foreground overlap), while BCE provides smooth, stable gradient descent.

---

### Q10: Why are `-1` labeled pixels ignored during loss computation?
**Answer:** In the Sen1Floods11 dataset, `-1` represents invalid data, cloud shadows, or no-data border pixels. Treating them as land (`0`) or water (`1`) would introduce severe label noise and distort backpropagation gradients. Restricting loss to valid pixels $\mathcal{V} = \{i \mid y_i \neq -1\}$ ensures unbiased parameter updates.

---

### Q11: What is Intersection over Union (IoU / Jaccard Index)?
**Answer:** IoU measures the spatial overlap between the predicted water mask and the ground-truth water mask:
$$\text{IoU} = \frac{\text{Area of Overlap}}{\text{Area of Union}} = \frac{\text{TP}}{\text{TP} + \text{FP} + \text{FN}}$$
It strictly penalizes both false positives and false negatives, making it the gold standard for segmentation benchmarks.

---

### Q12: What is the Dice Coefficient, and how does it relate to F1-Score?
**Answer:** The Dice Coefficient measures harmonic similarity between prediction and ground truth:
$$\text{Dice} = \frac{2 \cdot \text{TP}}{2 \cdot \text{TP} + \text{FP} + \text{FN}}$$
For binary segmentation over valid pixels, the Dice Coefficient is mathematically identical to the harmonic mean of Precision and Recall (the F1-Score).

---

### Q13: What is the fundamental difference between Precision and Recall in flood detection?
**Answer:**
* **Precision ($\frac{\text{TP}}{\text{TP} + \text{FP}}$):** Out of all pixels predicted as floodwater, how many were actually water (measures false alarms/over-prediction).
* **Recall ($\frac{\text{TP}}{\text{TP} + \text{FN}}$):** Out of all actual ground-truth flood pixels, how many did the model detect (measures missed flood areas/under-prediction).

---

### Q14: Why is Overall Pixel Accuracy insufficient as a primary evaluation metric?
**Answer:** Due to class imbalance ($87.5\%$ land vs. $12.5\%$ water), a naive model that predicts "all land" would achieve $87.5\%$ accuracy while detecting $0\%$ of the flood. IoU and Dice are class-imbalance robust because they focus exclusively on the foreground water class.

---

### Q15: What is data leakage, and why is it dangerous in Machine Learning?
**Answer:** Data leakage occurs when training data shares samples, locations, or information with the validation or test splits. This produces artificially inflated performance during testing that fails completely when deployed on real-world unseen data.

---

### Q16: How did you verify that no data leakage exists in your pipeline?
**Answer:** We performed pairwise mutual exclusivity audits across the official training (252 chips), validation (89 chips), test (90 chips), and Bolivia holdout (15 chips) CSV splits. We verified that the set intersection between all splits was strictly empty (**0 overlapping chips**).

---

### Q17: What does the input tensor to the model look like?
**Answer:** A 4D PyTorch FloatTensor of shape $(B, 2, 256, 256)$, where $B$ is the batch size, channel 0 is normalized Sentinel-1 $VV$ backscatter in $[0, 1]$, and channel 1 is normalized Sentinel-1 $VH$ backscatter in $[0, 1]$.

---

### Q18: What is the output of the model?
**Answer:** The model outputs continuous logit tensors of shape $(B, 256, 256)$. Applying the Sigmoid activation function produces a continuous **Flood Probability Map** $\hat{p} \in [0, 1]$. Applying a threshold ($\tau = 0.50$) produces a discrete binary flood mask ($0 = \text{Land}, 1 = \text{Water}$).

---

### Q19: How is the flooded surface area calculated from the model output?
**Answer:** By summing all positive water pixels ($N_{\text{water}}$) and multiplying by the nominal pixel area ($10\text{ m} \times 10\text{ m} = 100\text{ m}^2$):
$$\text{Nominal Area } (\text{km}^2) = \frac{N_{\text{water}} \times 100\text{ m}^2}{1,000,000\text{ m}^2/\text{km}^2}$$

---

### Q20: Why is the calculated flooded area explicitly described as "nominal"?
**Answer:** The dataset rasters are projected in Geographic Coordinates (WGS84 `EPSG:4326`), where pixel width is fixed in angular degrees ($\approx 8.98 \times 10^{-5\circ}$). On Earth's ellipsoid, physical ground distance in meters varies with $\cos(\text{latitude})$. Hence, $10\text{ m/pixel}$ is a nominal equatorial approximation.

---

### Q21: What are the main physical limitations of SAR-based flood detection?
**Answer:**
1. **Double-Bounce Scattering:** Submerged tree trunks and building walls create corner reflections, sending strong radar signals back and appearing bright (causing false negatives in flooded forests/cities).
2. **Smooth Non-Water Surfaces:** Sand dunes, smooth airport runways, and dry flat asphalt can cause specular reflection, appearing dark like water (causing false positives).
3. **Wind-Ruffled Water:** Strong storm winds roughen water surfaces, increasing backscatter and reducing contrast.

---

### Q22: Why did you use Group Normalization instead of Batch Normalization?
**Answer:** Batch Normalization calculates mean and variance across the batch dimension. With small batch sizes ($\text{batch\_size} = 2$) and geographically diverse scenes, BatchNorm statistics become noisy and unstable. Group Normalization ($G=8$) normalizes channels per sample independently of batch size, providing stable convergence.

---

### Q23: What happens when a user uploads a custom SAR GeoTIFF in Mode 2?
**Answer:** The system reads the raster via Rasterio, validates that at least 2 channels ($VV, VH$) exist, normalizes the dB range to $[0, 1]$, subsamples to $256 \times 256$, executes forward inference on the cached U-Net, and outputs the predicted mask, overlay, Flood Probability Map, and nominal area estimate. Ground truth metrics are omitted since reference labels do not exist for custom uploads.

---

### Q24: What is the purpose of the Streamlit application?
**Answer:** It provides an interactive, presentation-ready graphical user interface for non-technical stakeholders and disaster managers. Users can visually inspect benchmark test chips, toggle probability thresholds, view multi-panel diagnostics, and upload arbitrary SAR GeoTIFFs for rapid visual assessment.

---

### Q25: What future enhancements could be added to this project?
**Answer:**
1. **Bi-Temporal SAR Difference Networks:** Using paired pre-flood and post-flood SAR acquisitions to eliminate permanent water confusion directly.
2. **Infrastructure Impact Overlay:** Intersecting predicted flood polygons with OpenStreetMap road networks and building footprints to compute damaged assets.
3. **Real-Time API Integration:** Connecting the model to European Space Agency Copernicus Hub APIs for automated ingestion and disaster alerting.
