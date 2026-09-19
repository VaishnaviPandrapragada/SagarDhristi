import os
import tempfile
from typing import Any, Dict

import pandas as pd
from fastapi import APIRouter, File, Form, UploadFile

from services.unet_service import predict_with_unet
from services.deeplabv3_service import predict_with_deeplab
from services.transunet_service import predict_with_transunet
from services.orchestration_service import orchestrate_predictions

from services.environment_service import EnvironmentalConditions
from services.hindcast_service import HindcastService
from services.source_zone_service import SourceZoneService
from services.source_time_service import SourceTimeService
from services.forward_drift_service import ForwardDriftService
from services.ais_source_matching_service import AISSourceMatchingService
from services.phase_b_evidence_service import PhaseBEvidenceService
from services.alert_service import AlertService


router = APIRouter()


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


AIS_DATASET_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "Guam_AIS_2022_FINAL.parquet",
    )
)


def load_ais_dataset() -> pd.DataFrame:
    if not os.path.exists(AIS_DATASET_PATH):
        raise FileNotFoundError(
            f"AIS dataset not found: {AIS_DATASET_PATH}"
        )

    return pd.read_parquet(AIS_DATASET_PATH)


def _confidence(result: Dict[str, Any]) -> float | None:
    for key in (
        "confidence",
        "model_confidence",
        "score",
        "probability",
    ):
        value = result.get(key)

        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                pass

    return None


def _detected(result: Dict[str, Any]) -> bool | None:
    for key in (
        "oil_spill_detected",
        "spill_detected",
    ):
        if key in result:
            return bool(result[key])

    if "class" in result:
        try:
            return int(result["class"]) == 1
        except (TypeError, ValueError):
            pass

    if "prediction" in result:
        value = result["prediction"]

        if isinstance(value, bool):
            return value

        try:
            return int(value) == 1
        except (TypeError, ValueError):
            pass

    return None


def _serialize_model_result(
    key: str,
    result: Dict[str, Any],
) -> Dict[str, Any]:

    output = {
        "key": key,
        "name": {
            "unet": "U-Net",
            "deeplabv3": "DeepLabV3+",
            "transunet": "TransUNet",
        }[key],
        "confidence": _confidence(result),
        "detected": _detected(result),
        "oil_spill_detected": _detected(result),
        "class": result.get("class"),
        "role": {
            "unet": "Fine-grained segmentation",
            "deeplabv3": "Multi-scale segmentation",
            "transunet": "Global-context segmentation",
        }[key],
    }

    for source_key in (
        "mask_image",
        "maskImage",
        "mask_url",
        "mask_data_url",
    ):
        if result.get(source_key):
            output["mask_image"] = result[source_key]
            break

    for source_key in (
        "area",
        "area_pixels",
        "spill_pixels",
    ):
        if result.get(source_key) is not None:
            output["area"] = result[source_key]
            break

    return output


