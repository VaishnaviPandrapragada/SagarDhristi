/* ==========================================================================
   SIMULATED DEMONSTRATION DATA
   Every value below is synthetic. Vessel identities are fictional and are
   used only to demonstrate the interface. Nothing here asserts that any real
   vessel caused any real discharge.
   ========================================================================== */

export const COLORS = {
  bg: "#031018",
  navy: "#061D2A",
  navy2: "#0A2A3D",
  ocean: "#07527A",
  baby: "#8DDCF7",
  cyan: "#35C9F5",
  white: "#F5FAFC",
  oil: "#D99A3D",
  warning: "#F5B942",
  critical: "#FF5B5B",
};

export const CASE = {
  id: "CASE 2026-0417",
  status: "Investigation active",
  acquired: "27 Aug 2026 · 06:52 UTC",
  aoi: "22.4°N, 69.1°E",
  aoiName: "Gulf of Kutch approaches",
  confidence: 0.87,
  area: 12.5,
  age: "~12 hours",
  vesselsScreened: 14,
  candidates: 3,
};

/* --- 01 SAR image ------------------------------------------------------- */
export const SAR = {
  mission: "Sentinel-1",
  sensor: "C-band SAR",
  mode: "IW · GRD",
  pass: "Descending",
  polarisations: ["VV", "VH"],
  resolution: "10 m/px",
  swath: "250 km",
  notes: [
    "SAR sees through cloud and works at night, so a pass is usable regardless of weather or daylight.",
    "Oil damps capillary waves, so a slick returns less energy and appears as a dark patch against rougher sea.",
    "Dark patches are not automatically oil — low wind, algal mats and ship wakes look similar, which is why the later stages exist.",
  ],
};

/* --- 02 Preprocessing --------------------------------------------------- */
export const PREPROCESS = [
  { key: "calibration", name: "Calibration", detail: "Digital numbers converted to calibrated backscatter (σ⁰) so values are physically comparable between scenes.", ms: 820 },
  { key: "speckle", name: "Speckle filtering", detail: "Refined Lee filter suppresses multiplicative noise while preserving slick edges.", ms: 1440 },
  { key: "geometric", name: "Geometric correction", detail: "Terrain-corrected to WGS-84 so every pixel carries a real-world coordinate.", ms: 2110 },
  { key: "landmask", name: "Land masking", detail: "Coastline vector masks land, harbours and intertidal flats out of the analysis window.", ms: 640 },
  { key: "normalise", name: "Normalization", detail: "Backscatter rescaled to a fixed range so the vision models receive consistent input.", ms: 380 },
];

/* --- 03 Vision model layer ---------------------------------------------- */
export const VISION_MODELS = [
  {
    key: "unet",
    name: "U-Net",
    role: "Pixel-level segmentation",
    confidence: 0.91,
    strength: "Sharp boundaries on compact, well-defined slicks",
    weakness: "Under-segments thin trailing sheen",
    area: 12.1,
  },
  {
    key: "deeplab",
    name: "DeepLabV3+",
    role: "Multi-scale semantic segmentation",
    confidence: 0.89,
    strength: "Atrous convolutions catch both thick pools and faint sheen",
    weakness: "Occasionally merges nearby low-wind patches",
    area: 13.4,
  },
  {
    key: "transunet",
    name: "TransUNet",
    role: "Transformer-augmented segmentation",
    confidence: 0.86,
    strength: "Global attention keeps elongated, broken slicks connected",
    weakness: "Higher inference cost, softer edges",
    area: 12.8,
  },
];

export const ORCHESTRATOR = {
  agreement: 0.93,
  iou: 0.88,
  verdict: "Spill detected",
  confidence: 0.87,
  rule: "Majority vote on the pixel masks, weighted by each model's validation IoU. Agreement below 0.60 would end the pipeline here with no detection.",
  decisions: [
    { q: "Is there an oil spill?", a: "Yes — all three masks overlap at IoU 0.88" },
    { q: "How confident are we?", a: "0.87 combined confidence" },
    { q: "What happens next?", a: "Proceed to characterization" },
  ],
};

/* --- 05 Characterization ------------------------------------------------ */
export const SPILL = {
  location: "22.4°N, 69.1°E",
  area: 12.5,
  perimeter: 21.4,
  length: 8.6,
  width: 2.7,
  aspect: 3.19,
  shape: "Irregular",
  age: "~12 hours",
  confidence: 0.87,
  descriptors: [
    { label: "Irregularity", value: 0.62, note: "Boundary departs from a smooth ellipse — consistent with a weathering slick rather than a fresh point release." },
    { label: "Elongation", value: 0.81, note: "Strong stretching along the surface current vector." },
    { label: "Compactness", value: 0.44, note: "Low compactness, typical of wind-sheared surface oil." },
  ],
};

