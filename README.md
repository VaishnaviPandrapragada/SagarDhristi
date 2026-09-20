<div align="center">

# SAGAR DHRISTI

### Satellite-based Oil Spill Detection, Source Tracing & AIS Correlation

**SIH26143 · NTRO · Smart India Hackathon 2026**

<br>

<a href="https://sagardhristi-dts3.onrender.com/">
  <img src="https://img.shields.io/badge/LIVE%20DEMO-0B5CAD?style=for-the-badge" />
</a>
&nbsp;

<br><br>

<b>DETECT&nbsp;&nbsp;→&nbsp;&nbsp;TRACE&nbsp;&nbsp;→&nbsp;&nbsp;CORRELATE&nbsp;&nbsp;→&nbsp;&nbsp;RANK</b>

</div>

---

## Overview

Sagar Dhristi is a geospatial intelligence system for oil-spill investigation.

It combines **Sentinel-1 SAR imagery**, environmental data and historical **Automatic Identification System (AIS)** records to connect four stages of analysis:

| Stage | Purpose |
|---|---|
| **Detect** | Identify possible oil-spill regions from SAR imagery |
| **Trace** | Estimate the probable source region using wind and ocean currents |
| **Correlate** | Identify vessels present in the relevant space-time window |
| **Rank** | Combine available evidence to produce candidate-vessel rankings |

The system is intended to support investigation and decision-making. A candidate ranking does **not** establish legal liability or declare a vessel responsible.

**Live system:**  
https://sagardhristi-dts3.onrender.com/

---

## The Problem

An oil slick observed at sea may not correspond to the location where the oil was originally released.

Investigation therefore requires the combination of:

- Satellite imagery
- Ocean-current and wind information
- Historical AIS records
- Geospatial analysis
- Vessel trajectory information

These datasets are normally analysed as separate sources.

**Sagar Dhristi connects them into a single investigation workflow.**

---

## Investigation Workflow


 Sentinel-1 SAR
       │
       ▼
 Image Preprocessing
       │
       ▼
 AI Spill Segmentation
 U-Net / DeepLabV3+ / TransUNet
       │
       ▼
 Spill Characterization
 Area · Shape · Location
       │
       ▼
 Wind + Ocean Currents
       │
       ▼
 Backward Drift Analysis
       │
       ▼
 Probable Source Zone
 + Source Time Window
       │
       ▼
 AIS Space-Time Filtering
       │
       ▼
 Vessel Trajectory Analysis
       │
       ▼
 Evidence Fusion
       │
       ▼
 Candidate Vessel Ranking
       │
       ▼
 Investigation Dashboard

## System Architecture

Sagar Dhristi follows a modular investigation pipeline that connects
satellite imagery, environmental data and AIS vessel data.

┌─────────────────────┐
│   Sentinel-1 SAR    │
│   Satellite Image   │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│    Preprocessing    │
│  Noise / Normalise  │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   AI Segmentation   │
│ U-Net / DeepLabV3+  │
│     / TransUNet     │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Spill Characterize  │
│ Area • Shape • GPS  │
└──────────┬──────────┘
           ↓
     ┌─────┴─────┐
     ↓           ↓
┌───────────┐ ┌───────────────┐
│ Wind +    │ │ Source-Type   │
│ Currents  │ │ Classification│
└─────┬─────┘ └───────┬───────┘
      ↓               ↓
┌─────────────────────────────┐
│   Backward Drift Analysis   │
│ Probable Source Zone + Time │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│     AIS Space-Time Filter   │
│ Location + Time + Movement  │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ Trajectory & Behaviour      │
│ Analysis                    │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│      Evidence Fusion        │
│ Spatial • Temporal •        │
│ Trajectory • Behavioural    │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ Candidate Vessel Ranking    │
│ Explainable Evidence Score  │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│       FastAPI Backend       │
│       React Dashboard       │
└─────────────────────────────┘

## Investigation Workflow

The investigation is performed in four major stages:

| Stage | Process | Output |
|---|---|---|
| **01 — Detect** | Sentinel-1 SAR + AI segmentation | Spill mask |
| **02 — Trace** | Wind/current data + backward drift | Probable source zone |
| **03 — Correlate** | AIS + spatial-temporal filtering | Candidate vessels |
| **04 — Rank** | Evidence fusion + trajectory analysis | Ranked candidates |

### Detect

The system processes Sentinel-1 SAR imagery and uses segmentation
models to identify regions that may correspond to oil spills.

### Trace

The detected spill is characterized using its geometry and location.
Environmental conditions are then used to estimate how the slick could
have moved and derive a probable source zone and time window.

### Correlate

Historical AIS data is filtered using the estimated source region
and time window. Vessels that could not have been present in the
relevant space-time window are removed from further analysis.

### Rank

Remaining candidates are evaluated using multiple evidence factors,
including spatial proximity, temporal alignment, trajectory consistency
and behavioural patterns.

## Core Modules

### 5.1 Oil Spill Detection

Input:
- Sentinel-1 SAR imagery

Models:
- U-Net
- DeepLabV3+
- TransUNet

Output:
- Binary spill segmentation mask
- Spill confidence
- Detected spill region

### 5.2 Spill Characterization

The segmentation mask is converted into measurable geometric features.

| Feature | Description |
|---|---|
| Area | Size of detected spill region |
| Centroid | Geometric centre of the spill |
| Bounding Box | Spatial extent |
| Perimeter | Boundary length |
| Aspect Ratio | Shape elongation |
| Compactness | Shape characteristics |

