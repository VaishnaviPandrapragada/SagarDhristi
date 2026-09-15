from fastapi import APIRouter, UploadFile, File

import tempfile
import os
from datetime import datetime, timezone

from services.unet_service import predict_with_unet
from services.deeplabv3_service import predict_with_deeplab
from services.transunet_service import predict_with_transunet

from services.orchestration_service import orchestrate_predictions
from services.backtracking_service import BacktrackingService


router = APIRouter()

# Initialize once when the API starts
backtracking_service = BacktrackingService()


@router.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):

    # --------------------------------------------------
    # Save uploaded image temporarily
    # --------------------------------------------------

    suffix = os.path.splitext(file.filename)[1]

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp_file:

        temp_file.write(await file.read())

        temp_path = temp_file.name

    try:

        # --------------------------------------------------
        # Run all three vision models
        # --------------------------------------------------

        unet_result = predict_with_unet(temp_path)

        deeplab_result = predict_with_deeplab(temp_path)

        transunet_result = predict_with_transunet(temp_path)

        # --------------------------------------------------
        # Orchestrate predictions
        # --------------------------------------------------

        final_result = orchestrate_predictions(
            unet_result,
            deeplab_result,
            transunet_result
        )

        # --------------------------------------------------
        # Attribution pipeline
        # --------------------------------------------------
        #
        # Only run vessel attribution when a spill is detected.
        #
        # Current prototype uses a development AIS event
        # because the image pipeline does not yet provide
        # source coordinates / event timestamp.
        # --------------------------------------------------

        if final_result.get("spill_detected"):

            spill_latitude = -19.673594
            spill_longitude = 115.564515

            event_time = datetime(
                2021,
                6,
                15,
                3,
                20,
                tzinfo=timezone.utc
            )

            vessel_results = backtracking_service.rank_vessels(
                spill_latitude=spill_latitude,
                spill_longitude=spill_longitude,
                event_time=event_time,
                radius_km=50.0,
                lookback_hours=3.0
            )

            final_result["attribution"] = {
                "source_coordinates": {
                    "latitude": spill_latitude,
                    "longitude": spill_longitude
                },
                "event_time": event_time.isoformat(),
                "candidate_vessels": vessel_results
            }

        else:

            final_result["attribution"] = {
                "candidate_vessels": []
            }

        return final_result

    finally:

        # --------------------------------------------------
        # Delete temporary image
        # --------------------------------------------------

        if os.path.exists(temp_path):
            os.remove(temp_path)