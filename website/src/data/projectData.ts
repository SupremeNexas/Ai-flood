export interface MetricItem {
  label: string;
  value: string;
  subtext: string;
  description: string;
}

export interface SplitItem {
  name: string;
  chips: number;
  files: number;
  percentage: number;
  color: string;
}

export interface PixelCompositionItem {
  label: string;
  value: number;
  formatted: string;
  percentage: number;
  color: string;
  role: string;
}

export interface PredictionCase {
  id: string;
  title: string;
  category: "Good Prediction" | "Average Prediction" | "Difficult Challenge";
  stem: string;
  event: string;
  region: string;
  iou: number;
  dice: number;
  precision: number;
  recall: number;
  gtWaterPixels: number;
  predWaterPixels: number;
  nominalAreaKm2: number;
  gtAreaKm2: number;
  imagePath: string;
  highlights: string[];
  physicsExplanation: string;
}

export const PROJECT_METADATA = {
  title: "AI-Based Flood Detection and Mapping Using Satellite Imagery",
  subtitle: "Sen1Floods11 • Sentinel-1 SAR • PyTorch U-Net",
  shortTitle: "FloodAI",
  academicContext: "Academic Minor Project • Computer Science & Engineering (AI/ML)",
  domain: "Deep Learning • Computer Vision • Earth Observation & Remote Sensing",
  streamlitUrl: process.env.NEXT_PUBLIC_STREAMLIT_URL || "https://ai-flood-detection.onrender.com",
  githubUrl: process.env.NEXT_PUBLIC_GITHUB_URL || "https://github.com/SupremeNexas/Ai-flood",
};

export const VERIFIED_BENCHMARKS = {
  iou: 0.5548,
  dice: 0.7137,
  precision: 0.7717,
  recall: 0.6637,
  accuracy: 0.9334,
  testChips: "90 / 90",
  validPixels: "20,517,367",
  parameters: "7,760,257",
  unitTests: "39 / 39",
  dataLeakage: "0 Overlapping Chips",
};

export const CORE_KPIS: MetricItem[] = [
  {
    label: "Test IoU",
    value: "0.5548",
    subtext: "Jaccard Index",
    description: "Evaluated across all 90 official benchmark test chips (20,517,367 valid pixels)",
  },
  {
    label: "Test Dice / F1",
    value: "0.7137",
    subtext: "Harmonic Mean",
    description: "Balanced harmonic mean of precision and recall on the positive flood class",
  },
  {
    label: "Precision",
    value: "0.7717",
    subtext: "True Positives / Predicted",
    description: "77.17% of all AI-predicted flood pixels represent true standing water",
  },
  {
    label: "Recall",
    value: "0.6637",
    subtext: "True Positives / Ground Truth",
    description: "66.37% of all ground-truth floodwater was successfully detected",
  },
];

export const AUX_STATS = [
  { label: "Official Test Chips", value: "90 / 90", subtext: "100% Coverage" },
  { label: "Valid Test Pixels", value: "20.5M", subtext: "20,517,367 px" },
  { label: "Model Parameters", value: "7.76M", subtext: "7,760,257 params" },
  { label: "Unit Test Suite", value: "39 / 39", subtext: "100% Passing" },
];

export const DATASET_SPLITS: SplitItem[] = [
  { name: "Training Split", chips: 252, files: 1008, percentage: 56.5, color: "#3B82F6" },
  { name: "Validation Split", chips: 89, files: 356, percentage: 20.0, color: "#10B981" },
  { name: "Official Test Split", chips: 90, files: 360, percentage: 20.2, color: "#EF4444" },
  { name: "Bolivia Holdout", chips: 15, files: 60, percentage: 3.4, color: "#F59E0B" },
];

export const PIXEL_COMPOSITION: PixelCompositionItem[] = [
  {
    label: "Non-Water / Land (0)",
    value: 8888253,
    formatted: "8,888,253 px",
    percentage: 69.19,
    color: "#475569",
    role: "Background negative class",
  },
  {
    label: "Water / Flood (1)",
    value: 1828756,
    formatted: "1,828,756 px",
    percentage: 14.24,
    color: "#00D2FF",
    role: "Supervised target flood class",
  },
  {
    label: "Invalid / Cloud / No-Data (-1)",
    value: 2128047,
    formatted: "2,128,047 px",
    percentage: 16.57,
    color: "#ECC94B",
    role: "Masked out dynamically during loss calculation",
  },
];

export const CONFUSION_MATRIX = {
  tp: 1703186,
  fp: 503818,
  fn: 862915,
  tn: 17447448,
  totalValid: 20517367,
  waterGt: 2566101,
  landGt: 17951266,
};

export const TRAINING_CONFIG = {
  epochs: 5,
  batchSize: 2,
  imageDimension: "256 × 256",
  optimizer: "AdamW (betas=[0.9, 0.999])",
  learningRate: "0.0005",
  weightDecay: "0.0001",
  lossFunction: "Masked BCE + Dice (0.5 * BCE + 0.5 * Dice)",
  scheduler: "Cosine Annealing (min_lr=1e-5)",
  normalization: "GroupNorm (G=8, num_groups=8)",
  bestValIoU: 0.8255,
  bestValDice: 0.9044,
};

export const TRAINING_HISTORY = [
  { epoch: 1, trainLoss: 0.584, valLoss: 0.512, valIoU: 0.542, valDice: 0.703 },
  { epoch: 2, trainLoss: 0.465, valLoss: 0.428, valIoU: 0.678, valDice: 0.808 },
  { epoch: 3, trainLoss: 0.412, valLoss: 0.369, valIoU: 0.745, valDice: 0.854 },
  { epoch: 4, trainLoss: 0.391, valLoss: 0.338, valIoU: 0.796, valDice: 0.886 },
  { epoch: 5, trainLoss: 0.380, valLoss: 0.322, valIoU: 0.826, valDice: 0.904 },
];

export const UNET_ARCHITECTURE_SPECS = {
  inputChannels: 2,
  inputDim: "2 × 256 × 256 (VV, VH)",
  encoderLevels: [
    { name: "Encoder 1", channels: 32, resolution: "256 × 256", params: "~19K" },
    { name: "Encoder 2", channels: 64, resolution: "128 × 128", params: "~74K" },
    { name: "Encoder 3", channels: 128, resolution: "64 × 64", params: "~295K" },
    { name: "Encoder 4", channels: 256, resolution: "32 × 32", params: "~1.18M" },
  ],
  bottleneck: { name: "Bottleneck", channels: 512, resolution: "16 × 16", params: "~4.72M" },
  decoderLevels: [
    { name: "Decoder 1", channels: 256, resolution: "32 × 32", params: "~1.18M" },
    { name: "Decoder 2", channels: 128, resolution: "64 × 64", params: "~295K" },
    { name: "Decoder 3", channels: 64, resolution: "128 × 128", params: "~74K" },
    { name: "Decoder 4", channels: 32, resolution: "256 × 256", params: "~19K" },
  ],
  outputChannels: 1,
  outputDim: "1 × 256 × 256 (Logits → Sigmoid Probability)",
  totalParameters: 7760257,
};

export const PIPELINE_STAGES = [
  {
    step: 1,
    title: "Satellite SAR Acquisition",
    subtitle: "Sentinel-1 Level-1 GRD",
    desc: "Active C-band microwave radar pulses (5.405 GHz) penetrating clouds, rain, and darkness.",
    icon: "Satellite",
    badge: "All-Weather",
  },
  {
    step: 2,
    title: "Dual Polarization (VV + VH)",
    subtitle: "Surface & Volume Scattering",
    desc: "VV channel captures surface water specular reflections; VH captures vegetation texture.",
    icon: "Radio",
    badge: "2 Channels",
  },
  {
    step: 3,
    title: "Radiometric Normalization",
    subtitle: "[-35 dB, +5 dB] → [0.0, 1.0]",
    desc: "Decibel backscatter outlier clamping and linear min-max scaling for neural stability.",
    icon: "Sliders",
    badge: "Preprocessing",
  },
  {
    step: 4,
    title: "Spatial Tensor Formatting",
    subtitle: "(B, 2, 256, 256)",
    desc: "Strided spatial sampling preserving integer mask labels without interpolation distortion.",
    icon: "Grid",
    badge: "256×256 px",
  },
  {
    step: 5,
    title: "PyTorch U-Net Inference",
    subtitle: "4-Stage Encoder-Decoder",
    desc: "7.76M parameters with GroupNorm (G=8) and direct skip connections for boundary preservation.",
    icon: "Cpu",
    badge: "Deep CNN",
  },
  {
    step: 6,
    title: "Pixel-Level Segmentation",
    subtitle: "Dense Spatial Classification",
    desc: "Every single 10m spatial pixel receives a dense classification without scene-level generalization.",
    icon: "Target",
    badge: "Pixel-Wise",
  },
  {
    step: 7,
    title: "Flood Probability Map",
    subtitle: "Sigmoid Activation [0.0, 1.0]",
    desc: "Continuous model probability output representing pixel-wise inundation likelihood.",
    icon: "Activity",
    badge: "Continuous",
  },
  {
    step: 8,
    title: "Binary Flood Mask",
    subtitle: "Threshold Cutoff (p ≥ 0.50)",
    desc: "Discrete binary delineation separating standing floodwater (1) from dry terrain (0).",
    icon: "Shield",
    badge: "Threshold",
  },
  {
    step: 9,
    title: "Nominal Flooded Area",
    subtitle: "~100 m² per Pixel",
    desc: "Rapid spatial extent assessment with documented WGS84 latitudinal scaling caveats.",
    icon: "MapPin",
    badge: "Quantification",
  },
];

export const PREDICTION_CASES: PredictionCase[] = [
  {
    id: "good",
    title: "Case 1: High-Performance Delineation",
    category: "Good Prediction",
    stem: "USA_905409",
    event: "United States (Midwest Flooding)",
    region: "Agricultural Floodplain & River Basin",
    iou: 0.9350,
    dice: 0.9664,
    precision: 0.9720,
    recall: 0.9609,
    gtWaterPixels: 44467,
    predWaterPixels: 43959,
    nominalAreaKm2: 4.396,
    gtAreaKm2: 4.447,
    imagePath: "/images/final_test/1_good_prediction_USA_905409.png",
    highlights: [
      "Smooth open water specular reflections cleanly captured by VV backscatter",
      "Near-perfect boundary alignment on agricultural field levees",
      "IoU exceeds 0.93 with 97.2% precision and minimal false alarms",
    ],
    physicsExplanation:
      "Open floodwaters create a flat, mirror-like surface causing specular reflection away from the Sentinel-1 SAR antenna. This produces low backscatter values (<-18 dB) with high contrast against surrounding vegetated soil.",
  },
  {
    id: "average",
    title: "Case 2: Average Regional Inundation",
    category: "Average Prediction",
    stem: "Pakistan_694942",
    event: "Pakistan (Indus River Basin)",
    region: "Complex Irrigation Network & Saturated Soil",
    iou: 0.3829,
    dice: 0.5538,
    precision: 0.4152,
    recall: 0.8313,
    gtWaterPixels: 18481,
    predWaterPixels: 37006,
    nominalAreaKm2: 3.701,
    gtAreaKm2: 1.848,
    imagePath: "/images/final_test/2_average_prediction_Pakistan_694942.png",
    highlights: [
      "High recall (83.13%) captures all primary flooded corridors",
      "Saturated muddy soils produce partial radar specular reflection",
      "Demonstrates typical real-world tradeoff between recall and false positives",
    ],
    physicsExplanation:
      "Waterlogged soils and narrow irrigation ditches reduce radar backscatter similarly to standing water, resulting in moderate over-segmentation (False Positives) while maintaining high disaster detection recall.",
  },
  {
    id: "difficult",
    title: "Case 3: Difficult Challenge & Physical Limitation",
    category: "Difficult Challenge",
    stem: "Sri-Lanka_450918",
    event: "Sri Lanka (Tropical Monsoon Inundation)",
    region: "Dense Tropical Rainforest & Mountainous Terrain",
    iou: 0.0086,
    dice: 0.0171,
    precision: 0.2317,
    recall: 0.0089,
    gtWaterPixels: 4277,
    predWaterPixels: 164,
    nominalAreaKm2: 0.016,
    gtAreaKm2: 0.428,
    imagePath: "/images/final_test/3_difficult_prediction_Sri-Lanka_450918.png",
    highlights: [
      "Dense rainforest canopy absorbs and double-bounces C-band microwave radar",
      "Sub-canopy standing water obscured from SAR sensor view",
      "Documented physical limitation honestly presented without omission",
    ],
    physicsExplanation:
      "Sentinel-1 C-band microwaves (5.6 cm wavelength) scatter off dense tropical forest leaves and branches rather than penetrating to ground level. Corner reflection between vertical trunks and standing water creates bright backscatter instead of dark pixels.",
  },
];

