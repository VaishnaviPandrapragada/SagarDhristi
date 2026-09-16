from typing import Any, Dict

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.real_environment_service import RealEnvironmentService
from services.hindcast_service import HindcastService
from services.source_zone_service import SourceZoneService
from services.source_time_service import SourceTimeService
from services.forward_drift_service import ForwardDriftService
from services.ais_source_matching_service import AISSourceMatchingService
from services.phase_b_evidence_service import PhaseBEvidenceService
from services.alert_service import AlertService


router = APIRouter(
    tags=["Investigation"],
)


# ---------------------------------------------------------------------------
# Dataset paths
# ---------------------------------------------------------------------------

ERA5_DATASET_PATH = "era5_guam_2022_test.nc"
GLORYS_DATASET_PATH = "data/ocean_currents/glorys_guam_2022_test.nc"
AIS_DATASET_PATH = "Guam_AIS_2022_FINAL.parquet"


# ---------------------------------------------------------------------------
# Request schema
# ---------------------------------------------------------------------------

class InvestigationRequest(BaseModel):
    spill_latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
    )

    spill_longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
    )

    spill_timestamp: str

    wind_speed_knots: float = Field(
        default=20.0,
        ge=0.0,
    )

    wind_direction_deg: float = Field(
        default=90.0,
        ge=0.0,
        lt=360.0,
    )

    current_speed_knots: float = Field(
        default=1.5,
        ge=0.0,
    )

    current_direction_deg: float = Field(
        default=90.0,
        ge=0.0,
        lt=360.0,
    )

    lookback_hours: float = Field(
        default=6.0,
        gt=0.0,
    )

    forecast_hours: float = Field(
        default=6.0,
        gt=0.0,
    )

    time_step_hours: float = Field(
        default=1.0,
        gt=0.0,
    )


# ---------------------------------------------------------------------------
# Phase-B analytical pipeline
# ---------------------------------------------------------------------------

@router.post(
    "/investigate",
    summary="Run Maritime Investigation",
    description=(
        "Runs the complete maritime investigation pipeline: "
        "real environmental analysis, backward hindcast, source-zone "
        "estimation, source-time estimation, forward drift prediction, "
        "real AIS correlation, evidence fusion, and alert generation."
    ),
)
def run_investigation(
    request: InvestigationRequest,
) -> Dict[str, Any]:
    """
    Run the complete maritime investigation pipeline.

    Investigation pipeline:
        Real ERA5 + GLORYS
        -> Environmental Conditions
        -> Backward Hindcast
        -> Source Zone
        -> Source Time
        -> Forward Drift
        -> Real AIS Matching
        -> Evidence Fusion
        -> Alert
    """

    try:
        # ---------------------------------------------------------------
        # 1. Real environmental data
        # ---------------------------------------------------------------

        environment_service = RealEnvironmentService(
            era5_dataset_path=ERA5_DATASET_PATH,
            glorys_dataset_path=GLORYS_DATASET_PATH,
        )

        environment = environment_service.get_environment(
            latitude=request.spill_latitude,
            longitude=request.spill_longitude,
            timestamp=request.spill_timestamp,
        )

        # ---------------------------------------------------------------
        # 2. Backward hindcast
        # ---------------------------------------------------------------

        hindcast_service = HindcastService(
            particle_count=100,
            wind_factor=0.03,
        )

        hindcast_result = hindcast_service.backward_hindcast(
            spill_latitude=request.spill_latitude,
            spill_longitude=request.spill_longitude,
            environment=environment,
            lookback_hours=request.lookback_hours,
            time_step_hours=request.time_step_hours,
        )

        source_particles = hindcast_result["source_particles"]

        # ---------------------------------------------------------------
        # 3. Probable source zone
        # ---------------------------------------------------------------

        source_zone_service = SourceZoneService(
            containment_percent=90.0,
        )

        source_zone = source_zone_service.calculate_source_zone(
            source_particles=source_particles,
        )

        # ---------------------------------------------------------------
        # 4. Source-time estimation
        # ---------------------------------------------------------------

        source_time_service = SourceTimeService()

        source_time = source_time_service.estimate_source_time(
            spill_timestamp=request.spill_timestamp,
            lookback_hours=request.lookback_hours,
        )

        source_time_value = source_time["estimated_source_time"]

        # ---------------------------------------------------------------
        # 5. Forward drift prediction
        # ---------------------------------------------------------------

        source_center = source_zone["center"]

        forward_service = ForwardDriftService(
            particle_count=100,
            wind_factor=0.03,
        )

        forward_result = forward_service.forward_drift(
            source_latitude=source_center["latitude"],
            source_longitude=source_center["longitude"],
            environment=environment,
            forecast_hours=request.forecast_hours,
            time_step_hours=request.time_step_hours,
        )

        # ---------------------------------------------------------------
        # 6. Real AIS source matching
        # ---------------------------------------------------------------

        ais_dataframe = pd.read_parquet(
            AIS_DATASET_PATH,
            columns=[
                "mmsi",
                "base_date_time",
                "latitude",
                "longitude",
            ],
        )

        ais_dataframe["base_date_time"] = pd.to_datetime(
            ais_dataframe["base_date_time"],
            utc=True,
            errors="coerce",
        )

        source_time_timestamp = pd.to_datetime(
            source_time_value,
            utc=True,
        )

        time_tolerance = pd.Timedelta(hours=1.0)

        start_time = source_time_timestamp - time_tolerance
        end_time = source_time_timestamp + time_tolerance

        ais_dataframe = ais_dataframe[
            (ais_dataframe["base_date_time"] >= start_time)
            & (ais_dataframe["base_date_time"] <= end_time)
        ].copy()

        ais_service = AISSourceMatchingService(
            time_tolerance_hours=1.0,
        )

        ais_candidates = ais_service.match_vessels(
            dataframe=ais_dataframe,
            source_zone=source_zone,
            estimated_source_time=source_time_value,
        )

        # ---------------------------------------------------------------
        # 7. Evidence fusion
        # ---------------------------------------------------------------

        evidence_service = PhaseBEvidenceService()

        ranked_candidates = evidence_service.rank_candidates(
            ais_candidates
        )

        # ---------------------------------------------------------------
        # 8. Alert generation
        # ---------------------------------------------------------------

        alert_service = AlertService()

        top_score = (
            ranked_candidates[0]["evidence_score"]
            if ranked_candidates
            else 0.0
        )

        alert = alert_service.create_alert(
            spill_detected=True,
            confidence=top_score,
            latitude=request.spill_latitude,
            longitude=request.spill_longitude,
            timestamp=request.spill_timestamp,
            ranked_candidates=ranked_candidates,
        )

        # ---------------------------------------------------------------
        # 9. Final response
        # ---------------------------------------------------------------

        return {
            "phase": "Investigation",
            "status": "success",
            "spill": {
                "latitude": request.spill_latitude,
                "longitude": request.spill_longitude,
                "timestamp": request.spill_timestamp,
            },
            "environment": environment.to_dict(),
            "hindcast": {
                "particle_count": hindcast_result["particle_count"],
                "lookback_hours": request.lookback_hours,
                "time_step_hours": request.time_step_hours,
                "drift": hindcast_result["drift"],
            },
            "source_zone": source_zone,
            "source_time": source_time,
            "forward_prediction": forward_result,
            "ais_candidates": ranked_candidates,
            "alert": alert,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc