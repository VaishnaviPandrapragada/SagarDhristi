from datetime import datetime, timezone
import os
import tempfile
import pandas as pd
from fastapi import APIRouter, UploadFile, File, Form
from backend.schemas.analysis import AnalyzeResponse
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


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_image(
    file: UploadFile = File(...),

    # Prototype scene metadata.
    # In production, these should come from SAR scene metadata.
    spill_latitude: float = Form(-19.673594),
    spill_longitude: float = Form(115.564515),
    spill_timestamp: str = Form("2021-06-15T03:20:00Z"),

    wind_speed_knots: float = Form(20.0),
    wind_direction_deg: float = Form(90.0),

    current_speed_knots: float = Form(1.5),
    current_direction_deg: float = Form(90.0),

    lookback_hours: float = Form(6.0),
    forecast_hours: float = Form(6.0),
    time_step_hours: float = Form(1.0),
):

    suffix = os.path.splitext(file.filename)[1]

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp_file:

        temp_file.write(await file.read())
        temp_path = temp_file.name

    try:

        # ==================================================
        # 1. SAR SEGMENTATION
        # ==================================================

        segmentation_result = predict_segmentation(temp_path)

        mask = segmentation_result["mask"]

        # ==================================================
        # 2. SPILL GEOMETRY
        # ==================================================

        geometry = calculate_spill_geometry(mask)

        spill_detected = geometry["spill_present"]

        # ==================================================
        # 3. BASE RESPONSE
        # ==================================================

        result = {
            "spill_detected": spill_detected,

            "segmentation": {
                "mask_available": True,
                "mask_shape": list(mask.shape),
                "model_confidence": segmentation_result["confidence"],
            },

            "geometry": geometry,

            "attribution": {
                "candidate_vessels": []
            }
        }

        # ==================================================
        # 4. STOP IF NO SPILL
        # ==================================================

        if not spill_detected:
            return result

        # ==================================================
        # 5. PHASE B ENVIRONMENT
        # ==================================================

        environment = EnvironmentalConditions(
            latitude=spill_latitude,
            longitude=spill_longitude,
            timestamp=spill_timestamp,

            wind_speed_knots=wind_speed_knots,
            wind_direction_deg=wind_direction_deg,

            current_speed_knots=current_speed_knots,
            current_direction_deg=current_direction_deg,
        )

        # ==================================================
        # 6. BACKWARD HINDCAST
        # ==================================================

        hindcast_service = HindcastService(
            particle_count=100,
            wind_factor=0.03
        )

        hindcast = hindcast_service.backward_hindcast(
            spill_latitude=spill_latitude,
            spill_longitude=spill_longitude,
            environment=environment,
            lookback_hours=lookback_hours,
            time_step_hours=time_step_hours,
        )

        # ==================================================
        # 7. SOURCE ZONE
        # ==================================================

        source_zone_service = SourceZoneService(
            containment_percent=90.0
        )

        source_zone = source_zone_service.calculate_source_zone(
            hindcast["source_particles"]
        )

        # ==================================================
        # 8. SOURCE TIME
        # ==================================================

        source_time_service = SourceTimeService()

        source_time = source_time_service.estimate_source_time(
            spill_timestamp,
            lookback_hours
        )

        # ==================================================
        # 9. FORWARD DRIFT
        # ==================================================

        source_center = {
            "latitude": source_zone["center"]["latitude"],
            "longitude": source_zone["center"]["longitude"],
        }

        forward_drift_service = ForwardDriftService(
            particle_count=100,
            wind_factor=0.03
        )

        forward_prediction = forward_drift_service.forward_drift(
            source_latitude=source_center["latitude"],
            source_longitude=source_center["longitude"],
            environment=environment,
            forecast_hours=forecast_hours,
            time_step_hours=time_step_hours,)

        # ==================================================
        # 10. AIS CORRELATION
        # ==================================================

        source_time_value = source_time["estimated_source_time"]

        ais_records = [
            {
                "MMSI": "SIM030012",
                "LAT": -19.719000,
                "LON": 115.387000,
                "BaseDateTime": source_time_value
            },
            {
                "MMSI": "SIM030013",
                "LAT": -19.720000,
                "LON": 115.388000,
                "BaseDateTime": source_time_value
            },
        ]

        ais_service = AISSourceMatchingService()

        ais_dataframe = pd.DataFrame(ais_records)

        ais_candidates = ais_service.match_vessels(
            dataframe=ais_dataframe,
            source_zone=source_zone,
            estimated_source_time=source_time_value,
        )

        # ==================================================
        # 11. EVIDENCE FUSION
        # ==================================================

        evidence_service = PhaseBEvidenceService()

        ranked_candidates = evidence_service.rank_candidates(
            ais_candidates
        )

        # ==================================================
        # 12. ALERT
        # ==================================================

        top_score = (
            ranked_candidates[0].get("evidence_score", 0.0)
            if ranked_candidates
            else 0.0
        )

        alert_service = AlertService()

        alert = alert_service.create_alert(
            spill_detected=True,
            confidence=top_score,
            latitude=spill_latitude,
            longitude=spill_longitude,
            timestamp=spill_timestamp,
            ranked_candidates=ranked_candidates,
        )

        # ==================================================
        # 13. FINAL RESPONSE
        # ==================================================

        result.update({
            "phase": "A+B",
            "status": "success",

            "spill": {
                "latitude": spill_latitude,
                "longitude": spill_longitude,
                "timestamp": spill_timestamp,
                "geometry": geometry,
            },

            "environment": environment.to_dict(),

            "hindcast": hindcast,

            "source_zone": source_zone,

            "source_time": source_time,

            "forward_prediction": forward_prediction,

            "ais_candidates": ais_candidates,

            "ranked_candidates": ranked_candidates,

            "alert": alert,

            "prototype_note": (
                "SAR geolocation and timestamp are supplied as prototype "
                "scene metadata because the PNG dataset does not contain "
                "geospatial metadata."
            ),
        })

        return result

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)