export const LIMITATIONS_DATA = [
  {
    title: "Smooth Surface False Positives",
    icon: "AlertTriangle",
    description:
      "Dry airport runways, smooth asphalt highways, and dry salt flats reflect radar energy away like calm water, occasionally triggering false positive flood detections.",
  },
  {
    title: "Vegetation Canopy & Double-Bounce",
    icon: "Trees",
    description:
      "Sub-canopy floodwaters in dense forests cause radar double-bounce backscattering between water surfaces and vertical trunks, appearing bright and causing false negatives.",
  },
  {
    title: "Invalid / Cloud Masking in Labels",
    icon: "CloudOff",
    description:
      "Reference ground-truth masks contain -1 invalid labels from optical cloud cover and sensor borders. They are dynamically excluded during loss computation and evaluation.",
  },
  {
    title: "Historical Water Baseline (JRC)",
    icon: "Database",
    description:
      "Sen1Floods11 does NOT include separate pre-flood SAR images. The JRC 30-year Global Surface Water permanence layer is used as the historical reference baseline.",
  },
  {
    title: "WGS84 Nominal Area Scaling",
    icon: "Globe",
    description:
      "Geospatial rasters are in WGS84 (EPSG:4326). Ground resolution varies with cos(latitude). Stated km² values are documented nominal approximations at 100 m²/pixel.",
  },
  {
    title: "Academic Prototype Scope",
    icon: "GraduationCap",
    description:
      "This system is designed as an academic research prototype for rapid visual assessment and benchmark evaluation, not an operational emergency command system.",
  },
];

export const TECH_STACK = [
  { name: "Python 3.11", category: "Core Language", desc: "Scientific backend & ML execution" },
  { name: "PyTorch 2.14", category: "Deep Learning", desc: "U-Net architecture & autograd tensors" },
  { name: "Rasterio / GDAL", category: "Geospatial I/O", desc: "Multi-band GeoTIFF reading & CRS handling" },
  { name: "NumPy & Pandas", category: "Data Science", desc: "Array operations & split auditing" },
  { name: "OpenCV & Matplotlib", category: "Computer Vision", desc: "Diagnostic figure rendering & colormaps" },
  { name: "Streamlit 1.64", category: "Interactive App", desc: "Inference dashboard & GeoTIFF upload" },
  { name: "Next.js 16", category: "Web Framework", desc: "Modern React SSR & research presentation" },
  { name: "TypeScript 5", category: "Type Safety", desc: "Strict data typing & component contracts" },
  { name: "Tailwind CSS 4", category: "Styling", desc: "Dark research aesthetic & responsive layouts" },
];
