from services.segmentation_service import predict_segmentation


def predict_with_unet(image_path):
    result = predict_segmentation(image_path)

    spill_detected = bool(
        result["geometry"]["spill_present"]
    )

    return {
        "model": "U-Net",

        "class": 1 if spill_detected else 0,

        "oil_spill_detected": spill_detected,

        "confidence": result["model_confidence"],

        "mask": result["mask"],

        "mask_shape": result["mask_shape"],

        "spill_pixels": result["spill_pixels"],

        "coverage_ratio": result["coverage_ratio"],

        "mask_image": result["mask_image"],

        "original_image_size": result[
            "original_image_size"
        ],

        "model_input_size": result[
            "model_input_size"
        ],

        "geometry": result["geometry"],
    }