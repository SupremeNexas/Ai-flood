# Technical Methodology & Pipeline Documentation
## AI-Based Flood Detection and Mapping Using Satellite Imagery

---

## 1. System Pipeline Overview

The flood delineation framework processes raw satellite imagery through a deterministic, end-to-end Deep Learning pipeline:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. SATELLITE RADAR ACQUISITION                                              │
│    • Sentinel-1 C-band SAR (Level-1 GRD, IW mode)                           │
│    • Dual-polarization channels: VV and VH backscatter in decibels (dB)     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. RADIOMETRIC PREPROCESSING & NORMALIZATION                                │
│    • Outlier clipping to [-35.0 dB, +5.0 dB]                                │
│    • Min-Max scaling to [0.0, 1.0]                                          │
│    • Strided subsampling to 256 x 256 resolution                            │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. INPUT TENSOR FORMATION                                                   │
│    • Tensor shape: (B, 2, 256, 256) where C=0 is VV and C=1 is VH          │
│    • Synchronized geometric augmentations (HFlip, VFlip, Rot90)             │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. U-NET ENCODER (FEATURE EXTRACTION)                                       │
│    • 4 contracting stages: [32, 64, 128, 256] feature maps                  │
│    • Double 3x3 convolutions with GroupNorm (G=8) & GELU activations        │
│    • 2x2 Max-Pooling for spatial downsampling                               │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 5. BOTTLENECK LAYER                                                         │
│    • 512 channels with spatial Dropout (p = 0.10)                           │
│    • Captures global regional topological & contextual relationships        │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 6. U-NET DECODER (HIGH-RESOLUTION LOCALIZATION)                             │
│    • 4 expanding stages: [256, 128, 64, 32] feature maps                    │
│    • Bilinear upsampling with skip-connection channel concatenation         │
│    • Restores fine edge boundaries (canals, coastlines, agricultural bunds) │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 7. PIXEL-LEVEL PROBABILITY GENERATION & THRESHOLDING                        │
│    • 1x1 Convolution produces raw continuous logits z                       │
│    • Sigmoid activation generates Flood Probability Map p ∈ [0, 1]          │
│    • Thresholding at τ = 0.50 creates binary flood mask (0 = Land, 1 = Water)
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 8. GEOSPATIAL VISUALIZATION & AREA ESTIMATION                               │
│    • Generates 5-panel diagnostic figures and high-contrast Cyan overlays   │
│    • Computes Nominal Flooded Area (km² nominal) with documented caveat     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Technical Justifications & Architectural Decisions

### A. Why Sentinel-1 Synthetic Aperture Radar (SAR)?
1. **All-Weather Penetration:** Floods are triggered by heavy rain, tropical storms, and monsoons. Optical sensors (e.g., Sentinel-2 MSI, Landsat 8/9) are completely blinded by dense cloud cover and precipitation during active crises. Sentinel-1 transmits C-band microwave pulses at $5.405\text{ GHz}$ ($\lambda \approx 5.55\text{ cm}$), which penetrate clouds, smoke, atmospheric haze, and darkness.
2. **Specular Water Physics:** Smooth surface water behaves as a specular reflector for radar waves. The transmitted pulse bounces away from the sensor, returning near-zero backscatter ($<-18\text{ dB}$). In contrast, rough soil, vegetation, and urban infrastructure produce diffuse backscatter, creating a stark physical contrast for segmentation models.

### B. Why Dual-Polarization ($VV + VH$)?
* **$VV$ Polarization (Vertical Transmit / Vertical Receive):** Sensitive to surface dielectric properties and surface roughness. It delivers sharp contrast at the air-water boundary.
* **$VH$ Polarization (Vertical Transmit / Horizontal Receive):** Depolarized cross-talk scattering is generated by volume scattering from vegetation canopies and agricultural crops. Combining $VV$ and $VH$ allows the model to distinguish between smooth calm open water and flat bare soil or wet asphalt.
* **$VV/VH$ Cross-Ratio:** The ratio between co-polarization and cross-polarization backscatter highlights subtle structural boundaries along coastlines and levees.

