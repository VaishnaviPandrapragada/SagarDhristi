def orchestrate_predictions(
    unet_result,
    deeplab_result,
    transunet_result
):
    # --------------------------------------------------
    # Extract model predictions
    # --------------------------------------------------

    unet_spill = unet_result["oil_spill_detected"]

    deeplab_spill = deeplab_result["oil_spill_detected"]
    deeplab_confidence = deeplab_result.get("confidence", 0.5)

    transunet_spill = transunet_result["oil_spill_detected"]
    transunet_confidence = transunet_result.get("confidence", 0.5)

    # --------------------------------------------------
    # Model voting
    # --------------------------------------------------

    votes = [
        unet_spill,
        deeplab_spill,
        transunet_spill
    ]

    spill_count = sum(votes)

    # --------------------------------------------------
    # Decision logic
    # --------------------------------------------------

    if spill_count >= 2:
        spill_detected = True
        decision = "MAJORITY_SPILL"

    elif spill_count == 0:
        spill_detected = False
        decision = "MAJORITY_NO_SPILL"

    else:
        # 1 out of 3 models detected spill
        spill_detected = False
        decision = "MODEL_DISAGREEMENT"

    # --------------------------------------------------
    # Confidence
    # --------------------------------------------------

    confidence = max(
        deeplab_confidence,
        transunet_confidence
    )

    # --------------------------------------------------
    # Final response
    # --------------------------------------------------

    return {
        "spill_detected": spill_detected,
        "confidence": confidence,
        "decision": decision,

        "models": {
            "unet": unet_result,
            "deeplabv3": deeplab_result,
            "transunet": transunet_result
        },

        "evidence": {
            "total_models": 3,
            "spill_votes": spill_count,
            "no_spill_votes": 3 - spill_count
        },

        "spill": {
            "mask_available": False,
            "geometry_available": False
        }
    }