/* --- 06 Ocean & met data ------------------------------------------------ */
export const ENVIRONMENT = {
  source: "Copernicus Marine · ECMWF ERA5",
  wind: { speed: 14, unit: "kn", dir: "NE", bearing: 45 },
  current: { speed: 0.8, unit: "kn", dir: "E", bearing: 90 },
  wave: { height: 1.2, unit: "m", period: "6.4 s" },
  sst: { value: 28.4, unit: "°C" },
  windSeries: [9, 11, 12, 14, 15, 14, 13, 14],
  currentSeries: [0.5, 0.6, 0.7, 0.8, 0.8, 0.9, 0.8, 0.8],
  hours: ["00", "01", "02", "03", "04", "05", "06", "07"],
};

/* --- 07 Drift ----------------------------------------------------------- */
export const DRIFT = {
  originWindow: "27 Aug · 02:50 – 04:30 UTC",
  originZone: "22.48°N, 68.93°E ± 1.1 NM",
  detection: "27 Aug · 06:52 UTC",
  forecastHorizon: "+18 h",
  hindcastConfidence: "High",
  uncertainty: "±1.1 NM",
  method: "Lagrangian particle ensemble, 2 000 particles, 3 % windage",
  spreadNote: "The result is a zone and a time window, not a point — environmental modelling carries real uncertainty and the interface should show it.",
};

/* --- 08 Source type ----------------------------------------------------- */
export const SOURCE_TYPES = [
  { key: "vessel", name: "Vessel", desc: "Ship or tanker under way", score: 0.79, evidence: "Long, narrow slick aligned with a shipping lane — the classic signature of a discharge from a moving hull." },
  { key: "fixed", name: "Fixed structure", desc: "Rig, platform or pipeline", score: 0.14, evidence: "No installation within 40 NM of the origin zone in the infrastructure register." },
  { key: "unknown", name: "Unknown / natural", desc: "Seep, algal mat or look-alike", score: 0.07, evidence: "No recorded seep in this basin; backscatter contrast is too strong for an algal look-alike." },
];

/* --- 09 Space-time filter ----------------------------------------------- */
export const FILTER_FUNNEL = [
  { label: "AIS records in scene", count: 1482, note: "Raw position reports in the 6-hour buffer" },
  { label: "Unique vessels", count: 14, note: "Deduplicated by MMSI" },
  { label: "Inside source zone", count: 7, note: "Within 12 NM of the hindcast origin" },
  { label: "Inside time window", count: 5, note: "Present during 02:50 – 04:30 UTC" },
  { label: "Candidate vessels", count: 3, note: "Passing both space and time tests" },
];

/* --- Vessels ------------------------------------------------------------ */
export const VESSELS = [
  {
    rank: 1, name: "MV Kestrel", type: "Bulk carrier", mmsi: "123456789", imo: "9284710",
    flag: "Demo registry", length: 189, tier: "candidate",
    distance: 0.4, timeOffset: -22, speed: 8.4, heading: 118, aisGap: "12 min",
    spatial: 0.92, temporal: 0.89, trajectory: 0.81, proximity: 0.86, behaviour: 0.78, continuity: 0.64,
    score: 0.82,
    track: [[18, 74], [29, 66], [41, 58], [52, 50], [61, 46], [72, 41], [84, 36]],
    rnn: { match: 0.81, note: "Predicted track from 12×7 AIS features stays inside the origin zone for 34 minutes." },
    anomaly: "Speed drops from 12.6 kn to 8.4 kn for 26 minutes inside the origin window, then recovers.",
  },
  {
    rank: 2, name: "MT Sea Orchid", type: "Chemical tanker", mmsi: "987654321", imo: "9351102",
    flag: "Demo registry", length: 144, tier: "candidate",
    distance: 2.1, timeOffset: -58, speed: 11.2, heading: 244, aisGap: "0 min",
    spatial: 0.71, temporal: 0.58, trajectory: 0.63, proximity: 0.55, behaviour: 0.47, continuity: 0.94,
    score: 0.56,
    track: [[88, 22], [76, 32], [62, 42], [48, 52], [38, 58], [27, 66], [16, 73]],
    rnn: { match: 0.63, note: "Predicted track clips the western edge of the origin zone but exits before the window opens." },
    anomaly: "Course change of 18° near the zone boundary; consistent with routine traffic separation.",
  },
  {
    rank: 3, name: "MV Devi Priya", type: "General cargo", mmsi: "111222333", imo: "9412093",
    flag: "Demo registry", length: 121, tier: "candidate",
    distance: 4.8, timeOffset: -140, speed: 9.7, heading: 302, aisGap: "0 min",
    spatial: 0.44, temporal: 0.27, trajectory: 0.31, proximity: 0.36, behaviour: 0.22, continuity: 0.97,
    score: 0.34,
    track: [[92, 58], [86, 50], [80, 42], [76, 34], [74, 27], [70, 19], [66, 12]],
    rnn: { match: 0.31, note: "Predicted track remains north of the origin zone throughout the window." },
    anomaly: "No irregularities detected in speed or heading.",
  },
  {
    rank: 4, name: "MT Navigator Star", type: "Product tanker", mmsi: "419664521", imo: "9198845",
    flag: "Demo registry", length: 176, tier: "screened",
    distance: 6.2, timeOffset: 84, speed: 12.9, heading: 78, aisGap: "0 min",
    spatial: 0.31, temporal: 0.12, trajectory: 0.24, proximity: 0.28, behaviour: 0.18, continuity: 0.99,
    score: 0.19,
    track: [[8, 82], [14, 76], [19, 72], [22, 70], [28, 64], [35, 58], [43, 51]],
    rnn: { match: 0.24, note: "Enters the zone after detection time; cannot precede the slick." },
    anomaly: "None.",
  },
  {
    rank: 5, name: "MV Blue Horizon", type: "Container", mmsi: "419773098", imo: "9331177",
    flag: "Demo registry", length: 228, tier: "screened",
    distance: 8.9, timeOffset: -206, speed: 14.1, heading: 190, aisGap: "0 min",
    spatial: 0.18, temporal: 0.09, trajectory: 0.12, proximity: 0.15, behaviour: 0.09, continuity: 0.98,
    score: 0.11,
    track: [[94, 12], [92, 24], [90, 38], [88, 50], [84, 63], [80, 74], [76, 84]],
    rnn: { match: 0.12, note: "Transits well east of the origin zone." },
    anomaly: "None.",
  },
  {
    rank: 6, name: "MT Gulf Pioneer", type: "Crude tanker", mmsi: "419228841", imo: "9276630",
    flag: "Demo registry", length: 243, tier: "screened",
    distance: 11.4, timeOffset: 172, speed: 10.3, heading: 15, aisGap: "0 min",
    spatial: 0.12, temporal: 0.06, trajectory: 0.08, proximity: 0.11, behaviour: 0.06, continuity: 0.99,
    score: 0.07,
    track: [[6, 46], [8, 40], [11, 33], [13, 26], [15, 20], [18, 13], [21, 7]],
    rnn: { match: 0.08, note: "Northbound and outside the window entirely." },
    anomaly: "None.",
  },
];

export const VESSEL_POSITIONS = VESSELS.map((v) => ({
  mmsi: v.mmsi,
  x: v.track[4][0],
  y: v.track[4][1],
}));

/* --- 11 Evidence fusion ------------------------------------------------- */
export const EVIDENCE_FACTORS = [
  { key: "spatial", label: "Spatial consistency", weight: 0.25, question: "Was it in the right place?" },
  { key: "temporal", label: "Temporal consistency", weight: 0.25, question: "Was it there at the right time?" },
  { key: "trajectory", label: "Trajectory consistency", weight: 0.20, question: "Does its movement match the slick?" },
  { key: "proximity", label: "Proximity", weight: 0.15, question: "How close to the origin zone?" },
  { key: "behaviour", label: "Behaviour / AIS pattern", weight: 0.15, question: "Any unusual stops, slowdowns or gaps?" },
];

/* --- 13 Result ---------------------------------------------------------- */
export const RESULT = {
  topCandidate: VESSELS[0],
  sourceZone: "22.48°N, 68.93°E ± 1.1 NM",
  sourceWindow: "27 Aug 2026 · 02:50 – 04:30 UTC",
  confidence: "High",
  statement:
    "Strong spatio-temporal correlation between the reconstructed source zone and the AIS track of MV Kestrel.",
};

/* --- 14 API ------------------------------------------------------------- */
export const API_ENDPOINTS = [
  { method: "POST", path: "/v1/scenes", desc: "Upload a Sentinel-1 scene and open a case", time: "12 ms" },
  { method: "GET", path: "/v1/cases/{id}/detection", desc: "Orchestrated detection mask and confidence", time: "38 ms" },
  { method: "GET", path: "/v1/cases/{id}/drift", desc: "Hindcast source zone and forecast slick path", time: "64 ms" },
  { method: "GET", path: "/v1/cases/{id}/candidates", desc: "Ranked candidate vessels with evidence breakdown", time: "51 ms" },
  { method: "GET", path: "/v1/cases/{id}/report", desc: "Full investigation record as JSON or PDF", time: "140 ms" },
];

export const API_SAMPLE = `{
  "case_id": "2026-0417",
  "detection": { "spill": true, "confidence": 0.87 },
  "spill": { "area_km2": 12.5, "shape": "irregular", "age_h": 12 },
  "source_zone": {
    "centre": [22.48, 68.93],
    "radius_nm": 1.1,
    "window_utc": ["2026-08-27T02:50Z", "2026-08-27T04:30Z"]
  },
  "candidates": [
    { "mmsi": "123456789", "score": 0.82, "status": "potential_source" },
    { "mmsi": "987654321", "score": 0.56, "status": "candidate" },
    { "mmsi": "111222333", "score": 0.34, "status": "candidate" }
  ],
  "disclaimer": "Correlation score. Not a confirmed attribution."
}`;
