from services.segmentation_service import (
    predict_segmentation
)

from services.spill_geometry_service import (
    calculate_spill_geometry
)


def analyze_spill_image(image_path):

    segmentation = predict_segmentation(
        image_path
    )

    mask = segmentation["mask"]

    geometry = calculate_spill_geometry(
        mask
    )

    if not geometry["spill_present"]:

        return {
            "spill_detected": False,
            "confidence": 0.0,
            "mask_available": True,
            "geometry_available": True,
            "geometry": geometry
        }

    return {
        "spill_detected": True,

        "confidence": round(
            segmentation["confidence"],
            4
        ),

        "mask_available": True,

        "geometry_available": True,

        "geometry": geometry
    }