def _build_orchestrator(
    raw: Dict[str, Any],
    models: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:

    detected_values = [
        models["unet"]["detected"],
        models["deeplabv3"]["detected"],
        models["transunet"]["detected"],
    ]

    valid = [
        value
        for value in detected_values
        if value is not None
    ]

    spill_votes = sum(
        value is True
        for value in valid
    )

    no_spill_votes = sum(
        value is False
        for value in valid
    )

    total_models = len(valid)

    if total_models >= 2 and spill_votes >= 2:
        fallback_verdict = "MAJORITY_SPILL"
        final_detected = True

    elif total_models >= 2 and no_spill_votes >= 2:
        fallback_verdict = "MAJORITY_NO_SPILL"
        final_detected = False

    else:
        fallback_verdict = "MODEL_DISAGREEMENT"
        final_detected = None

    raw_verdict = (
        raw.get("verdict")
        or raw.get("decision")
        or raw.get("status")
    )

    if raw_verdict in (
        "MAJORITY_SPILL",
        "MAJORITY_NO_SPILL",
        "MODEL_DISAGREEMENT",
    ):
        verdict = raw_verdict
    else:
        verdict = fallback_verdict

    if raw.get("spill_detected") is not None:
        final_detected = bool(
            raw["spill_detected"]
        )

    confidence = _confidence(raw)

    if confidence is None:
        confidences = [
            model["confidence"]
            for model in models.values()
            if model["confidence"] is not None
        ]

        confidence = (
            max(confidences)
            if confidences
            else None
        )

    agreement = raw.get(
        "agreement",
        raw.get("model_agreement"),
    )

    if agreement is None and total_models:
        agreement = (
            max(
                spill_votes,
                no_spill_votes,
            )
            / total_models
        )

    iou = raw.get(
        "iou",
        raw.get("mask_iou"),
    )

    return {
        "verdict": verdict,
        "spill_detected": final_detected,
        "total_models": total_models,
        "spill_votes": spill_votes,
        "no_spill_votes": no_spill_votes,
        "confidence": (
            float(confidence)
            if confidence is not None
            else None
        ),
        "agreement": (
            float(agreement)
            if agreement is not None
            else None
        ),
        "iou": (
            float(iou)
            if iou is not None
            else None
        ),
        "decisions": raw.get(
            "decisions",
            [],
        ),
        "rule": raw.get(
            "rule",
            "Three independent model predictions are compared before the investigation continues.",
        ),
    }


@router.post(
    "/analyze",
    summary="Run Complete SAR Investigation",
)
async def analyze_image(
    file: UploadFile = File(...),

    spill_latitude: float = Form(
        DEMO_LATITUDE
    ),
    spill_longitude: float = Form(
        DEMO_LONGITUDE
    ),
    spill_timestamp: str = Form(
        DEMO_TIMESTAMP
    ),

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
        # ==================================================
        # 1. SAVE UPLOADED IMAGE
        # ==================================================

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:

            temp_file.write(
                await file.read()
            )

            temp_path = temp_file.name

        # ==================================================
        # 2. THREE-MODEL VISION LAYER
        # ==================================================

        # U-Net is executed exactly once.
        unet_result = predict_with_unet(
            temp_path
        )

        deeplab_result = predict_with_deeplab(
            temp_path
        )

        transunet_result = predict_with_transunet(
            temp_path
        )

        models = {
            "unet": _serialize_model_result(
                "unet",
                unet_result,
            ),
            "deeplabv3": _serialize_model_result(
                "deeplabv3",
                deeplab_result,
            ),
            "transunet": _serialize_model_result(
                "transunet",
                transunet_result,
            ),
        }

        # ==================================================
        # 3. ORCHESTRATOR
        # ==================================================

        raw_orchestrator = orchestrate_predictions(
            unet_result,
            deeplab_result,
            transunet_result,
        )

        orchestrator = _build_orchestrator(
            raw_orchestrator,
            models,
        )

        spill_detected = (
            orchestrator["spill_detected"]
        )

        # ==================================================
        # 4. AUTHORITATIVE U-NET SEGMENTATION
        # ==================================================

        # The same U-Net result used above is reused here.
        segmentation_result = unet_result

        geometry = segmentation_result.get(
            "geometry",
            {},
        )

        result: Dict[str, Any] = {
            "phase": "A+B",
            "status": "success",

            "spill_detected": spill_detected,

            "vision_models": models,

            "orchestrator": orchestrator,

            "segmentation": {
                "mask_available": bool(
                    segmentation_result.get(
                        "mask_image"
                    )
                ),

                "mask_shape": segmentation_result.get(
                    "mask_shape"
                ),

                "model_confidence": segmentation_result.get(
                    "confidence"
                ),

                "spill_pixels": segmentation_result.get(
                    "spill_pixels",
                    geometry.get(
                        "area_pixels",
                        0,
                    ),
                ),

                "coverage_ratio": segmentation_result.get(
                    "coverage_ratio",
                    geometry.get(
                        "coverage_ratio",
                        0.0,
                    ),
                ),

                "mask_image": segmentation_result.get(
                    "mask_image"
                ),

                "original_image_size": segmentation_result.get(
                    "original_image_size"
                ),

                "model_input_size": segmentation_result.get(
                    "model_input_size"
                ),

                "mask_threshold": 0.5,

                "geometry": geometry,
            },

            "geometry": geometry,

            "spill": {
                "latitude": spill_latitude,
                "longitude": spill_longitude,
                "timestamp": spill_timestamp,
                "geometry": geometry,
            },

            "attribution": {
                "candidate_vessels": [],
            },
        }

        # ==================================================
        # 5. STOP IF NOT A SPILL
        # ==================================================

        if spill_detected is not True:
            return result

        # ==================================================
        # 6. ENVIRONMENT
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

        result["environment"] = (
            environment.to_dict()
        )

        # ==================================================
        # 7. BACKWARD HINDCAST
        # ==================================================

        hindcast_service = HindcastService(
            particle_count=100,
            wind_factor=0.03,
        )

        hindcast = (
            hindcast_service.backward_hindcast(
                spill_latitude=spill_latitude,
                spill_longitude=spill_longitude,
                environment=environment,
                lookback_hours=lookback_hours,
                time_step_hours=time_step_hours,
            )
        )

        result["hindcast"] = hindcast

        # ==================================================
        # 8. PROBABLE SOURCE ZONE
        # ==================================================

        source_zone_service = SourceZoneService(
            containment_percent=90.0
        )

        source_zone = (
            source_zone_service.calculate_source_zone(
                source_particles=hindcast[
                    "source_particles"
                ]
            )
        )

        result["source_zone"] = source_zone

        # ==================================================
        # 9. SOURCE TIME
        # ==================================================

        source_time_service = SourceTimeService()

        source_time = (
            source_time_service.estimate_source_time(
                spill_timestamp,
                lookback_hours,
            )
        )

        result["source_time"] = source_time

        # ==================================================
        # 10. FORWARD DRIFT
        # ==================================================

        source_center = source_zone["center"]

        forward_service = ForwardDriftService(
            particle_count=100,
            wind_factor=0.03,
        )

        forward_prediction = (
            forward_service.forward_drift(
                source_latitude=float(
                    source_center["latitude"]
                ),
                source_longitude=float(
                    source_center["longitude"]
                ),
                environment=environment,
                forecast_hours=forecast_hours,
                time_step_hours=time_step_hours,
            )
        )

        result["forward_prediction"] = (
            forward_prediction
        )

        # ==================================================
        # 11. REAL AIS CORRELATION
        # ==================================================

        ais_dataframe = load_ais_dataset()

        estimated_source_time = source_time[
            "estimated_source_time"
        ]

        ais_service = AISSourceMatchingService(
            time_tolerance_hours=1.0,
            spatial_radius_km=25.0,
        )

        ais_candidates = (
            ais_service.match_vessels(
                dataframe=ais_dataframe,
                source_zone=source_zone,
                estimated_source_time=estimated_source_time,
            )
        )

        # ==================================================
        # 12. EVIDENCE FUSION
        # ==================================================

        evidence_service = PhaseBEvidenceService()

        ranked_candidates = (
            evidence_service.rank_candidates(
                ais_candidates
            )
        )

        result["ais_candidates"] = (
            ais_candidates
        )

        result["ranked_candidates"] = (
            ranked_candidates
        )

        result["attribution"] = {
            "candidate_vessels": ranked_candidates,
        }

        # ==================================================
        # 13. ALERT
        # ==================================================

        top_score = (
            float(
                ranked_candidates[0].get(
                    "evidence_score",
                    0.0,
                )
            )
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

        result["alert"] = alert

        return result

    except Exception as exc:
        return {
            "phase": "A+B",
            "status": "error",
            "error": str(exc),
        }

    finally:
        if (
            temp_path
            and os.path.exists(temp_path)
        ):
            try:
                os.remove(temp_path)
            except OSError:
                pass