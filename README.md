SAGAR DHRISTI
Satellite-based Oil Spill Detection, Source Tracing and AIS Correlation

SIH26143 · NTRO · Smart India Hackathon 2026

Sagar Dhristi is a geospatial intelligence system that combines Sentinel-1 SAR imagery, environmental data and historical AIS records to support oil-spill investigation.

The system follows a four-stage workflow:

DETECT → TRACE → CORRELATE → RANK

It detects possible oil spills from satellite imagery, estimates a probable source region using wind and ocean-current data, correlates the source window with historical vessel movements, and produces an evidence-based ranking of candidate vessels.

The system supports investigation and decision-making. It does not establish legal liability or declare a vessel guilty.
Live link : https://sagardhristi-dts3.onrender.com/

01 — OVERVIEW

An oil slick observed at sea may not correspond to the location where the oil was originally released.

Investigating an incident therefore requires multiple sources of information:

Satellite imagery for detecting possible spills
Environmental data for understanding spill movement
AIS data for reconstructing vessel movement
Geospatial analysis for connecting the different datasets
Evidence fusion for comparing potential candidate vessels

Sagar Dhristi brings these components into a single investigation workflow.

02 — INVESTIGATION WORKFLOW
                    SENTINEL-1 SAR
                          |
                          v
                  IMAGE PREPROCESSING
                          |
                          v
                 AI SPILL SEGMENTATION
                U-Net / DeepLabV3+
                    / TransUNet
                          |
                          v
                 SPILL CHARACTERIZATION
                Area / Shape / Location
                          |
                          v
             WIND + OCEAN CURRENT DATA
                          |
                          v
                  BACKWARD DRIFT MODEL
                          |
                          v
                PROBABLE SOURCE ZONE
                   + TIME WINDOW
                          |
                          v
                AIS SPACE-TIME FILTER
                          |
                          v
             TRAJECTORY & BEHAVIOUR
                   ANALYSIS
                          |
                          v
                   EVIDENCE FUSION
                          |
                          v
                CANDIDATE RANKING
                          |
                          v
                 INVESTIGATION VIEW
03 — SYSTEM ARCHITECTURE

Sagar Dhristi is organised as a sequence of modular processing stages.

Stage	Input	Processing	Output
Satellite ingestion	Sentinel-1 SAR	Preprocessing	Prepared SAR image
Spill detection	SAR image	AI segmentation	Spill mask
Characterization	Spill mask	Geospatial analysis	Area, centroid, geometry
Source estimation	Spill + environmental data	Backward drift	Probable source zone
Vessel filtering	Source zone + AIS	Spatio-temporal filtering	Candidate vessels
Trajectory analysis	AIS tracks	Movement analysis	Trajectory features
Evidence fusion	Combined evidence	Candidate scoring	Ranked candidates
Visualization	Analysis results	React dashboard	Investigation interface
04 — SAR SPILL DETECTION

The first stage identifies possible oil-spill regions from Sentinel-1 Synthetic Aperture Radar imagery.

SAR is suitable for maritime monitoring because it can acquire imagery independent of daylight and is capable of operating through cloud cover.

Models explored
U-Net
DeepLabV3+
TransUNet

The segmentation stage produces a binary mask:

0 → Background
1 → Possible oil spill

The resulting mask is passed to the characterization stage.

Evaluation metrics
Intersection over Union (IoU)
Dice / F1 Score
Precision
Recall
Accuracy

Model results are evaluated according to the dataset and experimental split used.

05 — SPILL CHARACTERIZATION

After segmentation, the detected region is converted into measurable spatial features.

The characterization stage extracts:

Spill presence
Pixel area
Largest connected component
Centroid
Bounding box
Perimeter
Aspect ratio
Compactness

Example:

{
  "spill_detected": true,
  "confidence": 0.914,
  "spill": {
    "area_pixels": 17450,
    "centroid": {
      "latitude": 13.4256,
      "longitude": 144.6821
    },
    "bounding_box": {
      "width": 250,
      "height": 220
    },
    "aspect_ratio": 1.136,
    "perimeter": 912.4,
    "compactness": 0.264
  }
}

For georeferenced satellite imagery, geographic coordinates can be derived from the raster transform.

06 — PROBABLE SOURCE ESTIMATION

The observed spill location is not necessarily the release location.

Sagar Dhristi uses environmental information to estimate how the slick could have moved.

Environmental inputs
Wind
Ocean currents
Spill location
Estimated elapsed time
Processing
Observed Spill
      |
      v
Environmental Conditions
      |
      v
Backward Drift
      |
      v
Possible Trajectories
      |
      v
Source Density / Probability Region
      |
      v
Probable Source Zone
+
Source Time Window

The system reports a probable source zone rather than presenting a single release coordinate as certain.

07 — AIS CORRELATION

Historical Automatic Identification System (AIS) data is used to reconstruct vessel movement around the estimated source region.

The system does not simply select the nearest vessel.

Vessels are filtered using both spatial and temporal constraints.

Space-Time Filtering
Historical AIS
      |
      v
Location Filter
      |
      v
Source Time Window
      |
      v
Trajectory Filter
      |
      v
Candidate Vessels

Relevant AIS features include:

MMSI
Timestamp
Latitude
Longitude
Speed over ground
Course over ground
Heading
Vessel type
Time gap
Distance travelled
Distance from source zone
Course changes
Time difference from estimated spill event
08 — TRAJECTORY AND BEHAVIOUR ANALYSIS

Candidate vessels can be represented as time-ordered trajectories.

Possible trajectory features include:

Position sequence
Speed variation
Course variation
Direction changes
Distance from probable source zone
Time spent near the source region
Movement continuity

An RNN/LSTM-based approach can be explored for vessel movement modelling where sufficient sequential training data is available.

The environmental drift model and vessel trajectory model serve different purposes:

Oil movement      → Environmental / drift model

Vessel movement   → AIS trajectory analysis
09 — EVIDENCE FUSION

Multiple pieces of evidence are combined before generating the final candidate ranking.

Evidence	Purpose
Spatial proximity	Was the vessel near the probable source zone?
Temporal proximity	Was it present during the relevant time window?
Trajectory compatibility	Does its movement connect with the source region?
Behavioural evidence	Does its movement contain relevant anomalies?
Source compatibility	Is a vessel a plausible source type?
Data confidence	How reliable is the available evidence?

The prototype evidence score represents agreement among available evidence sources.

Evidence score is not probability of guilt.

10 — SOURCE-TYPE CLASSIFICATION

The system does not assume that every oil spill originates from a vessel.

                  SOURCE TYPE
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
       VESSEL       FIXED       UNKNOWN
                    SOURCE

Potential fixed sources may include:

Offshore platforms
Pipelines
Maritime infrastructure

AIS-based vessel ranking is used when a vessel is a valid candidate.

If evidence does not support a strong vessel association, the system retains an uncertain result rather than forcing a vessel attribution.

11 — HANDLING UNCERTAINTY

Real-world maritime datasets contain uncertainty at several stages.

SAR uncertainty

Dark regions in SAR imagery can have multiple causes and are not automatically oil.

Approach: Multi-model segmentation and confidence-aware analysis.

Source uncertainty

The observed slick may have moved from its release location.

Approach: Backward drift modelling and source-zone estimation.

Environmental uncertainty

Wind and current conditions vary spatially and temporally.

Approach: Multiple scenarios and uncertainty-aware source regions.

AIS uncertainty

AIS records may contain gaps, noise or incomplete information.

Approach: Confidence-aware analysis and multi-factor evidence.

Vessel-density uncertainty

Several vessels may be present around the source region.

Approach: Space-time filtering followed by evidence-based ranking.

12 — CHALLENGES AND STRATEGIES
Challenge	Strategy
SAR look-alikes	Multi-model segmentation
Source-location uncertainty	Backward drift modelling
Environmental variability	Uncertainty-aware analysis
AIS data gaps	Space-time filtering
High vessel density	Evidence-based ranking
Non-vessel sources	Source-type classification
Limited training data	Data validation and augmentation

13 — TECHNOLOGY STACK

Data

Sentinel-1 SAR · Historical AIS · Wind Data · Ocean Current Data

Machine Learning

Python · U-Net · DeepLabV3+ · TransUNet

Geospatial Processing

Rasterio · GeoPandas · OpenCV · NumPy

Backend

FastAPI

Frontend

React

Development

Git · GitHub · Jupyter · Python


14 — API

The backend exposes the analysis pipeline through FastAPI.

Analysis Pipeline
SAR Image
    ↓
Preprocessing
    ↓
Segmentation
    ↓
Characterization
    ↓
Source Estimation
    ↓
AIS Correlation
    ↓
Evidence Fusion
Example Endpoint
POST /api/analyze
Example Output
{
  "spill_detected": true,
  "confidence": 0.914,
  "source_zone": {
    "latitude": 13.42,
    "longitude": 144.68
  },
  "candidate_vessels": [
    {
      "vessel_id": "MMSI_XXXX",
      "evidence_score": 0.86
    }
  ]
}

15 — DASHBOARD

The interface follows the investigation workflow:

SAR IMAGE
    ↓
SPILL DETECTION
    ↓
SPILL CHARACTERIZATION
    ↓
