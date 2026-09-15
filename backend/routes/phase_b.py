from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.environment_service import EnvironmentalConditions
from services.hindcast_service import HindcastService
from services.source_zone_service import SourceZoneService
from services.source_time_service import SourceTimeService
from services.forward_drift_service import ForwardDriftService
from services.ais_source_matching_service import AISSourceMatchingService
from services.phase_b_evidence_service import PhaseBEvidenceService
from services.alert_service import AlertService


router = APIRouter(
    prefix="/phase-b",
    tags=["Phase B - Hindcast & Source Estimation"],
)


class PhaseBRequest(BaseModel):
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
        ...,
        ge=0.0,
    )

    wind_direction_deg: float = Field(
        ...,
        ge=0.0,
        lt=360.0,
    )

    current_speed_knots: float = Field(
        ...,
        ge=0.0,
    )

    current_direction_deg: float = Field(
        ...,
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


@router.post("/analyze")
def analyze_phase_b(request: PhaseBRequest) -> Dict[str, Any]:
    """
    Run the complete Phase-B analytical pipeline.

    Phase B:
        Environment
        -> Backward Hindcast
        -> Source Zone
        -> Source Time
        -> Forward Drift
        -> AIS matching
        -> Evidence Fusion
        -> Alert
    """

    try:
        # --------------------------------------------------
        # 1. Environmental conditions
        # --------------------------------------------------

        environment = EnvironmentalConditions(
            latitude=request.spill_latitude,
            longitude=request.spill_longitude,
            timestamp=request.spill_timestamp,
            wind_speed_knots=request.wind_speed_knots,
            wind_direction_deg=request.wind_direction_deg,
            current_speed_knots=request.current_speed_knots,
            current_direction_deg=request.current_direction_deg,
        )

        # --------------------------------------------------
        # 2. Backward hindcast
        # --------------------------------------------------

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

        source_particles = (
            hindcast_result["source_particles"]
        )

        # --------------------------------------------------
        # 3. Probable source zone
        # --------------------------------------------------

        source_zone_service = SourceZoneService(
            containment_percent=90.0
        )

        source_zone = (
            source_zone_service.calculate_source_zone(
                source_particles=source_particles
            )
        )

        # --------------------------------------------------
        # 4. Source-time estimation
        # --------------------------------------------------

        source_time_service = SourceTimeService()

        source_time = (
            source_time_service.estimate_source_time(
                spill_timestamp=request.spill_timestamp,
                lookback_hours=request.lookback_hours,
            )
        )

        # --------------------------------------------------
        # 5. Forward drift prediction
        # --------------------------------------------------

        source_center = source_zone["center"]

        forward_service = ForwardDriftService(
            particle_count=100,
            wind_factor=0.03,
        )

        forward_result = forward_service.forward_drift(
            source_latitude=float(
                source_center["latitude"]
            ),
            source_longitude=float(
                source_center["longitude"]
            ),
            environment=environment,
            forecast_hours=request.forecast_hours,
            time_step_hours=request.time_step_hours,
        )

        # --------------------------------------------------
        # 6. AIS matching
        #
        # For the API integration test we use deterministic
        # AIS records. The production path can replace this
        # dataframe with the actual Phase-A AIS dataset.
        # --------------------------------------------------

        import pandas as pd

        source_time_value = source_time[
            "estimated_source_time"
        ]

        test_ais = pd.DataFrame(
            [
                {
                    "MMSI": "SIM030012",
                    "LAT": -19.719000,
                    "LON": 115.387000,
                    "BaseDateTime": source_time_value,
                },
                {
                    "MMSI": "SIM030013",
                    "LAT": -19.720000,
                    "LON": 115.388000,
                    "BaseDateTime": source_time_value,
                },
            ]
        )

        ais_service = AISSourceMatchingService(
            time_tolerance_hours=1.0
        )

        ais_candidates = ais_service.match_vessels(
            dataframe=test_ais,
            source_zone=source_zone,
            estimated_source_time=source_time_value,
        )

        # --------------------------------------------------
        # 7. Evidence fusion
        # --------------------------------------------------

        evidence_service = PhaseBEvidenceService()

        ranked_candidates = (
            evidence_service.rank_candidates(
                ais_candidates
            )
        )

        # --------------------------------------------------
        # 8. Backend alert
        # --------------------------------------------------

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

        # --------------------------------------------------
        # 9. Complete response
        # --------------------------------------------------

        return {
            "phase": "B",
            "status": "success",

            "spill": {
                "latitude": request.spill_latitude,
                "longitude": request.spill_longitude,
                "timestamp": request.spill_timestamp,
            },

            "environment": environment.to_dict(),

            "hindcast": {
                "particle_count": hindcast_result[
                    "particle_count"
                ],
                "lookback_hours": hindcast_result[
                    "lookback_hours"
                ],
                "time_step_hours": hindcast_result[
                    "time_step_hours"
                ],
                "drift": hindcast_result["drift"],
            },

            "source_zone": source_zone,

            "source_time": source_time,

            "forward_prediction": {
                "particle_count": forward_result[
                    "particle_count"
                ],
                "forecast_hours": forward_result[
                    "forecast_hours"
                ],
                "time_step_hours": forward_result[
                    "time_step_hours"
                ],
                "drift": forward_result["drift"],
            },

            "ais_candidates": ranked_candidates,

            "alert": alert,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc