import os
import tempfile
from typing import Any, Dict

import pandas as pd
from fastapi import APIRouter, File, Form, UploadFile

from services.segmentation_service import predict_segmentation
from services.spill_geometry_service import calculate_spill_geometry

from services.environment_service import EnvironmentalConditions
from services.hindcast_service import HindcastService
from services.source_zone_service import SourceZoneService
from services.source_time_service import SourceTimeService
from services.forward_drift_service import ForwardDriftService
from services.ais_source_matching_service import AISSourceMatchingService
from services.phase_b_evidence_service import PhaseBEvidenceService
from services.alert_service import AlertService


router = APIRouter()


# ============================================================
# DEMO SCENE
# ============================================================
#
# The PALSAR development images do not contain the geospatial
# metadata required for automatic AIS/environment correlation.
#
# Therefore the demo uses one validated Guam 2022 scene.
#
# These values are DEVELOPMENT/DEMO METADATA and should not be
# presented as metadata extracted from the uploaded PNG.
# ============================================================

DEMO_LATITUDE = 13.46321
DEMO_LONGITUDE = 144.65858
DEMO_TIMESTAMP = "2022-03-04T06:30:27Z"

DEMO_WIND_SPEED_KNOTS = 20.0
DEMO_WIND_DIRECTION_DEG = 90.0

DEMO_CURRENT_SPEED_KNOTS = 1.5
DEMO_CURRENT_DIRECTION_DEG = 90.0

DEMO_LOOKBACK_HOURS = 6.0
DEMO_FORECAST_HOURS = 6.0
DEMO_TIME_STEP_HOURS = 1.0


# ============================================================
# AIS DATASET
# ============================================================

AIS_DATASET_PATH = (
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "Guam_AIS_2022_FINAL.parquet",
        )
    )
)


def load_ais_dataset() -> pd.DataFrame:
    """
    Load the real Guam AIS development dataset.

    The parquet file uses:
        mmsi
        base_date_time
        latitude
        longitude
        sog
        cog
        heading
        ...
    """

    if not os.path.exists(AIS_DATASET_PATH):
        raise FileNotFoundError(
            f"AIS dataset not found: {AIS_DATASET_PATH}"
        )

    return pd.read_parquet(AIS_DATASET_PATH)


# ============================================================
# ANALYZE
# ============================================================

@router.post(
    "/analyze",
    summary="Analyze SAR Scene",
)
async def analyze_image(
    file: UploadFile = File(...),

    # --------------------------------------------------------
    # Optional metadata overrides
    # --------------------------------------------------------
    #
    # Normally the frontend does NOT need to send these.
    # The defaults create a one-click demo.
    #
    spill_latitude: float = Form(DEMO_LATITUDE),
    spill_longitude: float = Form(DEMO_LONGITUDE),
    spill_timestamp: str = Form(DEMO_TIMESTAMP),

    wind_speed_knots: float = Form(
        DEMO_WIND_SPEED_KNOTS
    ),
    wind_direction_deg: float = Form(
        DEMO_WIND_DIRECTION_DEG
    ),

    current_speed_knots: float = Form(
        DEMO_CURRENT_SPEED_KNOTS
    ),
    current_direction_deg: float = Form(
        DEMO_CURRENT_DIRECTION_DEG
    ),

    lookback_hours: float = Form(
        DEMO_LOOKBACK_HOURS
    ),
    forecast_hours: float = Form(
        DEMO_FORECAST_HOURS
    ),
    time_step_hours: float = Form(
        DEMO_TIME_STEP_HOURS
    ),
) -> Dict[str, Any]:

    suffix = os.path.splitext(
        file.filename or ".png"
    )[1]

    temp_path = None

    try:

        # ====================================================
        # 1. SAVE UPLOADED SAR IMAGE
        # ====================================================

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:

            temp_file.write(
                await file.read()
            )

            temp_path = temp_file.name

        # ====================================================
        # 2. SAR SEGMENTATION
        # ====================================================

        segmentation_result = (
            predict_segmentation(temp_path)
        )

        mask = segmentation_result["mask"]

        # ====================================================
        # 3. SPILL GEOMETRY
        # ====================================================

        geometry = (
            calculate_spill_geometry(mask)
        )

        spill_detected = geometry[
            "spill_present"
        ]

        result: Dict[str, Any] = {
            "phase": "A+B",
            "status": "success",

            "spill_detected": spill_detected,

            "segmentation": {
                "mask_available": True,
                "mask_shape": list(
                    mask.shape
                ),
                "model_confidence":
                    segmentation_result[
                        "confidence"
                    ],
            },

            "geometry": geometry,

            "spill": {
                "latitude":
                    spill_latitude,

                "longitude":
                    spill_longitude,

                "timestamp":
                    spill_timestamp,

                "geometry":
                    geometry,
            },

            "attribution": {
                "candidate_vessels": []
            },

            "demo_metadata": {
                "enabled": True,
                "note": (
                    "Development SAR images "
                    "do not contain the geospatial "
                    "metadata required for automatic "
                    "AIS correlation. The demo uses "
                    "a validated Guam 2022 scene."
                ),
            },
        }

        # ====================================================
        # 4. STOP IF NO SPILL
        # ====================================================

        if not spill_detected:

            result["alert"] = {
                "active": False,
                "severity": "NONE",
                "type": "NO_SPILL_DETECTED",
                "title": "No Spill Detected",
                "message": (
                    "The segmentation model did not "
                    "detect a spill region in this scene."
                ),
                "confidence":
                    segmentation_result[
                        "confidence"
                    ],
            }

            return result

        # ====================================================
        # 5. ENVIRONMENT
        # ====================================================

        environment = EnvironmentalConditions(
            latitude=spill_latitude,
            longitude=spill_longitude,
            timestamp=spill_timestamp,

            wind_speed_knots=
                wind_speed_knots,

            wind_direction_deg=
                wind_direction_deg,

            current_speed_knots=
                current_speed_knots,

            current_direction_deg=
                current_direction_deg,
        )

        # ====================================================
        # 6. BACKWARD HINDCAST
        # ====================================================

        hindcast_service = HindcastService(
            particle_count=100,
            wind_factor=0.03,
        )

        hindcast = (
            hindcast_service.backward_hindcast(
                spill_latitude=
                    spill_latitude,

                spill_longitude=
                    spill_longitude,

                environment=
                    environment,

                lookback_hours=
                    lookback_hours,

                time_step_hours=
                    time_step_hours,
            )
        )

        result["environment"] = {
            "latitude":
                spill_latitude,

            "longitude":
                spill_longitude,

            "timestamp":
                spill_timestamp,

            "wind": {
                "speed_knots":
                    wind_speed_knots,

                "direction_deg":
                    wind_direction_deg,
            },

            "ocean_current": {
                "speed_knots":
                    current_speed_knots,

                "direction_deg":
                    current_direction_deg,
            },
        }

        result["hindcast"] = {
            "particle_count":
                hindcast.get(
                    "particle_count",
                    100,
                ),

            "lookback_hours":
                lookback_hours,

            "time_step_hours":
                time_step_hours,

            "drift":
                hindcast.get(
                    "drift",
                    {},
                ),

            "tracks":
                hindcast.get(
                    "tracks",
                    [],
                ),
        }

        # ====================================================
        # 7. SOURCE ZONE
        # ====================================================

        source_zone_service = (
            SourceZoneService(
                containment_percent=90.0
            )
        )

        source_zone = (
            source_zone_service
            .calculate_source_zone(
                hindcast[
                    "source_particles"
                ]
            )
        )

        result["source_zone"] = (
            source_zone
        )

        # ====================================================
        # 8. SOURCE TIME
        # ====================================================

        source_time_service = (
            SourceTimeService()
        )

        source_time = (
            source_time_service
            .estimate_source_time(
                spill_timestamp,
                lookback_hours,
            )
        )

        result["source_time"] = (
            source_time
        )

        # ====================================================
        # 9. FORWARD DRIFT
        # ====================================================

        source_center = (
            source_zone["center"]
        )

        forward_drift_service = (
            ForwardDriftService(
                particle_count=100,
                wind_factor=0.03,
            )
        )

        forward_prediction = (
            forward_drift_service.forward_drift(
                source_latitude=
                    source_center[
                        "latitude"
                    ],

                source_longitude=
                    source_center[
                        "longitude"
                    ],

                environment=
                    environment,

                forecast_hours=
                    forecast_hours,

                time_step_hours=
                    time_step_hours,
            )
        )

        result[
            "forward_prediction"
        ] = forward_prediction

        # ====================================================
        # 10. REAL AIS CORRELATION
        # ====================================================

        ais_dataframe = (
            load_ais_dataset()
        )

        estimated_source_time = (
            source_time[
                "estimated_source_time"
            ]
        )

        ais_service = (
            AISSourceMatchingService(
                time_tolerance_hours=1.0,
                spatial_radius_km=25.0,
            )
        )

        ais_candidates = (
            ais_service.match_vessels(
                dataframe=
                    ais_dataframe,

                source_zone=
                    source_zone,

                estimated_source_time=
                    estimated_source_time,
            )
        )

        result[
            "ais_candidates"
        ] = ais_candidates

        # ====================================================
        # 11. EVIDENCE FUSION
        # ====================================================

        evidence_service = (
            PhaseBEvidenceService()
        )

        ranked_candidates = (
            evidence_service
            .rank_candidates(
                ais_candidates
            )
        )

        result[
            "ranked_candidates"
        ] = ranked_candidates

        # ====================================================
        # 12. ALERT
        # ====================================================

        alert_service = AlertService()

        top_score = 0.0

        if ranked_candidates:

            top_candidate = (
                ranked_candidates[0]
            )

            top_score = float(
                top_candidate.get(
                    "evidence_score",
                    0.0,
                )
            )

        alert = (
            alert_service.create_alert(
                spill_detected=True,
                confidence=top_score,
                timestamp=spill_timestamp,
                latitude=spill_latitude,
                longitude=spill_longitude,
                candidate_vessels=
                    ranked_candidates,
            )
        )

        result["alert"] = alert

        return result

    except Exception as exc:

        return {
            "phase": "A+B",
            "status": "error",
            "error": str(exc),
        }

    finally:

        # ====================================================
        # CLEAN TEMPORARY FILE
        # ====================================================

        if (
            temp_path
            and os.path.exists(temp_path)
        ):
            try:
                os.remove(temp_path)
            except OSError:
                pass