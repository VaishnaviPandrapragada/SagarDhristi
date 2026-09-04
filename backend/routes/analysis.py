from fastapi import APIRouter, UploadFile, File

import tempfile
import os

from services.unet_service import predict_with_unet
from services.deeplabv3_service import predict_with_deeplab
from services.transunet_service import predict_with_transunet

from services.orchestration_service import orchestrate_predictions


router = APIRouter()


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
        # Run all three models
        # --------------------------------------------------

        unet_result = predict_with_unet(
            temp_path
        )

        deeplab_result = predict_with_deeplab(
            temp_path
        )

        transunet_result = predict_with_transunet(
            temp_path
        )

        # --------------------------------------------------
        # Orchestrate predictions
        # --------------------------------------------------

        final_result = orchestrate_predictions(
            unet_result,
            deeplab_result,
            transunet_result
        )

        return final_result

    finally:

        # --------------------------------------------------
        # Delete temporary image
        # --------------------------------------------------

        if os.path.exists(temp_path):
            os.remove(temp_path)