### C. Why Group Normalization ($G=8$) Instead of Batch Normalization?
* **Batch Size Invariance:** Batch Normalization computes mean and variance across the batch dimension. In remote sensing segmentation tasks, memory constraints limit batch sizes to small values ($\text{batch\_size} = 2$). Small batch sizes introduce high statistical variance and instability in BatchNorm.
* **Geographic Heterogeneity:** Satellite chips come from globally distinct biomes (e.g., arid floodplains in Somalia vs. tropical wetlands in the Mekong Delta). BatchNorm causes cross-sample feature corruption when diverse scenes share a small batch.
* **GroupNorm Solution:** Group Normalization divides the channels of each individual sample into $G=8$ groups and computes normalization statistics strictly within each sample, completely eliminating batch-size dependency.

### D. Why Combined Masked BCE + Dice Loss?
* **Extreme Class Imbalance:** Floodwater accounts for only $12.5\%$ of pixels in the Sen1Floods11 benchmark dataset ($87.5\%$ dry land). Standard Cross-Entropy loss causes networks to converge toward predicting all-land backgrounds.
* **Dice Loss Complement:** The Soft Dice loss directly optimizes the intersection over union metric, penalizing false negatives and forcing the network to delineate small water channels.
* **BCE Loss Stability:** BCE provides smooth, convex gradients during early training epochs, preventing local optima.
* **Hybrid Formulation:**
  $$\mathcal{L}_{\text{total}} = 0.5 \cdot \mathcal{L}_{\text{BCE}}(\mathbf{\hat{p}}_{\mathcal{V}}, \mathbf{y}_{\mathcal{V}}) + 0.5 \cdot \mathcal{L}_{\text{Dice}}(\mathbf{\hat{p}}_{\mathcal{V}}, \mathbf{y}_{\mathcal{V}})$$

### E. Why Ignore Invalid (`-1`) Pixels?
In Sen1Floods11, invalid pixels include cloud shadows, sensor no-data borders, and unannotated edge artifacts. If treated as land (`0`), the model would learn incorrect negative priors; if treated as water (`1`), it would hallucinate flooding. Calculating loss strictly over valid pixels $\mathcal{V} = \{i \mid y_i \neq -1\}$ guarantees unbiased parameter gradients.

---

## 3. Pixel-Level Segmentation vs. Image Classification

| Aspect | Image Classification | Semantic Segmentation (Proposed U-Net) |
| :--- | :--- | :--- |
| **Output** | Single global label (e.g., "Flooded Scene") | Dense $256 \times 256$ binary mask ($y_i \in \{0, 1\}$) |
| **Spatial Localization** | None (cannot identify which areas are submerged)| Exact pixel-by-pixel geographic boundary delineation |
| **Actionability** | Low (only alerts that an event exists) | High (enables flood polygon extraction and area mapping) |
| **Area Quantification** | Impossible | Directly computed by integrating detected water pixels |

---

## 4. Geospatial Area Estimation & Latitudinal Scaling

The nominal flooded area is calculated as:

$$\text{Nominal Flooded Area } (\text{km}^2) = \frac{\sum_{i \in \mathcal{V}} \mathbb{I}(\hat{p}_i \ge \tau) \times (10.0\text{ m} \times 10.0\text{ m})}{1,000,000\text{ m}^2/\text{km}^2}$$

### The WGS84 Latitudinal Approximation:
* Sen1Floods11 GeoTIFF rasters are distributed in the Geographic Coordinate Reference System WGS84 (`EPSG:4326`), where coordinates are defined in angular degrees ($\Delta \approx 8.98 \times 10^{-5\circ}$).
* At the equator ($\text{lat} = 0^\circ$), $1^\circ \approx 111.32\text{ km}$, giving $\Delta \approx 10.0\text{ m/pixel}$ ($100\text{ m}^2$).
* As latitude $\phi$ increases toward the poles, the physical width of a degree of longitude decreases proportionally with $\cos(\phi)$:
  $$\Delta x_{\text{meters}}(\phi) = \Delta \times 111,320 \times \cos(\phi)$$
* Therefore, all $\text{km}^2$ metrics in this project are strictly documented as **nominal equatorial approximations**. Physical surveying requires local UTM projection re-sampling.
