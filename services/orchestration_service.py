import base64
import io

import numpy as np
from PIL import Image


def _geometry(mask):
    mask = np.asarray(mask).astype(bool)

    h, w = mask.shape
    area = int(mask.sum())

    if not area:
        return {
            "spill_present": False,
            "area_pixels": 0,
            "coverage_ratio": 0.0,
            "mask_width": 0,
            "mask_height": 0,
            "bounding_box": None,
            "centroid": None,
        }

    ys, xs = np.where(mask)

    xmin, xmax = int(xs.min()), int(xs.max())
    ymin, ymax = int(ys.min()), int(ys.max())

    return {
        "spill_present": True,
        "area_pixels": area,
        "coverage_ratio": float(mask.mean()),
        "mask_width": xmax - xmin + 1,
        "mask_height": ymax - ymin + 1,
        "bounding_box": {
            "x_min": xmin,
            "y_min": ymin,
            "x_max": xmax,
            "y_max": ymax,
            "width": xmax - xmin + 1,
            "height": ymax - ymin + 1,
        },
        "centroid": {
            "x": float(xs.mean()),
            "y": float(ys.mean()),
        },
    }


def _data_url(mask):
    buffer = io.BytesIO()

    Image.fromarray(
        np.asarray(mask).astype(np.uint8) * 255,
        mode="L",
    ).save(buffer, format="PNG")

    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")

    return "data:image/png;base64," + encoded


def _summary(result):
    raw_confidence = result.get("confidence")

    confidence = (
        float(raw_confidence)
        if raw_confidence is not None
        else None
    )

    return {
        "model": result.get("model"),
        "class": result.get("class"),
        "oil_spill_detected": bool(
            result.get("oil_spill_detected")
        ),
        "confidence": confidence,
        "mask_available": "mask" in result,
        "mask_shape": result.get("mask_shape"),
        "spill_pixels": result.get("spill_pixels"),
        "coverage_ratio": result.get("coverage_ratio"),
        "mask_image": result.get("mask_image"),
        "model_input_size": result.get("model_input_size"),
    }


def orchestrate_predictions(
    unet_result,
    deeplab_result,
    transunet_result,
):
    models = {
        "unet": unet_result,
        "deeplabv3": deeplab_result,
        "transunet": transunet_result,
    }

    votes = [
        bool(result["oil_spill_detected"])
        for result in models.values()
    ]

    spill_votes = sum(votes)

    if spill_votes >= 2:
        detected = True
        decision = "MAJORITY_SPILL"

    elif spill_votes == 0:
        detected = False
        decision = "MAJORITY_NO_SPILL"

    else:
        detected = False
        decision = "MODEL_DISAGREEMENT"

    masks = [
        np.asarray(result["mask"], dtype=np.float32)
        for result in models.values()
        if "mask" in result
    ]

    fused_mask = None
    fused_image = None
    geometry = None

    if masks:
        h, w = masks[0].shape
        resized_masks = []

        for mask in masks:
            if mask.shape != (h, w):
                mask = (
                    np.asarray(
                        Image.fromarray(
                            (mask * 255).astype(np.uint8)
                        ).resize(
                            (w, h),
                            Image.Resampling.NEAREST,
                        )
                    )
                    .astype(np.float32)
                    / 255.0
                )

            resized_masks.append(mask)

        consensus = np.mean(resized_masks, axis=0)

        fused_mask = consensus >= (2 / 3)

        geometry = _geometry(fused_mask)

        fused_image = _data_url(fused_mask)

        fused_confidence = float(
            np.maximum(
                consensus,
                1 - consensus,
            ).mean()
        )

    else:
        geometry = _geometry(
            np.zeros((128, 128), dtype=bool)
        )

        fused_confidence = 0.0

    model_confidences = {}

    for name, result in models.items():
        confidence = result.get("confidence")

        if confidence is None:
            model_confidences[name] = None
        else:
            model_confidences[name] = float(confidence)

    return {
        "spill_detected": detected,
        "confidence": fused_confidence,
        "decision": decision,

        "models": {
            "unet": _summary(unet_result),
            "deeplabv3": _summary(deeplab_result),
            "transunet": _summary(transunet_result),
        },

        "evidence": {
            "total_models": 3,
            "spill_votes": spill_votes,
            "no_spill_votes": 3 - spill_votes,
            "model_confidences": model_confidences,
        },

        "spill": {
            "mask_available": fused_image is not None,
            "geometry_available": True,
            "mask_image": fused_image,
            "mask_shape": (
                list(fused_mask.shape)
                if fused_mask is not None
                else None
            ),
            "geometry": geometry,
        },
    }