### 5.3 Probable Source Estimation

A detected spill does not necessarily indicate the location where
the oil was released.

Sagar Dhristi therefore uses:

**Spill Location → Environmental Data → Backward Drift → Source Zone**

The output is represented as a probable source region and time window
rather than an exact release coordinate.

### 5.4 AIS Correlation

AIS records are filtered using:

- Vessel position
- Timestamp
- Distance from source zone
- Time difference
- Vessel trajectory
- Course and speed
- Source-zone overlap

This produces a smaller set of realistic candidate vessels.

### 5.5 Evidence Fusion

Each candidate is evaluated using multiple independent signals.

| Evidence | Meaning |
|---|---|
| Spatial | Was the vessel near the source zone? |
| Temporal | Was it present during the relevant time? |
| Trajectory | Does its movement connect with the source zone? |
| Behavioural | Are there unusual movement patterns? |

The final output is an **evidence score**, not a declaration of
responsibility.

## Technology Stack

| Layer | Technologies |
|---|---|
| Satellite Data | Sentinel-1 SAR |
| AI / ML | U-Net, DeepLabV3+, TransUNet |
| Environmental Data | Ocean Currents, Wind |
| Vessel Data | Historical AIS |
| Geospatial | Rasterio, GeoPandas, OpenCV |
| Backend | Python, FastAPI |
| Frontend | React |
| Data Processing | NumPy, Pandas |

## Dataset & Data Sources

### Satellite Imagery

- Sentinel-1 SAR oil-spill imagery
- Oil-spill segmentation masks
- Look-alike and no-oil samples

### AIS

Historical AIS records containing vessel position,
timestamp and movement information.

### Environmental Data

- Ocean current information
- Wind information

These datasets are combined only when their spatial and temporal
coverage is compatible with the investigation case.

## Model Evaluation

The segmentation stage supports comparison between multiple
architectures rather than relying on a single model.

| Model | Role |
|---|---|
| U-Net | Baseline segmentation |
| DeepLabV3+ | Multi-scale semantic segmentation |
| TransUNet | CNN + Transformer-based segmentation |

Evaluation metrics include:

- IoU
- Dice / F1 Score
- Precision
- Recall
- Accuracy

## API

The backend exposes the analysis pipeline through a FastAPI service.

### Analysis Endpoint

`POST /api/analyze`

The endpoint accepts an input image and returns the processed
spill-analysis output.

### Pipeline

Image
  ↓
Preprocessing
  ↓
Segmentation
  ↓
Spill Characterization
  ↓
Source Estimation
  ↓
AIS Correlation
  ↓
Evidence Ranking
  ↓
JSON Response

{
  "spill_detected": true,
  "confidence": 0.91,
  "source_zone": {
    "latitude": 13.4256,
    "longitude": 144.6821
  },
  "candidate_vessels": [
    {
      "vessel_id": "XXXXXXXXX",
      "evidence_score": 86
    }
  ]
}


---

# 10. DASHBOARD

Then show screenshots.

## Dashboard

The React dashboard presents the investigation results in a single
interface.

### Dashboard View

![Dashboard](docs/assets/dashboard.png)

### Key Outputs

- Detected spill region
- Spill geometry
- Probable source zone
- Source time window
- AIS candidate vessels
- Evidence scores
- Vessel trajectory information

## Results

The current prototype demonstrates the complete investigation flow:

**SAR Image → Spill Detection → Source Estimation → AIS Filtering → Candidate Ranking**

The system is designed to preserve uncertainty throughout the pipeline
rather than treating individual model outputs as definitive conclusions.

## Limitations

- SAR imagery can contain oil-like look-alikes.
- Environmental conditions introduce uncertainty into drift estimation.
- AIS coverage can contain missing or irregular observations.
- Satellite revisit timing limits temporal resolution.
- Source attribution depends on the quality and alignment of multiple datasets.
- The current prototype requires further validation across different
  geographic regions and real-world spill cases.

## Responsible Use

Sagar Dhristi is designed as a decision-support and investigation
tool.

A candidate vessel ranking represents evidence consistency within
the available data. It does not establish legal responsibility,
intent or guilt.

Final investigation and enforcement decisions require validation
using authoritative records and independent evidence.

## Future Scope

- Lagrangian particle-based drift modelling
- Improved uncertainty estimation
- Larger regional AIS datasets
- Additional SAR and optical satellite sources
- Improved vessel trajectory modelling
- Fixed-source detection for platforms and pipelines
- Automated case report generation
- Regional model adaptation

## Team

**Team Sagar Dhristi**

| Member | Role |
|---|---|
| P. Vaishnavi | Data, Research & System Integration |
| Keertana | AI / ML & Backend |
| Tanvi Gupta | Frontend & Data |
| Naman Kumar Sahoo | AI / ML & Trajectory Analysis |
| Jagat Dubey | Business & Strategy |
| Nikil | Business & Strategy |

## SIH 2026

**Problem Statement:** SIH26143  
**Organization:** NTRO  
**Theme:** Disaster Management
**Category:** Software

## References

<details>
<summary>View references</summary>

1. Sentinel-1 SAR documentation
2. Oil-spill segmentation research
3. AIS-based vessel tracking research
4. Oil-spill source-tracing research
5. Environmental drift-modelling research
6. SIH26143 Problem Statement
7. Dataset documentation

</details>