SOURCE ZONE
    ↓
AIS VESSELS
    ↓
EVIDENCE ANALYSIS
    ↓
CANDIDATE RANKING

The dashboard presents the detected spill, source estimation, relevant vessel traffic and supporting evidence in a single interface.

16 — CASE WALKTHROUGH

A typical investigation follows these stages:

CASE INPUT
Sentinel-1 SAR image
        ↓
SPILL DETECTION
Possible spill region
        ↓
CHARACTERIZATION
Area / geometry / centroid
        ↓
SOURCE ESTIMATION
Wind + ocean currents
        ↓
SOURCE ZONE
Probable region + time window
        ↓
AIS CORRELATION
Historical vessel traffic
        ↓
SPACE-TIME FILTER
Relevant vessels retained
        ↓
EVIDENCE ANALYSIS
Trajectory + proximity + timing
        ↓
FINAL OUTPUT
Ranked candidate vessels

17 — MODEL EVALUATION

The segmentation models are evaluated using standard classification and segmentation metrics.

Model	Dataset	Split	IoU	Dice / F1	Precision	Recall
U-Net	—	—	—	—	—	—
DeepLabV3+	—	—	—	—	—	—
TransUNet	—	—	—	—	—	—

Model performance depends on the dataset, geographical region, preprocessing and evaluation split.

Published research benchmarks are kept separate from the team's own experimental results.

18 — DATASETS
Sentinel-1 SAR Oil Spill Dataset

The project uses publicly available Sentinel-1 SAR oil-spill datasets for model development and evaluation.

Primary sources include:

Sentinel-1 SAR Oil Spill Dataset — Part I
Sentinel-1 SAR Oil Spill Dataset — Part II
Sentinel-1 SAR Oil Spill Dataset — Part III
CSIRO Sentinel-1 SAR Oil/Non-Oil Dataset
Additional development datasets where applicable
AIS

Historical AIS data is used for vessel movement analysis.

Environmental Data

Wind and ocean-current information is used for drift analysis and probable source estimation.

Detailed dataset information, preprocessing and licensing are documented in docs/datasets.md.

19 — RESEARCH BASIS

The project is informed by research in:

SAR remote sensing
Oil-spill segmentation
Deep learning
Marine pollution modelling
Backward drift modelling
Lagrangian trajectory analysis
AIS vessel analytics
Geospatial intelligence
Maritime surveillance
Selected Research
Longépé et al. (2015) — SAR imagery, AIS and forward drift modelling.
El Mohtar et al. (2021) — Bayesian oil-spill source identification.
Luo et al. (2024) — Multi-source ship tracing from oil spills.
Zakzouk et al. (2025) — Deep learning and SAR-based oil-spill detection.
Dong et al. (2023) — Deep learning for low-quality SAR oil-spill detection.

The complete reference list is available in docs/references.md.

20 — LIMITATIONS

Sagar Dhristi is currently a research and prototype system.

Important limitations include:

SAR detections can contain oil-spill look-alikes.
Environmental conditions introduce uncertainty into drift modelling.
The observed slick location may differ from the release location.
AIS data may contain gaps or inaccuracies.
High vessel density can produce multiple plausible candidates.
Model performance can vary across geographical regions.
Training data may not represent every maritime environment.
Vessel association cannot be established from satellite and AIS evidence alone.

21 — RESPONSIBLE USE

Sagar Dhristi is designed as a decision-support and investigation-assistance system.

It should not be used to:

Automatically declare a vessel guilty
Establish legal liability
Treat a model score as proof
Treat missing AIS as proof of absence
Replace human investigation
Present an uncertain source location as an exact coordinate

The intended workflow is:

Possible Spill
      +
Probable Source Zone
      +
Historical Vessel Evidence
      ↓
Candidate Ranking
      ↓
Human Investigation

22 — DEPLOYMENT CONTEXT

Potential institutional users include:

Indian Coast Guard
Maritime authorities
Port authorities
Environmental agencies
Marine response teams

The architecture is modular and can be adapted to different maritime regions by changing the available satellite, environmental and AIS datasets.

23 — FUTURE DEVELOPMENT
Detection
Larger and geographically diverse training datasets
Improved SAR look-alike discrimination
Multi-satellite integration
Source Estimation
Lagrangian particle modelling
Weathering and diffusion modelling
Ensemble environmental scenarios
Improved uncertainty estimation
Vessel Analysis
Larger AIS datasets
Advanced trajectory modelling
Behavioural anomaly detection
Improved candidate scoring
Platform
Cloud deployment
Regional scaling
Automated data ingestion
Advanced geospatial visualization
Historical incident comparison

24 — QUICK START
Clone the repository
git clone <repository-url>
cd SAGAR-DHRISTI
Create the Python environment
python -m venv venv
Activate

Windows:

venv\Scripts\activate

Linux / macOS:

source venv/bin/activate
Install dependencies
pip install -r requirements.txt
Start the backend
uvicorn main:app --reload
Start the frontend
npm install
npm run dev

25 — TEAM
Team Sagar Dhristi
Member	Contribution
Vaishnavi	Research, data, system integration, source tracing and evidence fusion
Keertana	Machine learning, U-Net, backend and FastAPI
Tanvi Gupta	Frontend, interface and data generation
Naman Kumar Sahoo	Deep learning, DeepLabV3+ and trajectory analysis
Jagat Dubey	Business model, government adoption and viability
Nikil	Business strategy, impact and deployment planning

26 — SMART INDIA HACKATHON 2026

Problem Statement: SIH26143
Organisation: NTRO
Category: Software
Theme: Space Technology

27 — REFERENCES
Government and Operational Sources
Press Information Bureau, Government of India. (2025). Parliament Question: Coastline of the Country. PRID 2198800.
International Tanker Owners Pollution Federation (ITOPF). (2026). 2025 Oil Tanker Spill Statistics.
European Maritime Safety Agency (EMSA). How Does SAR Detection Work?
UN-SPIDER. AI Combines Satellite Data to Improve Oil Spill Detection.
Satellite and Environmental Data
Copernicus Data Space Ecosystem. Sentinel-1 Copernicus Sentinel Mission.
Hersbach, H., et al. (2020). ERA5 Hourly Data on Single Levels from 1940 to Present. Copernicus Climate Change Service. DOI: 10.24381/cds.adbb2d47.
NOAA MarineCadastre. Automatic Identification System Vessel Traffic Data.
Oil-Spill Datasets
Trujillo-Acatitla, R., et al. (2024). Sentinel-1 SAR Oil Spill Image Dataset — Part I. Zenodo. DOI: 10.5281/zenodo.8346860.
Trujillo-Acatitla, R., et al. (2024). Sentinel-1 SAR Oil Spill Image Dataset — Part II. Zenodo. DOI: 10.5281/zenodo.8253899.
Trujillo-Acatitla, R., et al. (2024). Sentinel-1 SAR Oil Spill Image Dataset — Part III. Zenodo. DOI: 10.5281/zenodo.13761290.
Blondeau-Patissier, D., et al. (2022). CSIRO Sentinel-1 SAR Image Dataset of Oil- and Non-Oil Features for Machine Learning. DOI: 10.25919/4v55-dn16.
Bakhtiyar2222. Deep-SAR Oil Spill Segmentation Refined. Kaggle.
AI and SAR Detection
Dong, X., et al. (2023). Marine Oil Spill Detection from Low-Quality SAR Remote Sensing Images. Journal of Marine Science and Engineering, 11(8), 1552. DOI: 10.3390/jmse11081552.
Zakzouk, M., Abdulaziz, A. M., Abou El-Magd, I., et al. (2025). Automated Oil Spill Detection Using Deep Learning and SAR Satellite Data for the Northern Entrance of the Suez Canal. Scientific Reports, 15, 20107. DOI: 10.1038/s41598-025-03028-1.
Sugitha, A., et al. (2026). Automatic Identification System-Based Oil Spill Detection. DOI: 10.21203/rs.3.rs-8922220/v1.
S., S. (2025). Maritime Environment Safety: Advanced Oil Spill Detection through AIS and Remote Sensing. IJRASET, 13(4), 3371–3377. DOI: 10.22214/ijraset.2025.68733.
Source Tracing and Vessel Identification
Longépé, N., Mouche, A. A., Goacolou, M., et al. (2015). Polluter Identification with Spaceborne Radar Imagery, AIS and Forward Drift Modeling. Marine Pollution Bulletin, 101(2), 826–833. DOI: 10.1016/j.marpolbul.2015.08.006.
El Mohtar, S., et al. (2021). Bayesian Identification of Oil Spill Source Parameters from Image Contours. Marine Pollution Bulletin, 169, 112514. DOI: 10.1016/j.marpolbul.2021.112514.
Luo, D., et al. (2024). A New Ship Tracing Technology from Oil Spills Based on Multi-Source Data. Marine Pollution Bulletin, 207, 116808. DOI: 10.1016/j.marpolbul.2024.116808.
SAGAR DHRISTI

Find where first. Determine who next.

Satellite Observation
        +
Environmental Dynamics
        +
Vessel Movement
        ↓
Structured Oil-Spill Investigation

Smart India Hackathon 2026 · SIH26143 · NTRO
